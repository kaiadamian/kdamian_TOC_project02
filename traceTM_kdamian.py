#!/usr/bin/env python3

'''NTMtracing_kdamian.py - this program traces all the paths that an NTM takes, collects its data, and checks if it accepts or rejects'''

import sys
import csv
import os
from typing import List, Dict

def go_right(left_in: str, right_in: str, replace) -> tuple:
    '''function that changes the strings to the left and right of the tape head based on a RIGHT transition'''
    left_in = left_in + replace                             # add the replacement char to the end of the left string
    right_in = right_in[1:]                                 # slice the first char off the right string
    return(left_in, right_in)

def go_left(left_in: str, right_in: str, replace) -> tuple:
    '''function that changes the strings to the left and right of the tape head based on a LEFT transition'''
    right_in = left_in[-1] + replace + right_in[1:]         # slice the first char off the right string and add the last char of the left string and the replacement char to the beginning of it
    left_in = left_in[:-1]                                  # slice the last char off the left string
    return(left_in, right_in)

def create_tree(transitions: Dict[str, List[str]], configurations: List[List[str]], input, acc_state, rej_state, max_depth, machine_name) -> None:
    '''function that creates a tree that traces an NTM'''
    level = 0                                               # initialize variables
    left_in = ''
    right_in = input
    accepted = False
    rejected = False
    tot_trans = 0
    tot_nonleaves = 0
    state = configurations[level][0][1]
    char = configurations[level][0][2][0]
    prevs = [[]]                                            # initialize list of previous configurations to be able to backtrack the accepting path

    while not accepted and not rejected:
        level_list = []
        prev_list = []
        for config in configurations[level]:                # for each configuration on our current level of the tree
            n_trans = 0
            state = config[1]                               # obtain the current state
            if state == rej_state:                          # skip to next configuration if current state is the reject state
                continue
            if state in transitions:
                for trans in transitions[state]:            # go through each transition from current state
                    right_in = config[2]
                    left_in = config[0]
                    if len(right_in) == 0:
                        right_in = "_"
                    if len(left_in) == 0 and level != 0:
                        left_in = "_"
                    if trans[1] == right_in[0]:             # if transition char matches the char we are reading, make the appropriate replacements and shifts
                        if trans[4] == 'R':
                            left_in, right_in = go_right(left_in, right_in, trans[3])
                        elif trans[4] == 'L':
                            left_in, right_in = go_left(left_in, right_in, trans[3])
                        n_trans += 1                        # increment the number of transitions
                        prev_list.append(config)            # append the configuration to our list of previous configurations for the current level
                        level_list.append([left_in, trans[2], right_in])
                                                            # append the appropriate configuration to our list of configurations for the current level of the tree

            if n_trans == 0:                                # if there was no transition listed for our current configuration
                    if len(right_in) == 0:
                        right_in = "_"
                    if len(left_in) == 0:
                        left_in = "_"
                    replace = right_in[0]                   # shift right and reject
                    left_in, right_in = go_right(left_in, right_in, replace)   
                    n_trans += 1                            # increment the number of transitions
                    prev_list.append(config)                # append the configuration to our list of previous configurations for the current level
                    level_list.append([left_in, rej_state, right_in])
                                                            # append the appropriate REJECTING configuration to our list of configurations for the current level of the tree
            tot_nonleaves += 1
            tot_trans += n_trans
        
        prevs.append(prev_list)                             # append list of previous configurations for the level to the "prevs" list
        configurations.append(level_list)                   # append list of configurations for this level to the "configurations" list

        for config in level_list:                           
            if acc_state in config:                         # if an accepting configuration is found, stop all lines of execution (exit the while loop)
                accepted = True
                continue
        if all(rej_state in list for list in level_list):   # if all configurations are rejecting, stop all lines of execution (exit the while loop)
            rejected = True
        level += 1                                          # increment the level of the tree
        if level > max_depth:
            rejected = True

    n_configs = 0
    for config in configurations:                           # find the total number of configurations
        n_configs += len(config)

    print('-------------------------------------------')
    print('machine information:')
    print('-------------------------------------------')
    print(f'turing machine used: {machine_name}')           # print the required output (NTM, string, result, depth, number of configurations, average nondeterminism, path of configurations)
    print(f'input string used: {input}')
    print(f'accept state: {acc_state}')
    print('-------------------------------------------')
    print('tree of configurations information:')
    print('-------------------------------------------')
    print(f'depth: {level}')
    print(f'number of configurations explored: {n_configs}')
    print(f'total transitions (execution time): {tot_trans}')
    print(f'total nonleaves: {tot_nonleaves}')
    print(f'average nondeterminism: {tot_trans/tot_nonleaves}')
    if accepted is True:
        print(f'result: ACCEPTED in {level} transitions')
        print('-------------------------------------------')
        print('path of configurations to accept state:')
        print('-------------------------------------------')
        path_to_acc = tracing_tree(configurations, prevs, acc_state)
        for config in path_to_acc:
            print(','.join(x if x else '_' for x in config))
    elif level < max_depth:
        print(f'result: REJECTED in {level} transitions')
    else: 
        print(f'execution STOPPED after {max_depth} transitions')
    print('-------------------------------------------')
    print('each configuration, beginning at the start:')
    print('-------------------------------------------')
    for lvl in configurations:
        print(' | '.join(
        ','.join(x if x else '_' for x in config)
        for config in lvl
    ))
    print()

def tracing_tree(configurations: List[List[str]], prevs: List[List[str]], acc_state) -> list:
    '''tracing tree function'''
    path_to_acc = []
    acc_index = None

    for i, config in enumerate(configurations[-1]):         # search for the last accepting configuration and accepting index
        if acc_state in config:
            acc_index = i                                   # update accepting index
            path_to_acc.append(config)                      # add the accepting configuration to the path
            break
    
    if acc_index is None:                                   # ERROR CHECK: if no accept state is found, return an empty path
        return path_to_acc
    
    for level in range(len(configurations) - 2, -1, -1):    # trace backwards through the tree, starting from the second-to-last level
        config = prevs[level + 1][acc_index]                # get the parent configuration of the current accepting configuration
        path_to_acc.append(config)
        acc_index = configurations[level].index(config)     # update acc_index to the index of this config in the current level
    
    return path_to_acc[::-1]                                # reverse the path the starting configuration to the last accepting configuration

def help(file: str, input: str, max_depth: int) -> None:
    '''help function'''
    print(f'Usage: {sys.argv[0]} [file name] [max depth] [input]')
    print(f'     input all 3 parameters or none at all: defaults are [{file}] [{input}] [{max_depth}]')
    print()

def main() -> None:
    '''main function'''
    file = "check_equal_abs-kdamian.csv"                               # set default parameters
    input = "abab"
    max_depth = 50

    if len(sys.argv) == 4:                                  # ERROR CHECK: ensure user inputted at least the file name
        file = sys.argv[1]                                  # initialize file name
        if not os.path.isfile(file):                        # ERROR CHECK: ensure user inputted a valid file
            print(f'the file "{file}" is invalid')
            help(file, input, max_depth)
            return
        try:
            max_depth = int(sys.argv[2])                    # initialize max depth
        except ValueError:
            print("ERROR: max depth must be an integer")
            help(file, input, max_depth)
            return
        input = sys.argv[3]                                 # initialize input string
    elif len(sys.argv) != 1:
        help(file, input, max_depth)
    

    transitions = {}                                        # initialize transitions dict with states as keys and their corresponding configurations as values

    with open(file, mode = 'r') as file:
        csv_file = csv.reader(file)                         # read in the lines of the .csv and initialize appropriate variables
        for count, line in enumerate(csv_file):
            if count == 0:
                machine_name = line[0]
            elif count == 2:
                input_alpha = line
            elif count == 4: 
                start_state = line[0]
            elif count == 5:
                acc_state = line[0]
            elif count == 6:
                rej_state = line[0]
            elif count >= 7:
                transitions.setdefault(line[0], []).append(line)

    for char in input:                                      # ERROR CHECK: ensure user used valid input alphabet for machine given
        if char not in input_alpha and char != '_':
            print(f'STRING REJECTED: invalid char "{char}" in input for machine {machine_name}')
            return
            
    configurations = []                                     # initialize configurations, which will end up being a list of lists (for each level) of lists (for each configuration)
    configurations.append([["", start_state, input]])       # initialize the starting configuration in the configurations list
                                                            # call create_tree to create a tree that traces a given NTM and prints required output
    create_tree(transitions, configurations, input, acc_state, rej_state, max_depth, machine_name)
    
if __name__ == '__main__':
    main()