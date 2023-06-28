def add_two_numbers(x, y):
    #<<add both args>>
    return x + y
    #<</>>

#<<argparse stuff>>
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("x", type=int)
parser.add_argument("y", type=int)
args = parser.parse_args()
return add_two_numbers(args.x, args.y)
#<</>>
