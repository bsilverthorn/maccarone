def main(n: int):
    #<<do fizzbuzz from 1 to n>>
    for i in range(1, n+1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)
    #<</>>

#<<
# parse command line args for main
# call main with those args
#>>
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("n", type=int)
args = parser.parse_args()
main(args.n)
#<</>>
