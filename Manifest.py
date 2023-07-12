import pathlib

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
        pass

    def __entry_from_xml(self, e):
        pass

    def __tags_to_xml(self):
        pass

    def __entry_to_xml(self):
        pass
