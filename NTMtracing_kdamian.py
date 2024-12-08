#!/usr/bin/env python3

'''NTMtracing_kdamian.py - this program traces all the paths that an NTM takes and checks if it accepts or rejects'''

import csv
from typing import List, Dict

def go_right(left_in: str, right_in: str, replace) -> tuple:
    left_in = left_in + replace
    right_in = right_in[1:]
    return(left_in, right_in)

def go_left(left_in: str, right_in: str, replace) -> tuple:
    right_in = left_in[-1] + replace + right_in[1:]
    left_in = left_in[:-1]
    return(left_in, right_in)

def create_tree(transitions: Dict[str, List[str]], configurations: List[List[str]], input, acc_state, rej_state, max_depth, machine_name):
    '''tree creation for NTM tracing function'''
    level = 0
    state = configurations[level][0][1]
    char = configurations[level][0][2][0]
    left_in = ''
    right_in = input
    accepted = False
    rejected = False
    tot_trans = 0
    tot_nonleaves = 0

    while not accepted and not rejected:
        level_list = []
        for config in configurations[level]:
            n_trans = 0
            state = config[1]
            if state == rej_state:
                continue
            if state in transitions:
                for trans in transitions[state]:
                    right_in = config[2]
                    left_in = config[0]
                    if len(right_in) == 0:
                        right_in = "_"
                    if len(left_in) == 0 and level != 0:
                        left_in = "_"
                    if trans[1] == right_in[0]:
                        if trans[4] == 'R':
                            left_in, right_in = go_right(left_in, right_in, trans[3])
                        elif trans[4] == 'L':
                            left_in, right_in = go_left(left_in, right_in, trans[3])
                        n_trans += 1    
                        level_list.append([left_in, trans[2], right_in])

            if n_trans == 0: 
                    replace = right_in[0]
                    left_in, right_in = go_right(left_in, right_in, replace)   
                    n_trans += 1             
                    level_list.append([left_in, rej_state, right_in])
            tot_nonleaves += 1
            tot_trans += n_trans
        
        configurations.append(level_list)

        for config in level_list:
            if acc_state in config:
                accepted = True
                continue
        if all(rej_state in list for list in level_list):
            rejected = True
        level += 1
        if level > max_depth:
            rejected = True

    n_configs = 0
    for config in configurations:
        n_configs += len(config)

    print(f'NTM: {machine_name}')
    print(f'string used: {input}')
    print(f'accept state: {acc_state}')
    if accepted is True:
        print(f'result: ACCEPTED in {level} transitions')
        print('each configuration, beginning at the start:')
        print('-------------------------------------------')
        for lvl in configurations:
            print('|'.join(
            ','.join(x if x else '_' for x in config)
            for config in lvl
        ))
        print('-------------------------------------------')
    elif level < max_depth:
        print(f'result: REJECTED in {level} transitions')
    else: 
        print(f'execution STOPPED after {max_depth} transitions')
    print(f'total transitions: {tot_trans}')
    print(f'total nonleaves: {tot_nonleaves}')
    print(f'depth of tree: {level}')
    print(f'number of configurations explored: {n_configs}')
    print(f'average nondeterminism: {tot_trans/tot_nonleaves}')


def main() -> None:
    '''main function'''
    file = "a_plus.csv" 
    input = "a"
    max_depth = 50
    transitions = {}

    with open(file, mode = 'r') as file:
        csv_file = csv.reader(file)
        for count, line in enumerate(csv_file):
            if count == 0:
                machine_name = line[0]
            elif count == 4: 
                start_state = line[0]
            elif count == 5:
                acc_state = line[0]
            elif count == 6:
                rej_state = line[0]
            elif count >= 7:
                transitions.setdefault(line[0], []).append(line)
            
    configurations = []
    configurations.append([["", start_state, input]])

    create_tree(transitions, configurations, input, acc_state, rej_state, max_depth, machine_name)
    
if __name__ == '__main__':
    main()