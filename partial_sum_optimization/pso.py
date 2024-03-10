#!/usr/bin/env python3

"""
Partial sum optimization for Skinny.
Copyright (C) 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import minizinc
import json
import argparse
from datetime import timedelta
import math

def propagate_dependency(start_round, final_round, balanced_cell):
    # Round i: Zi-1 -(ARK)-> Xi -(SR)-> Yi -(MC)-> Zi
    X = [[True if c == balanced_cell else False for c in range(16)]]
    W = []
    or3 = lambda x, y, z: [xi or yi or zi for xi, yi, zi in zip(x, y, z)]
    shiftrows = lambda X : X[0:4] + X[7:8] + X[4:7] + X[10:12] + X[8:10] + X[13:16] + X[12:13]
    mixcolumn = lambda X : X[12:16] + or3(X[0:4], X[4:8], X[8:12]) + X[4:8] + or3(X[4:8], X[8:12], X[12:16])
    for r in range(start_round, final_round+1):
        W.append(shiftrows(X[-1]))
        X.append(mixcolumn(W[-1]))
    # Tweakey schedule
    #RT = [[hex(c)[2:] for c in range(16)]]
    RT = [[c for c in range(16)]] # rounds are 1-indexed
    permute = lambda X : [X[9], X[15], X[8], X[13], X[10], X[14], X[12], X[11]] + X[:8]
    for r in range(final_round):
        RT.append(permute(RT[-1]))
    return X, W, [r[:8] for r in RT[start_round:]]

def build_key_guess(RT, X, tweakey_cell, tweakey_setting):
    steps = 0
    tweakey_count = {key: 0 for key in range(16)}
    tweakey_uncertain = {key: [] for key in range(16)}
    stk_to_guess = [[-1 for _ in range(len(RT[0]))] for _ in range(len(RT))]
    for i in range(len(RT)-1, 0, -1):
        for j in range(len(RT[i])):
            if X[i][j] and RT[i][j] != tweakey_cell:
                tweakey_count[RT[i][j]] += 1
                if tweakey_count[RT[i][j]] < tweakey_setting:
                    stk_to_guess[i][j] = 0
                    steps += 1
                elif tweakey_count[RT[i][j]] < (tweakey_setting+2):
                    if tweakey_count[RT[i][j]] == (tweakey_setting+1):
                        stk_to_guess[i][j] = 1
                        k = tweakey_uncertain[RT[i][j]][-1]
                        stk_to_guess[k[0]][k[1]] = 1
                    tweakey_uncertain[RT[i][j]].append([i, j])

    for i in tweakey_uncertain.values():
        if len(i) == 1:
            k = i.pop()
            stk_to_guess[k[0]][k[1]] = 0
            steps += 1
            
    tweakey_uncertain = [i for i in tweakey_uncertain.values() if i != []]
    return stk_to_guess, tweakey_uncertain, int(steps + len(tweakey_uncertain) + 1)
        

def optimize_ps(parameter):
    # Create a MiniZinc model
    model = minizinc.Model()
    model.add_file('pso.mzn')

    # Transform Model into a instance
    gecode = minizinc.Solver.lookup("com.google.ortools.sat")
    inst = minizinc.Instance(gecode, model)

    X, _, RT = propagate_dependency(parameter['start_round'], parameter['final_round'], parameter['balanced_cell'])
    _, _, steps = build_key_guess(RT, X, parameter['tweakey_cell'], parameter['tweakey_setting'])
    print(f'Max steps: {steps}')

    inst["tweakey_setting"] = parameter['tweakey_setting']
    inst["start_round"] = parameter['start_round']
    inst["final_round"] = parameter['final_round']
    inst["tweakey_cell"] = parameter['tweakey_cell']
    inst["balanced_cell"] = parameter['balanced_cell']
    inst["input_active"] = parameter['input_active']
    if parameter['steps']:
        inst["steps"] = parameter['steps']
    else:
        inst["steps"] = steps
    inst["scale"] = parameter['scale']

    # Solve the instance
    result = inst.solve() # processes=4, timeout=timedelta(minutes=30))

    file_name = f"{parameter['tweakey_setting']}_{parameter['final_round']}_{parameter['start_round']}_{parameter['tweakey_cell']}_{parameter['balanced_cell']}_{parameter['input_active']}.json"

    log2cost = math.log2(result['total_time_cost']/(16*(parameter['final_round']+1)))+parameter['scale']
    print(f'Cost: 2^{log2cost}')
    parameter['cost'] = result['total_time_cost']/(16*(parameter['final_round']+1)) * 2**parameter['scale']

    parameter['status'] = result.status.name

    try:
        with open(file_name,"r") as f:
            old_parameter = json.load(f)
            if parameter['cost'] >= int(old_parameter['cost']):
                print("There already exists a partial sum order file with a better cost! - Not writing to file")
                return
    except IOError as e:
        pass

    parameter['keys'] = [[] for _ in range(max(map(max, result['stk'])))]

    for i, round in enumerate(result['stk']):
        for j, cell in enumerate(round):
            if cell != -1:
                k = {}
                k['r'] = i + parameter["start_round"]
                k['c'] = j
                parameter['keys'][cell-1].append(k)


    try:
        with open(file_name, 'w') as file:
            json.dump(parameter, file)
    except IOError as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find partial sum recovery steps")
    parser.add_argument('tweakey_setting', action='store', type=int, help="Specify version of Skinny used")
    parser.add_argument('final_round', action='store', type=int, help="Final round of the key recovery")
    parser.add_argument('start_round', action='store', type=int, help="Start round of the key recovery")
    parser.add_argument('tweakey_cell', action='store', type=int, help="Specify which tweakey cell is controlled by the attacker")
    parser.add_argument('balanced_cell', action='store', type=int, help="Specify the balanced cell from the output of the distinguisher")
    parser.add_argument('input_active', action='store', type=int, help="Specify how many cell are active at the input of the distinguisher")
    parser.add_argument('scale', action='store', type=int, help="Scale the time complexity, must be used since many solver only support limited data types")
    parser.add_argument('-s', '--steps', nargs='?', type=int, help="Specify the maximum number of steps, default are the involved subtweakey cells")
    parameter = parser.parse_args()

    optimize_ps(vars(parameter))
