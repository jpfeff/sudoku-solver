# Modified by Joshua Pfefferkorn
# Dartmouth CS76, Fall 2021
# November 1, 2021

from display import display_sudoku_solution
import random, sys
from SAT import SAT
import time

if __name__ == "__main__":
    # for testing, always initialize the pseudorandom number generator to output the same sequence
    #  of values:
    random.seed(2)

    puzzle_name = str(sys.argv[1][:-4])
    sol_filename = puzzle_name + ".sol"

    sat = SAT(sys.argv[1], 1000000)

    start = time.time()
    result = sat.walksat()
    end = time.time()

    print("Time elapsed:", end-start)

    if result:
        sat.write_solution(sol_filename, result)
        display_sudoku_solution(sol_filename)