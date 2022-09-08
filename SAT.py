# Written by Joshua Pfefferkorn
# Dartmouth CS76, Fall 2021
# November 1, 2021

# GSAT algorithm adapted from pseudocode found here:
# https://www.researchgate.net/publication/2634047_A_New_Method_for_Solving_Hard_Satisfiability_Problems

import random

class SAT:
    def __init__(self, cnf_filename, max_iterations):
        # limit on the maximum number of iterations before the algorithms reach failure
        self.max_iterations = max_iterations
        # holds integer variable numbers
        self.variables = []
        # the name of the .cnf file for the program to solve
        self.cnf_filename = cnf_filename
        # a dictionary mapping from variable name to its assigned integer value (1,2,3,...)
        self.vars_to_ints = {}
        # a set of sets, each inner set representing an "or" clause in the knowledge base
        self.clauses = self.split_clauses()
        # counter for testing
        self.iterations = 0
    
    # creates a set of sets of clauses, with each variable converted to an integer
    def split_clauses(self):
        # open filename.cnf
        cnf_file = open(self.cnf_filename, 'r')
        # empty set representing the knowledge base that will contain inner sets, each one representing a clause
        clauses = set()
        # counter for assigning integer values to variables
        ctr = 1

        # iterate over lines in .cnf file
        for line in cnf_file:
            # split each line into variables, creating a list
            variables = line.split()
            # empty set to hold the current individual clause
            clause = set()
            # iterate over variables in the current clause
            for var in variables:
                # boolean to track whether the current variable is negated
                negated = False

                # if the variable is negated
                if var[0] == '-':
                    # store variable as everything after '-'
                    var = var[1:]
                    negated = True
            
                # if a variable (or negated version) is not already in dictionary
                if var not in self.vars_to_ints:
                    # assign an integer value and link the variable to its value in the dictionary
                    self.vars_to_ints[var] = ctr
                    value = ctr
                    # increment the integer counter
                    ctr += 1
                    # store each integer
                    self.variables.append(value)
                else:
                    # otherwise get the variable's previously-assigned integer
                    value = self.vars_to_ints[var]
                
                # after integer assignment to the current clause (negative if the variable was negated, positive otherwise)
                if negated:
                    clause.add(-1*value)
                else:
                    clause.add(value)
                    
            # add each individual clause to the set of clauses in the knowledge base
            clauses.add(frozenset(clause))
        # close the file
        cnf_file.close()
        # return the knowledge base as a set of sets
        return clauses
    
    # boolean satisfiability problem algorithm #1
    def gsat(self):
        # threshold for random pick vs. intelligent pick
        threshold = 0.7
        # generate a random assignment 
        assignment = self.generate_random_assignment()
        # until maximum iterations has been reached
        for i in range(self.max_iterations):
            print("iteration:", self.iterations)
            self.iterations += 1
            # check if all clauses are satisfied, and return the consistent assignment if so
            if self.is_consistent(assignment):
                return assignment
            # choose a random number between 0 and 1
            if random.random() > threshold:
                # choose a variable at random from all variables
                random_index = random.randint(1,len(assignment)-1)
                # flip it
                assignment = self.flip_variable(random_index, assignment)
            else:
                # get a variable that will result in the largest increase in satisfied clauses
                best_index = self.choose_variable(self.variables,assignment)
                # flip it
                assignment = self.flip_variable(best_index, assignment)
        
        return 'no satisfying assignment found'

    # boolean satisfiability problem algorithm #2         
    def walksat(self):
        # threshold for random pick vs. intelligent pick
        threshold = 0.7
        # generate a random assignment 
        assignment = self.generate_random_assignment()
        # until maximum iterations has been reached
        for i in range(self.max_iterations):
            print("iteration:", self.iterations)
            self.iterations += 1
            # check if all clauses are satisfied, and return the consistent assignment if so
            if self.is_consistent(assignment):
                return assignment
            # choose a random number between 0 and 1
            if random.random() > threshold:
                # choose a variable at randon
                random_index = random.randint(1,len(assignment)-1)
                # flip it
                assignment = self.flip_variable(random_index, assignment)
            else:
                # creates a pool of candidate variables from a randomly-chosen unsatisfied clause
                vars = self.get_candidates(assignment)
                # get a variable that will result in the largest increase in satisfied clauses
                best_index = self.choose_variable(vars, assignment)
                # flip it
                assignment = self.flip_variable(best_index, assignment)
        
        return 'no satisfying assignment found'
    
    # returns a list of variables from a randomly-selected unsatisfied clause
    def get_candidates(self, assignment):
        unsatisfied_clauses = []
        # get a list of clauses that are not satisfied by the assignment
        for clause in self.clauses:
            if not self.clause_satisfied(assignment,clause):
                unsatisfied_clauses.append(clause)
        # choose one at random
        random_index = random.randint(0,len(unsatisfied_clauses)-1)
        random_clause = unsatisfied_clauses[random_index]
        # get all the variables from that clause
        candidate_variables = []
        for var in random_clause:
            candidate_variables.append(var)

        return candidate_variables

    # changes a variables value in the assignment
    def flip_variable(self, index, assignment):
        # if the value was 0 make it 1
        if assignment[index] == 0:
            assignment[index] = 1
        # vice versa
        else:
            assignment[index] = 0
        
        return assignment

    # generates a random assignment (list of 0s and 1s) for the variables
    def generate_random_assignment(self):
        # put a placeholder at index 0 in the assignment so that variable integers and assignment indices align
        assignment = ['empty']
        # create a random assignment of 0s and 1s
        for variable in self.vars_to_ints:
            assignment.append(random.randint(0,1))

        return assignment
    
    # chooses a variable that maximizes the number of clauses satisfied by flipping it
    def choose_variable(self, variables, assignment):
        # store best score, initially -inf, and a list of best variables
        best_score = float('-inf')
        best_var_list = []

        # iterate over variables
        for var in variables:
            # calculate the number of clauses satisfied by flipping that variable
            score = self.num_clauses_satisfied(var,assignment)
            # if the score is better than the current best score
            if score > best_score:
                # store the score
                best_score = score
                # empty the best variable list and add it to it
                best_var_list = []
                best_var_list.append(var)
            # if the score matches the current best score
            elif score == best_score:
                # add the variable to the list of best variables
                best_var_list.append(var)
                
        # randomly choose an variable from the best variable list
        random_index = random.randint(0,len(best_var_list)-1)

        return best_var_list[random_index]
    
    # calculates the number of clauses satisfied by flipping a given variable in the assignment
    def num_clauses_satisfied(self, var, assignment):
        # copy the assignment
        assignment_copy = assignment.copy()
        # flip the selected variable
        assignment_copy = self.flip_variable(var, assignment_copy)
        ctr = 0
        # count the number of clauses satisfied
        for clause in self.clauses:
            if self.clause_satisfied(assignment_copy,clause):
                ctr += 1
        return ctr

    # returns true if a clause is satisfied given some assignment, false otherwise
    def clause_satisfied(self, assignment, clause):
        clause_satisfied = False
        # iterate over variable in each clause
        for var in clause:
            # get its assigned value (0 for false, 1 for true)
            val = assignment[var]

            # if the variable is negated
            if var < 0:
                # a value of false satisfies the clause
                if val == 0:
                    clause_satisfied = True
                    break

            # if the variable is not negated
            else:
                # a value of true satisfies the clause
                if val == 1:
                    clause_satisfied = True
                    break
        
        return clause_satisfied
    
    # returns true if assignment satisfies all clauses
    def is_consistent(self, assignment):
        # iterate over clauses
        for clause in self.clauses:

            # if any clause is not satisifed, return false
            if not self.clause_satisfied(assignment, clause):
                return False

        # if all clauses are satisgfied, return true
        return True

    # writes the solution to a .sol file
    def write_solution(self, filename, assignment):
        # create a file to hold the solution
        sol = open(filename, 'w')

        # iterates over the assignment
        for var in range(1, len(assignment)):
            # iterates over the dictionary to find the original variable (from its integer value)
            for key in self.vars_to_ints:
                if self.vars_to_ints[key] == var:
                    var_str = key
                    break

            # if the assignment is false (0), write in the variable name with a '-' in front
            if assignment[var] == 0:
                sol.write('-' + var_str + '\n')
            # otherwise write in the variable name
            else:
                sol.write(var_str + '\n')
