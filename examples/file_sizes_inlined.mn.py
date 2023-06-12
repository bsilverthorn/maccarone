def main(path: str):
    #<<filenames = a list of filenames under path>>
    import os
    filenames = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    #<</>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        size = os.path.getsize(fn)
        #<</>>
        print(fn, size)

#<<use argparse and call main>>
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("path", type=str)
args = parser.parse_args()
main(args.path)
#<</>>
