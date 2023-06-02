def main(path: str):
    #<<filenames = a list of filenames under path>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        print(fn, size)

#<<use argparse and call main>>
