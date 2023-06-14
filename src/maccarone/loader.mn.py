import os
import sys
import logging

from importlib.abc import (
    MetaPathFinder,
    SourceLoader,
)
from importlib.machinery import ModuleSpec
from fnmatch import fnmatchcase

from maccarone.openai import CachedChatAPI
from maccarone.preprocessor import preprocess_maccarone

SNIPPET_START = "#" + "<<"
DEFAULT_MN_SUFFIX = ".mn.py"
DEFAULT_CACHE_SUFFIX = ".mn.json"

class ImportFinder(MetaPathFinder):
    def __init__(
            self,
            py_string_matching: bool,
            include_pattern: str | None,
            exclude_pattern: str | None,
        ) -> None:
        self.py_string_matching = py_string_matching
        self.include_pattern = include_pattern
        self.exclude_pattern = exclude_pattern

    def find_spec(self, fullname, path, target=None):
        # check against module name patterns, if configured
        if self.exclude_pattern is not None:
            if fnmatchcase(fullname, self.exclude_pattern) is not None:
                return None

        if self.include_pattern is not None:
            if fnmatchcase(fullname, self.include_pattern) is None:
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
            basename = fullname.split(".")[-1]
            base_filename = os.path.join(entry, basename)
            py_filename = base_filename + '.py'
            mn_filename = base_filename + DEFAULT_MN_SUFFIX

            if os.path.exists(mn_filename):
                return make_modulespec(mn_filename)
            elif self.py_string_matching and os.path.exists(py_filename):
                with open(py_filename, "rt") as file:
                    if SNIPPET_START in file.read():
                        return make_modulespec(py_filename)

        return None  # we don't know how to import this

def replace_suffix(path: str, new_suffix: str, search_suffix: str) -> str:
    """
    Replace suffix (i.e., file extension) per the following rules:

    - Replace entire search suffix if it matches.
    - Otherwise replace the last file extension.
    """

    if path.endswith(search_suffix):
        return path[:-len(search_suffix)] + new_suffix
    else:
        (root, _) = os.path.splitext(path)

        return root + new_suffix

class ImportLoader(SourceLoader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def get_filename(self, fullname):
        return self.path

    def get_data(self, filename):
        with open(self.path, 'r') as file:
            in_source = file.read()

        cache_path = replace_suffix(
            self.path,
            DEFAULT_CACHE_SUFFIX,
            search_suffix=DEFAULT_MN_SUFFIX,
        )
        chat_api = CachedChatAPI(cache_path)

        return preprocess_maccarone(in_source, chat_api)

def enable(
        py_string_matching=True,
        include_pattern=None,
        exclude_pattern=None,
    ):
    """Exclude patterns take precedence over include patterns."""

    import_finder = ImportFinder(
        py_string_matching=py_string_matching,
        include_pattern=include_pattern,
        exclude_pattern=exclude_pattern,
    )

    sys.meta_path.insert(0, import_finder)

    if os.environ.get("MACCARONE_LOGGING", False):
        logging.basicConfig(level=logging.DEBUG)
