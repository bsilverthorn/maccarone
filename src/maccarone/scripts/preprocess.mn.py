import glob
import logging

from argparse import (
    ArgumentParser,
    Namespace,
)

from maccarone.preprocessor import preprocess_maccarone

logger = logging.getLogger(__name__)

def preprocess(mn_path: str, suffix=".mn.py") -> None:
    # replace suffix with `.py`
    assert mn_path.endswith(suffix)

    py_path = mn_path[:-len(suffix)] + ".py"

    # produce Python source
    logger.info("preprocessing %s → %s", mn_path, py_path)

    with open(mn_path, "rt") as mn_file:
        mn_source = mn_file.read()
        py_source = preprocess_maccarone(mn_source)

    with open(py_path, "wt") as file:
        file.write(py_source)

def main(root_path: str):
    """Preprocess maccarone files into Python."""

    for path in glob.glob(root_path + "/**/*.mn.py", recursive=True):
        preprocess(path)

def parse_args() -> Namespace:
    #<<use argparse to handle `script ROOT_PATH`>>

def script_main():
    logging.basicConfig(level=logging.INFO)

    return main(**vars(parse_args()))

if __name__ == "__main__":
    script_main()

