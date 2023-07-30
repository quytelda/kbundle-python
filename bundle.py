# Copyright 2023 Quytelda Kahja
#
# This file is part of kbundle.
#
# kbundle is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kbundle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kbundle. If not, see <https://www.gnu.org/licenses/>.

import hashlib
import sys
import os.path
import zipfile as Zip
import zlib
import manifest

BUNDLE_MIMETYPE = b'application/x-krita-resourcebundle'
RESOURCE_DIR_NAMES = ["brushes",
                      "gamutmasks",
                      "gradients",
                      "paintoppresets",
                      "palettes",
                      "patterns",
                      "seexpr_scripts",
                      "workspaces"]

def parent_dir_name(path):
    parent_dir_path = os.path.dirname(path)
    return os.path.basename(parent_dir_path)

def md5sum(path):
    alg = hashlib.md5()
    with open(path, "rb") as file:
        alg.update(file.read())

    return alg.hexdigest()

# Zip Compression Options
# https://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part3.html
ZIP_OPTIONS = {
    "allowZip64"    : False,
    "compression"   : Zip.ZIP_DEFLATED,
    "compresslevel" : zlib.Z_DEFAULT_COMPRESSION
}

class Bundle:
    def __init__(self, path):
        self.root = path
        manifest_path = self.__external_path(manifest.MANIFEST_PATH)
        self.manifest = manifest.Manifest(manifest_path)
        self.resources = []

    def load(self):
        if self.manifest.exists() and not self.manifest.load():
            print("Failed to load manifest file.", file=sys.stderr)
            return False

        if not self.scan_files():
            print("Failed to scan bundle directory.", file=sys.stderr)
            return False

        return True

    def scan_files(self):
        if not os.path.isdir(self.root):
            print("Bundle directory does not exist: {}".format(self.root), file=sys.stderr)
            return False

        self.resources.clear()

        for dirname in RESOURCE_DIR_NAMES:
            dirpath = self.__external_path(dirname)
            if not os.path.isdir(dirpath):
                continue

            for filename in os.listdir(dirpath):
                ipath = os.path.join(dirname, filename)
                self.resources.append(ipath)

        return True

    def update_manifest(self):
        if not self.resources:
            return False

        common, mf_only, file_only = self.manifest.compare_entries(self.resources)

        # Remove resources that exist in the manifest but not on disk
        for ipath in mf_only:
            if not self.__remove_entry(ipath, info="REMOVE"):
                return False

        for ipath in file_only:
            if not self.__insert_entry(ipath, info="INSERT"):
                return False

        for ipath in common:
            if not self.__insert_entry(ipath, info="UPDATE"):
                return False

        self.manifest.save()
        return True

    def add_tag(self, path, tag):
        ipath = self.__internal_path(path)
        if not self.manifest.add_tag(ipath, tag):
            print("Failed to add tag for resource: {}".format(ipath), file=sys.stderr)
            return False

        self.manifest.save()
        return True

    def remove_tag(self, path, tag):
        ipath = self.__internal_path(path)
        if not self.manifest.remove_tag(ipath, tag):
            print("Failed to remove tag for resource: {}".format(ipath), file=sys.stderr)
            return False

        self.manifest.save()
        return True

    def unpack(self, archive_path):
        with Zip.ZipFile(archive_path, mode='r', **ZIP_OPTIONS) as zip:
            zip.extractall(path=self.root)

        # Remove the extraneous "mimetype" file. The file is
        # automatically inserted into bundle archives, so storing it
        # is unecessary.
        os.remove(self.__external_path("mimetype"))

    def pack(self, archive_path):
        with Zip.ZipFile(archive_path, mode='w', **ZIP_OPTIONS) as zip:

            def zip_add_file(ipath):
                xpath = self.__external_path(ipath)
                zip.write(xpath, arcname=ipath)

            # The mimetype file must be the first entry in the
            # archive. It must contain only the ASCII-encoded
            # mime-type string and be uncompressed.
            zip.writestr("mimetype", BUNDLE_MIMETYPE,
                         compress_type=Zip.ZIP_STORED,
                         compresslevel=zlib.Z_NO_COMPRESSION)

            for ipath in self.resources:
                zip_add_file(ipath)

            zip_add_file("preview.png")
            zip_add_file(manifest.MANIFEST_PATH)
            zip_add_file("meta.xml")

        return True

    def __external_path(self, ipath):
        return os.path.join(self.root, ipath)

    def __internal_path(self, path):
        # Check whether the given path refers to a location inside the
        # bundle tree. If not, assume the path is relative to the
        # bundle root instead of the current directory (i.e. the path
        # is already internal).
        abs_root = os.path.abspath(self.root)
        abs_path = os.path.abspath(path)
        relative = abs_root != os.path.commonpath([abs_root, abs_path])

        return path if relative else os.path.relpath(abs_path, start=self.root)

    def __generate_entry(self, xpath):
        if not os.path.isfile(xpath):
            print("Not a resource file: {}".format(xpath), file=sys.stderr)
            return None

        entry = {
            "media-type" : parent_dir_name(xpath),
            "full-path"  : self.__internal_path(xpath),
            "md5sum"     : md5sum(xpath),
            "tags"       : []
        }
        return entry

    def __insert_entry(self, ipath, info="INSERT"):
        print("{}: {}".format(info, ipath))
        xpath = self.__external_path(ipath)
        entry = self.__generate_entry(xpath)
        if entry is None:
            print("Failed to create entry for file: {}".format(xpath), file=sys.stderr)
            return False

        self.manifest.insert_entry(entry)
        return True

    def __remove_entry(self, ipath, info="REMOVE"):
        print("{}: {}".format(info, ipath))
        return self.manifest.remove_entry(ipath)
