import sys
import os.path
import Manifest

RESOURCE_DIR_NAMES = ["brushes",
                      "gamutmasks",
                      "gradients",
                      "paintoppresets",
                      "palettes",
                      "patterns",
                      "seexpr_scripts",
                      "workspaces"]

class Bundle:
    def __init__(self, path):
        self.root = path
        manifest_path = self.__external_path(Manifest.MANIFEST_PATH)
        self.manifest = Manifest.Manifest(manifest_path)
        self.resources = []

    def load(self):
        pass

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
                filepath = os.path.join(dirpath, filename)
                self.resources.append(filepath)

        return True

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

    def __external_path(self, ipath):
        return os.path.join(self.root, ipath)

    def __internal_path(self, xpath):
        return os.path.relpath(xpath, start=self.root)

    def __zip_add_file(self):
        pass
