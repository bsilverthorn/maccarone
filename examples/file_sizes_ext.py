#<<imports>>
import os
import argparse
from typing import Optional
from termcolor import colored
#<</>>

def main(path: str, extension: str | None):
    #<<filenames = list of filenames under path; no dirs>>
    filenames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (f.endswith(extension) if extension else True)]
    #<</>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        size = os.path.getsize(os.path.join(path, fn))
        #<</>>

        #<<print fn and size with colors>>
        print(colored(f"Filename: {fn}", 'green'), colored(f"Size: {size} bytes", 'blue'))
        #<</>>

#<<use argparse and then call main>>
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to the directory")
    parser.add_argument("--extension", type=str, help="File extension to filter by", default=None)
    args = parser.parse_args()
    main(args.path, args.extension)
#<</>>
