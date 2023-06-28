#<<imports>>
import os
import sys
from typing import List
#<</>>

def main(path: str, extension: str | None):
    #<<filenames = list of filenames under path; no dirs>>
    filenames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (extension is None or f.endswith(extension))]
    #<</>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        size = os.path.getsize(os.path.join(path, fn))
        #<</>>

        #<<print fn and size with colors>>
        print(f"\033[1;34m{fn}\033[0m: \033[1;32m{size} bytes\033[0m")
        #<</>>

#<<use argparse and then call main>>
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", help="Path to the directory containing files")
parser.add_argument("-e", "--extension", help="Filter files by extension", default=None)
args = parser.parse_args()

main(args.path, args.extension)
#<</>>
