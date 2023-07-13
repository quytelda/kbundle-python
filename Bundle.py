import os.path
import Manifest

class Bundle:
    def __init__(self, path):
        self.root = path
        manifest_path = os.path.join(path, Manifest.MANIFEST_PATH)
        self.manifest = Manifest.Manifest(manifest_path)

    def scan_files(self):
        pass

    def load(self):
        pass

    def prune_manifest(self):
        pass

    def update_manifest(self):
        pass

    def add_tag(self):
        pass

    def remove_tag(self):
        pass

    def build(self):
        pass

    def __external_path(self):
        pass

    def __internal_path(self):
        pass

    def __zip_add_file(self):
        pass
