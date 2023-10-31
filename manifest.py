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

import os.path
import xml.dom.minidom as MD
import pprint
from dataclasses import dataclass

MANIFEST_PATH   = "META-INF/manifest.xml"
MANIFEST_XMLNS  = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"

# XML Node Names
ELEM_MANIFEST   = "manifest:manifest"
ELEM_FILE_ENTRY = "manifest:file-entry"
ELEM_TAGS       = "manifest:tags"
ELEM_TAG        = "manifest:tag"
ATTR_VERSION    = "manifest:version"
ATTR_MEDIA_TYPE = "manifest:media-type"
ATTR_FULL_PATH  = "manifest:full-path"
ATTR_MD5SUM     = "manifest:md5sum"

@dataclass
class ManifestEntry:
    """ManifestEntry is a class which represents an entry in the manifest."""

    full_path: str
    media_type: str
    md5sum: str
    tags: list[str]

    def to_string(self):
        tag_list = pprint.pformat(self.tags)
        return '\n'.join([self.full_path,
                          "\tmedia-type: {}".format(self.media_type),
                          "\tmd5sum: {}".format(self.md5sum),
                          "\ttags: {}".format(tag_list)])

class Manifest:
    """A representation of a bundle manifest."""

    def __init__(self, manifestPath):
        self.path = manifestPath
        self.entries = {}

    def exists(self):
        """Test whether the backing manifest XML file exists."""
        return os.path.isfile(self.path)

    def load(self):
        """Read and parse the manifest XML file."""

        doc = MD.parse(self.path)
        root = doc.documentElement
        if root.tagName != ELEM_MANIFEST or root.getAttribute(ATTR_VERSION) != "1.2":
            return False;

        self.entries = {}
        for e in doc.getElementsByTagName(ELEM_FILE_ENTRY):
            entry = self.__entry_from_xml(e)
            if entry is None:
                return False

            # Skip entry for bundle root that is always present.
            if entry.full_path == "/" or entry.full_path == "\\":
                continue

            self.insert_entry(entry)

        return True

    def save(self):
        """Write this manifest to the manifest XML file."""

        # If the "META-INF" directory doesn't exists, create it.
        # The manifest file is created when written.
        (dir_path, _) = os.path.split(self.path)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        doc = self.to_xml()
        output = doc.toprettyxml(indent=' ', encoding='UTF-8')

        with open(self.path, "wb") as manifest_file:
            manifest_file.write(output)

    def insert_entry(self, entry):
        """Add a new ManifestEntry to the manifest."""

        # If an entry already exists for the provided path, replace
        # it, but merge the old and new tag lists.
        if entry.full_path in self.entries:
            entry.tags += self.entries[entry.full_path].tags

        self.entries[entry.full_path] = entry

    def remove_entry(self, path):
        """Remove the entry with the given path from the manifest.

        Returns False if the manifest doesn't contain an entry for the
        given path, or True otherwise.
        """
        if path not in self.entries:
            return False

        del self.entries[path]
        return True

    def has_entry(self, path):
        """Test if the manifest contains an entry for the given path."""
        return path in self.entries

    def compare_entries(self, entry_list):
        """Given a list of paths, determine which overlap with
        manifest entries, and which are present in only one list or
        the other.
        """
        entries_here  = set(self.entries.keys())
        entries_there = set(entry_list)

        common     = entries_here  & entries_there
        only_here  = entries_here  - entries_there
        only_there = entries_there - entries_here

        return (common, only_here, only_there)

    def tags(self, path):
        """Return the list of tags for the resource at the given path.

        If no entry exists for the given path, an empty list is returned.
        """
        if not self.has_entry(path):
            return None

        return self.entries[path].tags

    def add_tag(self, path, tag):
        """Apply a tag to the manifest entry with the given path.

        Return False if there is no matching entry or the entry
        already has the given tag.
        """
        if not self.has_entry(path):
            return False

        if tag in self.entries[path].tags:
            return False

        self.entries[path].tags.append(tag)
        return True

    def remove_tag(self, path, tag):
        """Remove a tag from the manifest entry with the given path.

        Return False if there is no matching entry or the entry
        doesn't have the given tag.
        """
        if not self.has_entry(path):
            return False

        if tag not in self.entries[path].tags:
            return False

        self.entries[path].tags.remove(tag)
        return True

    def to_xml(self):
        """Generate an XML document which describes the manifest."""
        doc = MD.getDOMImplementation().createDocument(MANIFEST_XMLNS, ELEM_MANIFEST, None)

        root = doc.documentElement
        root.setAttribute("xmlns:manifest", MANIFEST_XMLNS)
        root.setAttribute(ATTR_VERSION, "1.2")

        # A file-entry for the bundle's root directory is always included.
        dir_entry = doc.createElement(ELEM_FILE_ENTRY)
        dir_entry.setAttribute(ATTR_MEDIA_TYPE, "application/x-krita-resourcebundle")
        dir_entry.setAttribute(ATTR_FULL_PATH , "/")
        root.appendChild(dir_entry)

        for entry in self.entries.values():
            entry_elem = self.__entry_to_xml(doc, entry)
            root.appendChild(entry_elem)

        return doc

    def to_string(self):
        """Generate a human-readable string representation of the manifest."""
        return '\n\n'.join([entry.to_string() for entry in self.entries.values()])

    def __tags_from_xml(self, e):
        """Parse a list of tags from an appropriate XML DOM element."""
        tags = []
        for tags_elem in e.getElementsByTagName(ELEM_TAGS):
            for tag_elem in tags_elem.getElementsByTagName(ELEM_TAG):
                tags.append(tag_elem.firstChild.data)

        return tags

    def __entry_from_xml(self, e):
        """Parse a ManifestEntry from an equivalent XML DOM element."""
        if e.tagName != ELEM_FILE_ENTRY:
            return None

        # Resource paths in the manifest must use forward slash (/)
        # separators, so we must convert them into the local style.
        fixed_path = os.path.normpath(e.getAttribute(ATTR_FULL_PATH))

        entry = ManifestEntry(full_path  = fixed_path,
                              media_type = e.getAttribute(ATTR_MEDIA_TYPE),
                              md5sum     = e.getAttribute(ATTR_MD5SUM    ),
                              tags       = self.__tags_from_xml(e))
        return entry

    def __tags_to_xml(self, doc, tags):
        """Convert a list of tags into an equivalent XML DOM element."""
        tags_elem = doc.createElement(ELEM_TAGS)

        for tag in tags:
            tag_text = doc.createTextNode(tag)
            tag_elem = doc.createElement(ELEM_TAG)

            tag_elem.appendChild(tag_text)
            tags_elem.appendChild(tag_elem)

        return tags_elem

    def __entry_to_xml(self, doc, entry):
        """Convert a ManifestEntry into an equivalent XML DOM element."""
        entry_elem = doc.createElement(ELEM_FILE_ENTRY)

        # Resource paths in the manifest must use forward slash (/)
        # separators, so Windows-style paths need to be fixed.
        fixed_path = entry.full_path.replace("\\", "/")

        entry_elem.setAttribute(ATTR_MEDIA_TYPE, entry.media_type)
        entry_elem.setAttribute(ATTR_FULL_PATH , fixed_path      )
        entry_elem.setAttribute(ATTR_MD5SUM    , entry.md5sum    )

        if entry.tags:
            tags_elem = self.__tags_to_xml(doc, entry.tags)
            entry_elem.appendChild(tags_elem)

        return entry_elem
