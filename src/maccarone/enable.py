import os
import sys
import logging
import importlib.abc
import importlib.machinery

from importlib.abc import (
    MetaPathFinder,
    SourceLoader,
)

from maccarone.preprocessor import preprocess_maccarone

class ImportFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        print("find_spec", fullname, path, target)

        if path is None or path == '':
            path = [os.getcwd()]  # top level import 

        for entry in path:
            parts = fullname.split(".")
            basename = parts[-1]
            package_path = parts[1:-1]
            filename = os.path.join(entry, *package_path, basename) + '.mn.py'
            print("trying", filename)
            if not os.path.exists(filename):
                continue

            return importlib.machinery.ModuleSpec(
                fullname,
                ImportLoader(fullname, filename),
                origin=filename,
                is_package=False
            )

        return None  # we don't know how to import this

class ImportLoader(SourceLoader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def get_filename(self, fullname):
        print("get_filename", fullname)
        return self.path

    def get_data(self, filename):
        with open(self.path, 'r') as file:
            in_source = file.read()

        return preprocess_maccarone(in_source)

sys.meta_path.append(ImportFinder())

if os.environ.get("MACCARONE_LOGGING", False):
    logging.basicConfig(level=logging.DEBUG)
