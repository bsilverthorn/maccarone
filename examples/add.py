def add_two_numbers(x, y):
    #<<add both args>>
    return x + y
    #<</>>

#<<argparse then print result>>
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("x", type=int)
parser.add_argument("y", type=int)
args = parser.parse_args()
print(add_two_numbers(args.x, args.y))
#<</>>
