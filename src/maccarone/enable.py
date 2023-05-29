import os
import re
import sys
import logging
import importlib.abc
import importlib.machinery

from enum import Enum
from importlib.abc import (
    MetaPathFinder,
    SourceLoader,
)
from importlib.machinery import ModuleSpec

from maccarone.preprocessor import preprocess_maccarone

enable_py_string_matching = True
fullname_pattern: str | None = None

class ImportFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # check against module name pattern, if configured
        if fullname_pattern is not None:
            if re.match(fullname_pattern, fullname) is None:
                return None

        # module name looks ok; check for maccarone snippets
        def make_modulespec(filename):
            return ModuleSpec(
                fullname,
                ImportLoader(fullname, filename),
                origin=filename,
                is_package=False
            )

        if path is None or path == '':
            path = [os.getcwd()]  # top level import 

        for entry in path:
            parts = fullname.split(".")
            basename = parts[-1]
            package_path = parts[1:-1]
            base_filename = os.path.join(entry, *package_path, basename)
            py_filename = base_filename + '.py'
            mn_filename = base_filename + '.mn.py'

            if os.path.exists(mn_filename):
                return make_modulespec(mn_filename)
            elif os.path.exists(py_filename):
                with open(py_filename, "rt") as file:
                    if "#<<" in file.read():
                        return make_modulespec(py_filename)

        return None  # we don't know how to import this

class ImportLoader(SourceLoader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def get_filename(self, fullname):
        return self.path

    def get_data(self, filename):
        with open(self.path, 'r') as file:
            in_source = file.read()

        return preprocess_maccarone(in_source)

sys.meta_path.insert(0, ImportFinder())

if os.environ.get("MACCARONE_LOGGING", False):
    logging.basicConfig(level=logging.DEBUG)
