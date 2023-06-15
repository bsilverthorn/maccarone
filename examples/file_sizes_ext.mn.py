def main(path: str, extension: str | None = None):
    #<<filenames = list of filenames under path; no dirs>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        print(fn, size)

#<<use argparse and call main>>
