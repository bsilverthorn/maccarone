import os
import os.path
import glob
import logging

from argparse import Namespace

from maccarone.openai import CachedChatAPI
from maccarone.loader import (
    DEFAULT_CACHE_SUFFIX,
    DEFAULT_MN_SUFFIX,
    replace_suffix,
)
from maccarone.preprocessor import preprocess_maccarone

logger = logging.getLogger(__name__)

def preprocess(
        mn_path: str,
        print_: bool,
        write: bool,
        rewrite: bool,
        search_suffix: str,
    ) -> None:
    # produce Python source
    logger.info("preprocessing %s", mn_path)

    cache_path = replace_suffix(mn_path, DEFAULT_CACHE_SUFFIX, search_suffix)
    chat_api = CachedChatAPI(cache_path)

    #<<mn_source = read mn_path>>

    py_source = preprocess_maccarone(mn_source, chat_api)

    if write:
        py_path = replace_suffix(mn_path, ".py", search_suffix)

        logger.info("writing %s", py_path)

        if py_path == mn_path:
            raise ValueError("won't overwrite input file", mn_path)
    elif rewrite:
        py_path = mn_path
    else:
        py_path = None

    #<<write py_source to py_path if not None>>

    if print_:
        print(py_source, end="")

def main(path: str, print_: bool, write: bool, rewrite: bool, suffix: str) -> None:
    """Preprocess files with Maccarone snippets."""

    if os.path.isdir(path):
        mn_files = glob.glob(
            os.path.join(path, f"**/*{suffix}"),
            recursive=True,
        )
    else:
        mn_files = [path]

    #<<preprocess mn_files>>

def parse_args() -> Namespace:
    #<<
    # get args for main() and return; use argparse
    # set the `print_` var for `--print`
    # default suffix: DEFAULT_MN_SUFFIX
    #>>

def script_main():
    logging.basicConfig(level=logging.INFO)

    return main(**vars(parse_args()))

if __name__ == "__main__":
    script_main()
