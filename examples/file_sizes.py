def main(path: str):
    #<<filenames = list of filenames under path; no dirs>>
    import os
    filenames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    #<</>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        size = os.path.getsize(fn)
        #<</>>
        print(fn, size)

#<<use argparse and call main once>>
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("path", type=str)
args = parser.parse_args()
main(args.path)
#<</>>
