import glob
import logging

from argparse import Namespace

from maccarone.openai import CachedChatAPI
from maccarone.preprocessor import preprocess_maccarone

logger = logging.getLogger(__name__)

def preprocess(mn_path: str, suffix=".mn.py") -> None:
    #<<py_path = mn_path replace suffix with `.py`>>

    # produce Python source
    logger.info("preprocessing %s → %s", mn_path, py_path)

    cache_path = mn_path.replace(suffix, ".mn.json")
    chat_api = CachedChatAPI(cache_path)

    with open(mn_path, "rt") as mn_file:
        mn_source = mn_file.read()
        py_source = preprocess_maccarone(mn_source, chat_api)

    #<<write py_source to py_path>>

def main(root_path: str):
    """Preprocess `*.my.py` to produce pure-Python `.py` files."""

    for path in glob.glob(root_path + "/**/*.mn.py", recursive=True):
        preprocess(path)

def parse_args() -> Namespace:
    #<<use argparse to handle `script ROOT_PATH`>>

def script_main():
    logging.basicConfig(level=logging.INFO)

    return main(**vars(parse_args()))

if __name__ == "__main__":
    script_main()

