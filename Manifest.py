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

        for elem in doc.getElementsByTagName(TAG_FILE_ENTRY):
            entry = self.__entry_from_xml(elem)
            if entry is None:
                return False

            # Skip entry for bundle root that is always present
            if entry["full-path"] == "/":
                continue

            self.insert_entry(entry)

        return True

    def save(self):
        manifestFile = open(self.path, "w")

        doc = self.to_xml()
        output = doc.toprettyxml(indent=' ')
        manifestFile.write(output)

        manifestFile.close()

    def insert_entry(self, entry):
        path = entry["full-path"]

        if path in self.entries:
            entry["tags"] += self.entries[path]["tags"]

        self.entries[path] = entry

    def remove_entry(self):
        pass

    def has_entry(self):
        pass

    def add_tag(self):
        pass

    def remove_tag(self):
        pass

    def to_xml(self):
        doc = MD.getDOMImplementation().createDocument(MANIFEST_XMLNS, TAG_MANIFEST, None)

        root = doc.documentElement
        root.setAttribute("xmlns:manifest", MANIFEST_XMLNS)
        root.setAttribute(ATTR_VERSION, "1.2")

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
            print("Invalid file entry.")
            return None

        entry = {
            "media-type" : e.getAttribute(ATTR_MEDIA_TYPE),
            "full-path"  : e.getAttribute(ATTR_FULL_PATH),
            "md5sum"     : e.getAttribute(ATTR_MD5SUM),
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
