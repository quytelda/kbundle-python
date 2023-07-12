import os.path
import xml.dom.minidom as MD

MANIFEST_PATH  = "META-INF/manifest.xml"
MANIFEST_XMLNS = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"

# XML Node Names
TAG_MANIFEST    = "manifest:manifest"
TAG_FILE_ENTRY  = "manifest:file-entry"
TAG_TAGS        = "manifest:tags"
TAG_TAG         = "manifest:tag"
ATTR_VERSION    = "manifest:version"
ATTR_MEDIA_TYPE = "manifest:media-type"
ATTR_FULL_PATH  = "manifest:full-path"
ATTR_MD5SUM     = "manifest:md5sum"

class Manifest:

    def __init__(self, manifestPath):
        self.path = manifestPath
        self.entries = {}

    def exists(self):
        return os.path.isfile(self.path)

    def load(self):
        doc = MD.parse(self.path)

        root = doc.documentElement
        if root.tagName != TAG_MANIFEST or root.getAttribute(ATTR_VERSION) != "1.2":
            return False;

        for e in doc.getElementsByTagName(TAG_FILE_ENTRY):
            entry = self.__entry_from_xml(e)
            if entry is None:
                return False

            # Skip entry for bundle root that is always present
            if entry["full-path"] == "/":
                continue

            self.insert_entry(entry)

        return True

    def save(self):
        # If the "META-INF" directory doesn't exists, create it.
        # The manifest file is created when written.
        (dir_path, _) = os.path.split(self.path)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        doc = self.to_xml()
        output = doc.toprettyxml(indent=' ')

        with open(self.path, "w") as manifestFile:
            manifestFile.write(output)

    def insert_entry(self, entry):
        path = entry["full-path"]
        if path in self.entries:
            entry["tags"] += self.entries[path]["tags"]

        self.entries[path] = entry

    def remove_entry(self, path):
        if path not in self.entries:
            return False

        del self.entries[path]
        return True

    def has_entry(self, path):
        return path in self.entries

    def add_tag(self, path, tag):
        if not self.has_entry(path):
            return False

        if tag in self.entries[path]["tags"]:
            return False

        self.entries[path]["tags"].append(tag)
        return True

    def remove_tag(self, path, tag):
        if not self.has_entry(path):
            return False

        if tag not in self.entries[path]["tags"]:
            return False

        self.entries[path]["tags"].remove(tag)
        return True

    def to_xml(self):
        doc = MD.getDOMImplementation().createDocument(MANIFEST_XMLNS, TAG_MANIFEST, None)

        root = doc.documentElement
        root.setAttribute("xmlns:manifest", MANIFEST_XMLNS)
        root.setAttribute(ATTR_VERSION, "1.2")

        # A file-entry for the bundle's root directory is always included.
        dir_entry = doc.createElement(TAG_FILE_ENTRY)
        dir_entry.setAttribute(ATTR_MEDIA_TYPE, "application/x-krita-resourcebundle")
        dir_entry.setAttribute(ATTR_FULL_PATH , "/")
        root.appendChild(dir_entry)

        for entry in self.entries.values():
            entry_elem = self.__entry_to_xml(doc, entry)
            root.appendChild(entry_elem)

        return doc

    def resource_list(self):
        pass

    def __tags_from_xml(self, e):
        tags = []
        for tags_elem in e.getElementsByTagName(TAG_TAGS):
            for tag_elem in tags_elem.getElementsByTagName(TAG_TAG):
                tags.append(tag_elem.firstChild.data)

        return tags

    def __entry_from_xml(self, e):
        if e.tagName != TAG_FILE_ENTRY:
            return None

        entry = {
            "media-type" : e.getAttribute(ATTR_MEDIA_TYPE),
            "full-path"  : e.getAttribute(ATTR_FULL_PATH ),
            "md5sum"     : e.getAttribute(ATTR_MD5SUM    ),
            "tags"       : self.__tags_from_xml(e)
        }

        return entry

    def __tags_to_xml(self, doc, tags):
        tags_elem = doc.createElement(TAG_TAGS)

        for tag in tags:
            tag_text = doc.createTextNode(tag)
            tag_elem = doc.createElement(TAG_TAG)

            tag_elem.appendChild(tag_text)
            tags_elem.appendChild(tag_elem)

        return tags_elem

    def __entry_to_xml(self, doc, entry):
        entry_elem = doc.createElement(TAG_FILE_ENTRY)

        entry_elem.setAttribute(ATTR_MEDIA_TYPE, entry["media-type"])
        entry_elem.setAttribute(ATTR_FULL_PATH , entry["full-path"] )
        entry_elem.setAttribute(ATTR_MD5SUM    , entry["md5sum"]    )

        if entry["tags"]:
            tags_elem = self.__tags_to_xml(doc, entry["tags"])
            entry_elem.appendChild(tags_elem)

        return entry_elem
