import hashlib
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

def parent_dir_name(path):
    parent_dir_path = os.path.dirname(path)
    return os.path.basename(parent_dir_path)

def md5sum(path):
    alg = hashlib.md5()
    with open(path, "rb") as file:
        alg.update(file.read())

    return alg.hexdigest()

class Bundle:
    def __init__(self, path):
        self.root = path
        manifest_path = self.__external_path(Manifest.MANIFEST_PATH)
        self.manifest = Manifest.Manifest(manifest_path)
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

    def __zip_add_file(self):
        pass
