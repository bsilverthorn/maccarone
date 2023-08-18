import os
import os.path
import glob
import logging

from argparse import Namespace
from typing import Optional

from maccarone.openai import ChatAPI
from maccarone.preprocessor import preprocess_maccarone

logger = logging.getLogger(__name__)

def preprocess(
        mn_path: str,
        print_: bool,
        rewrite: bool,
        block_at_line: Optional[int],
    ) -> None:
    # produce Python source
    logger.info("preprocessing %s", mn_path)

    chat_api = ChatAPI()

    #<<mn_source = read mn_path>>
    with open(mn_path, 'r') as file:
        mn_source = file.read()
    #<</>>

    py_source = preprocess_maccarone(mn_source, chat_api, block_at_line=block_at_line)

    if rewrite:
        #<<write py_source to py_path>>
        py_path = os.path.splitext(mn_path)[0] + '.py'
        with open(py_path, 'w') as file:
            file.write(py_source)
        #<</>>

    if print_:
        print(py_source, end="")

def main(path: str, print_: bool, rewrite: bool, suffix: str, block_at_line: Optional[int] = None) -> None:
    """Preprocess files with Maccarone snippets."""

    if os.path.isdir(path):
        mn_files = glob.glob(
            os.path.join(path, f"**/*{suffix}"),
            recursive=True,
        )
    else:
        mn_files = [path]

    #<<preprocess mn_files>>
    for mn_file in mn_files:
        preprocess(mn_file, print_, rewrite, block_at_line)
    #<</>>

def parse_args() -> Namespace:
    #<<
    # get args for main() and return; use argparse
    # set the `print_` var for `--print`
    # default suffix: ".py"
    #>>
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file or directory to preprocess")
    parser.add_argument("--print", dest="print_", action="store_true", help="Print the preprocessed source code")
    parser.add_argument("--rewrite", action="store_true", help="Rewrite the source file with the preprocessed code")
    parser.add_argument("--suffix", default=".py", help="Suffix for the preprocessed files")
    parser.add_argument("--block-at-line", type=int, help="Preprocess only the block at given line")
    args = parser.parse_args()
    return args
    #<</>>

def script_main():
    logging.basicConfig(level=logging.INFO)

    return main(**vars(parse_args()))

if __name__ == "__main__":
    script_main()
