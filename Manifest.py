import pathlib
import xml.dom.minidom as MD

class Manifest:

    def __init__(self, manifestPath):
        self.path = manifestPath
        self.entries = {}

    def exists(self):
        return pathlib.Path(self.path).is_file()

    def load(self):
        pass

    def save(self):
        pass

    def insert_entry(self, entry):
        pass

    def remove_entry(self):
        pass

    def has_entry(self):
        pass

    def add_tag(self):
        pass

    def remove_tag(self):
        pass

    def to_xml(self):
        pass

    def resource_list(self):
        pass

    def __tags_from_xml(self, e):
        tags = []
        for tags_elem in e.getElementsByTagName("manifest:tags"):
            for tag_elem in tags_elem.getElementsByTagName("manifest:tag"):
                tags.append(tag_elem.firstChild.data)

        return tags

    def __entry_from_xml(self, e):
        if e.tagName != "manifest:file-entry":
            print("Invalid file entry.")
            return None

        entry = {
            "media-type" : e.getAttribute("manifest:media-type"),
            "full-path"  : e.getAttribute("manifest:full-path"),
            "md5sum"     : e.getAttribute("manifest:md5sum"),
            "tags"       : self.__tags_from_xml(e)
        }

        return entry

    def __tags_to_xml(self):
        pass

    def __entry_to_xml(self):
        pass
