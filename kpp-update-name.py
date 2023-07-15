#!/usr/bin/env python3

# Copyright (C) 2023 Freya Lupen <penguinflyer2222@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import zlib
import xml.etree.ElementTree as ET
import os.path
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".kpp file path",
                        type=str)
    parser.add_argument("brush_name", help="new brush name",
                        type=str, nargs='?')
    args = parser.parse_args()

    path = args.file_path
    new_name = args.brush_name

    with open(path, 'r+b') as f:
        PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
        if f.read(8) != PNG_MAGIC:
            print("Not a .png file!")
            return

        found_preset_data = False
        while buf := f.read(4):
            chunk_data_len = int.from_bytes(buf, 'big')
            chunk_id = f.read(4)

            if chunk_id == b'zTXt' or chunk_id == b'iTXt':
                found_preset_data = True
                chunk_pos = f.seek(0, 1) - 8
                # Read the rest of file
                f.seek(chunk_data_len + 4, 1)
                buf = f.read()
                # And seek back
                f.seek(chunk_pos + 8)
                modify_metadata(f, chunk_pos, chunk_data_len, chunk_id,
                                buf, new_name, path)
                break

            # Seek to next chunk at current position + data + CRC
            f.seek(chunk_data_len + 4, 1)

        if not found_preset_data:
            print("Found no preset metadata chunk.")

def modify_metadata(f, chunk_pos, data_length, chunk_type,
                    rest_of_file, new_name, path):
    head_expected = b''
    if chunk_type == b'zTXt':
        head_expected = b'preset\0\0'
    elif chunk_type == b'iTXt':
        head_expected = b'preset\0\1\0UTF-8\0preset\0'

    head = f.read(len(head_expected))
    if head != head_expected:
        print("Not a preset")
        return

    compressed_text = f.read(data_length - len(head_expected))
    text = zlib.decompress(compressed_text)

    root = ET.fromstring(text)
    if root.tag != "Preset":
        print("No Preset tag")
        return
    old_name = root.get("name")
    if old_name == None:
        print("Preset has no name")
        return

    if not new_name:
        filename = os.path.basename(path)
        filename, _ext = os.path.splitext(filename)
        new_name = filename.replace('_', ' ')

    # Use a regex to replace the name directly in text, because I was unable
    # to produce a properly formatted XML string with ET.tostring(root)...
    pat = b'<Preset (.*?)name=\"%s\"(.*?)>' % re.escape(old_name.encode())
    def replfunc(m):
        return b'<Preset %sname=\"%s\"%s>' % \
                  (m.group(1), new_name.encode(), m.group(2))
    new_text = re.sub(pat, replfunc, text, count=1)

    print("Changed name: \"%s\" -> \"%s\"" % (old_name, new_name))

    new_compressed_text = zlib.compress(new_text)

    new_data_length = len(head_expected) + len(new_compressed_text)

    f.seek((chunk_pos + 8 + len(head_expected)), 0)
    # Cut off the rest of the file and write the new text.
    f.truncate()
    f.write(new_compressed_text)

    chksum = zlib.crc32(chunk_type + head_expected + new_compressed_text)
    # Write the CRC after the data we just wrote.
    f.write(chksum.to_bytes(4, 'big'))
    
    f.write(rest_of_file)

    f.seek(chunk_pos, 0)
    f.write(new_data_length.to_bytes(4, 'big'))

if __name__ == "__main__":
    main()
