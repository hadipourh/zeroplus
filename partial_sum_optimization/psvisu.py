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

# code snippets taken from autopsy.py
from enum import Enum
import math
import json
import os
import contextlib
import argparse

data_inital = 0
args = None
rounds = 0
sbox_use = []

class State_name(Enum):
    X = 'X'
    STK = 'STK'
    Z = 'Z'
    W = 'W'

SORT_ORDER = {State_name.W: 0,State_name.Z: 1,State_name.STK: 2,State_name.X: 3}

class Node:

    def __init__(self, previous_node, round, state_name, index, key=-1, size=4):
        self.incoming_amount = 0
        self.incoming_count = 0
        if previous_node is not None:
            self.previous_nodes = [previous_node]
        else:
            self.previous_nodes = []
        self.round = round
        self.state_name = state_name
        self.index = index
        self.size = size
        self.key = key

    def add_previous(self, previous_node):
        self.previous_nodes.append(previous_node)

    def reset_incoming_count(self):
        self.incoming_count = self.incoming_amount

    def to_string(self):
        return f'{self.state_name.value}_{self.round}_{self.index}'


### TEX OUTPUT #########################################################

def tex_doc_start():
    with open(arg.split('.')[0] + ".tex", "w") as texfile:
        with contextlib.redirect_stdout(texfile):
            print(r"""\documentclass[multi=page, varwidth=50cm]{standalone}
\usepackage{skinnyzero}
\usepackage{tabularx}
\usepackage{booktabs}
""")
            c = len(parameter['keys']) + 1
            for i in range(c):
                # v = #(((i*240/c)+240)%360)/360
                print(f"\\definecolor{{c{i}}}{{hsb}}{{{(i//3)/(c//3)},{0.75-((i/3)%1)*.75},0.5}}")
            print(r"""\colorlet{key}{tuggreen}
\begin{document}
        """)

def tex_doc_final():
    with open(arg.split('.')[0] + ".tex", "a") as texfile:
        with contextlib.redirect_stdout(texfile):
            print(r"""
        \end{document}
        """)

def tex_table_start():
    print(r"\begin{tabularx}{21cm}[t]{@{}clc@{${}\times{}$}c@{${}={}$}cc@{${}\cdot{}$}cX@{}}")
    print(r"  \toprule")
    print(" & ".join(["Step", "Guessed", "Keys", "Data", "Memo", "Time", "Unit", "Stored Texts"]), r"\\ \midrule")

def state_to_string(state):
    if not state:
        return ""
    state = list(state)
    state.sort(key=lambda x: (-x.round, SORT_ORDER[x.state_name], x.index))
    
    to_return = f"$\\textit{{{state[0].state_name.value}}}_{{{state[0].round}}}[{state[0].index}"
    prev = state[0]
    for node in state[1:]:
        if node.state_name == prev.state_name and node.round == prev.round:
            to_return += f", {node.index}"
        else:
            to_return += f"]$; $\\textit{{{node.state_name.value}}}_{{{node.round}}}[{node.index}"
            prev = node

    return to_return + "]$"

def tex_table_row(step, guesskey, data, keys, memory, time, state, tweakey):
    global sbox_use, rounds
    # converts rnd to rnd-1!
    sformat = "{s}".format(s=step)
    kformat = state_to_string(guesskey) if guesskey else "--"
    stateformat = state_to_string(state)
    tweakeyformat = state_to_string(tweakey)
    unit = math.log2(sbox_use[step]/(16*rounds))

    Dformat = "$2^{{{d}}}$".format(d=data)
    Kformat = "$2^{{{k}}}$".format(k=keys)
    Mformat = "$2^{{{m}}}$".format(m=memory)
    Tformat = "$2^{{{t}}}$".format(t=time)
    Uformat = "$2^{{{u:2.1f}}}$".format(u=unit)
    print("  " + " & ".join([sformat, kformat, Kformat, Dformat, Mformat, Tformat, Uformat, stateformat + tweakeyformat]), r"\\")

def tex_table_hline():
    print(r"""  \midrule""")

def tex_table_final(maxkeys,maxmemo,maxtime, last_page):
    if last_page:
        print("  " + " & ".join([r"$\Sigma$", r"\multicolumn{3}{c}{}", f"$2^{{{maxmemo}}}$", f"$2^{{{maxtime:.2f}}}$", ""]), r"\\")
    print(r"  \bottomrule")
    print(r"\end{tabularx}")

def tex_skinny_start():
    print(r"""\begin{tikzpicture}[baseline=0pt]
  \SkinnyInit{}{}{}{}""")

def tex_skinny_state(state):
    if not state:
        return ""
    if args.color:
        if args.memory:
            fill = "".join([r"\Fill[" + v[0] + ("!50" if v[1] else "") + "]{ss" + k + r"}" for k, v in state.items()])
        else:
            fill = "".join([r"\Fill[" + v[0] + "]{ss" + k + r"}" for k, v in state.items()])
    else:
        if args.memory:
            fill = "".join([r"\Fill[blue" + ("!80" if v[1] else "!50") + "]{ss" + k + r"}" for k, v in state.items()])
        else:
            fill = "".join([r"\Fill{ss" + k + r"}" for k, _ in state.items()])
    
    if args.step_number:
        return fill + "".join([r"\Cell{ss" + k + r"}{\ttfamily " + str(v[2]) + r"}" for k, v in state.items()])
    else:
        return fill


def tex_skinny_stkey(state):
    if not state:
        return ""
    if args.color:
        fill = "".join([r"\Fill[" + (v[1] + "!75" if v[2] else v[1]) + "]{ss" + k + r"}" for k, v in state.items()])
    else:
        fill = "".join([r"\Fill" + ("" if v[2] else "[key]") + "{ss" + k + r"}" for k, v in state.items()])
    return fill + "".join([r"\Cell{ss" + k + r"}{\ttfamily " + hex(v[0])[2:] + r"}" for k, v in state.items()])

def tex_skinny_round(r, X_, W, Z, STK, X, final=False):
    print(r"""
  \SkinnyRoundTK[""" + str(r) + r"""] % round number should be 0-indexed
                {""" + tex_skinny_state(X) + r"""} % state (input)
                {""" + tex_skinny_stkey(STK) + r"""}{}{} % tk[1,2,3]
                {""" + tex_skinny_state(X) + r"""} % state (after subcells)
                {""" + tex_skinny_state(Z) + r"""} % state (after addtweakey)
                {""" + tex_skinny_state(W) + r"""} % state (after shiftrows)""")
    if final:
        print(r"""
  \SkinnyFin[""" + str(r+1) + r"""]
                {""" + tex_skinny_state(X_) + r"""}""")
    else:
        print(r"""
  \SkinnyNewLine[""" + str(r+1) + r"""]
                {""" + tex_skinny_state(X_) + r"""} % state (after mixcolumns)""")

def tex_skinny_final():
    print(r"""\end{tikzpicture}""")

def save_state_to_file(path, visualization_info, total_cost, last_page=True):
    with open(arg.split('.')[0] + ".tex", "a") as texfile:
        with contextlib.redirect_stdout(texfile):
            print(r"\begin{page}")
            tex_skinny_start()

            for i in range(parameter['start_round'], parameter['final_round'] + 1):
                tex_skinny_round(i, 
                                 visualization_info['X', i+1] if ('X', i+1) in visualization_info else None, 
                                 visualization_info['W', i] if ('W', i) in visualization_info else None, 
                                 visualization_info['Z', i] if ('Z', i) in visualization_info else None, 
                                 visualization_info['STK', i] if ('STK', i) in visualization_info else None, 
                                 visualization_info['X', i] if ('X', i) in visualization_info else None, 
                                 i == parameter['final_round'])
            tex_skinny_final()

            tex_table_start()
            
            i = 0
            (keys, state_, tweakey) = path[0]
            data = min(data_inital, len(state_) * 4 + len(tweakey) * 4)
            maxmemo = data
            tex_table_row(0, keys, data, 0, data, data, state_, tweakey)

            for s, (keys, state_, tweakey) in enumerate(path[1:]):
                i += len(keys) * 4
                data_n = min(data_inital, len(state_) * 4 + len(tweakey) * 4)
                maxmemo = max(maxmemo, i+data_n)
                tex_table_row(s+1, keys, data_n, i, i+data_n, i+data, state_, tweakey)
                data = data_n
            
            tex_table_final(0, maxmemo, math.log2(total_cost) if total_cost != 0 else 0, last_page)

            print(r"\end{page}")


def add_previous_node(current_nodes, round, state_name, index, previous_node, key=-1):
    if previous_node is not None:
        previous_node.incoming_amount += 1
        previous_node.reset_incoming_count()
        if current_nodes[index] is None:
            current_nodes[index] = Node(previous_node, round, state_name, index, key=key)
        else:
            current_nodes[index].add_previous(previous_node)

def build_dependency_graph_skinny(start_round, final_round, balanced_cell, tweakey_cell):
    # Round i: Xi -> STKi -> Zi -(SR)-> Wi -(MC)-> Xi+1

    shift_rows_i = [0, 1, 2, 3, 7, 4, 5, 6, 10, 11, 8, 9, 13, 14, 15, 12]

    current_nodes = [Node(None, start_round, State_name.X, c) if c == balanced_cell else None for c in range(16)]

    tweakey_nodes = []

    # Tweakey schedule
    RT = [[], [c for c in range(16)]] # rounds are 1-indexed
    permute = lambda X : [X[9], X[15], X[8], X[13], X[10], X[14], X[12], X[11]] + X[:8]
    for r in range(final_round):
        RT.append(permute(RT[-1]))


    for r in range(start_round, final_round+1):
        previous_nodes = current_nodes
        current_nodes = [None for _ in range(16)] 

        # Xi -> STKi
        for i, previous_node in enumerate(previous_nodes):
            if i < 8:
                add_previous_node(current_nodes, r, State_name.STK, i, previous_node, RT[r+1][i])
                if previous_node is not None and RT[r+1][i] == tweakey_cell:
                    tweakey_nodes.append(current_nodes[i])
            else:
                current_nodes[i] = previous_node

        previous_nodes = current_nodes
        current_nodes = [None for _ in range(16)] 

        # STKi -> Zi
        for i, previous_node in enumerate(previous_nodes):
            add_previous_node(current_nodes, r, State_name.Z, i, previous_node)

        previous_nodes = current_nodes
        current_nodes = [None for _ in range(16)] 

        # Zi -> Wi
        for i in range(16):
            add_previous_node(current_nodes, r, State_name.W, i, previous_nodes[shift_rows_i[i]])

        previous_nodes = current_nodes
        current_nodes = [None for _ in range(16)] 

        # Wi -> Xi+1
        for i, previous_node in enumerate(previous_nodes):
            if i < 4:
                add_previous_node(current_nodes, r+1, State_name.X, i+4, previous_node)
            elif i < 8:
                add_previous_node(current_nodes, r+1, State_name.X, i, previous_node)
                add_previous_node(current_nodes, r+1, State_name.X, i+4, previous_node)
                add_previous_node(current_nodes, r+1, State_name.X, i+8, previous_node)
            elif i < 12:
                add_previous_node(current_nodes, r+1, State_name.X, i-4, previous_node)
                add_previous_node(current_nodes, r+1, State_name.X, i+4, previous_node)
            else:
                add_previous_node(current_nodes, r+1, State_name.X, i-12, previous_node)
                add_previous_node(current_nodes, r+1, State_name.X, i, previous_node)
                 

    return set(filter(None, current_nodes)), tweakey_nodes


def add_visualization_info(visualization_info, node, color, current_step, memory=False, tweakey=False, start=False):
    global sbox_use
    key = (node.state_name.value, node.round)
    if key not in visualization_info:
        visualization_info[key] = {}

    if str(node.index // 4)+str(node.index%4) in visualization_info[key]:
        if memory:
            visualization_info[key][str(node.index // 4)+str(node.index%4)][1] = memory
        return

    if node.state_name == State_name.STK:
        visualization_info[key][str(node.index // 4)+str(node.index%4)] = [node.key, f'c{color}', tweakey]
    else:
        visualization_info[key][str(node.index // 4)+str(node.index%4)] = [f'c{color}', memory, current_step]

    if node.state_name == State_name.X and not start:
        sbox_use[-1] += 1


def propagate_state(state, key_guess, tweakey_nodes, tweakey_usage, visualization_info, color, current_step):
    key_candidates = set()
    min_memory = 1000
    best_state = state
    best_tweakey = tweakey_nodes
    while True:
        for node in state:
            for previous_node in node.previous_nodes:
                previous_node.reset_incoming_count()

        new_state = set()
        for node in state:
            for previous_node in reversed(node.previous_nodes):
                previous_node.incoming_count -= 1
                if previous_node.incoming_count == 0:
                    is_tweakey_node = previous_node in tweakey_nodes
                    if previous_node.key != -1 and previous_node not in key_guess and tweakey_usage[previous_node.key] > 0 and not is_tweakey_node:
                        new_state.add(node)
                        add_visualization_info(visualization_info, node, color, current_step)
                        key_candidates.add(previous_node)
                    else:
                        if is_tweakey_node:
                            tweakey_nodes.remove(previous_node)

                        new_state.add(previous_node) 
                        add_visualization_info(visualization_info, previous_node, color, current_step, False, is_tweakey_node)

                        node.previous_nodes.remove(previous_node)

                        for new_node in list(new_state):
                            if previous_node in new_node.previous_nodes:
                                new_node.previous_nodes.remove(previous_node)
                                if not new_node.previous_nodes:
                                    new_state.remove(new_node)
                else:
                    new_state.add(node)
                    add_visualization_info(visualization_info, node, color, current_step)

                if len(new_state) + len(tweakey_nodes) <= min_memory:
                    best_state = new_state
                    best_tweakey = tweakey_nodes
        
        if state == new_state or not new_state:
            for node in state:
                    add_visualization_info(visualization_info, node, color, current_step, True)
            # return state, key_candidates, tweakey_nodes
            return best_state, key_candidates, best_tweakey
        state = new_state


def find_partial_sum(state, key_candidates, tweakey_nodes, tweakey_usage, total_cost, total_number_keys, path, keys, visualization_info, current_step):
    global data_inital, sbox_use, rounds

    if not key_candidates:
        save_state_to_file(path, visualization_info, total_cost)
        return

    if args.steps:
        save_state_to_file(path, visualization_info, total_cost, False)
        for (n, _), a in visualization_info.items():
            if n != State_name.STK.value:
                for v in a.values():
                    v[1] = False


    key_guess = []
    for k in keys[0]:
        for k_c in key_candidates:
            if k_c.round == k['r'] and k_c.index == k['c']:
                key_guess.append(k_c)

    if len(keys[0]) != len(key_guess):
        print('error in input file')
        return

    data_cost = min(data_inital, len(state) * 4 + len(tweakey_nodes) * 4)
    keys_cost = total_number_keys + len(key_guess)* 4

    sbox_use.append(0)

    state, key_candidates, tweakey_nodes = propagate_state(state, key_guess, tweakey_nodes, tweakey_usage, visualization_info, len(path), current_step)

    path.append((key_guess, state, tweakey_nodes.copy()))

    for k in key_guess:
        tweakey_usage[k.key] -= 1

    cost = 2 ** (keys_cost + data_cost) * sbox_use[-1]/(16*rounds) + total_cost

    find_partial_sum(state, key_candidates, tweakey_nodes, tweakey_usage, cost, total_number_keys + len(key_guess) * 4, path, keys[1:], visualization_info, current_step+1)


def find_partial_sum_skinny(keys, tweakey_setting, final_round, start_round, tweakey_cell, balanced_cell, input_active=1):
    global data_inital, sbox_use

    current_step = 0

    tweakey_usage = {i : tweakey_setting for i in range(16)}

    data_inital = 4*(16 - input_active + tweakey_setting)

    dependency_graph, tweakey_nodes = build_dependency_graph_skinny(start_round, final_round, balanced_cell, tweakey_cell)
    
    sbox_use.append(0)
    visualization_info = {}
    for node in dependency_graph:
        add_visualization_info(visualization_info, node, 0, current_step, start=True)

    state, key_candidates, tweakey_nodes = propagate_state(dependency_graph, set(), tweakey_nodes, tweakey_usage, visualization_info, 0, current_step)

    path = []
    path.append(([], state, tweakey_nodes.copy()))
    find_partial_sum(state, key_candidates, tweakey_nodes, tweakey_usage, 0, 0, path, keys, visualization_info, current_step+1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize the partial sum recovery steps")
    parser.add_argument("-c", "--color", action="store_true", help="Use different color for every step")
    parser.add_argument("-s", "--steps", action="store_true", help="Visualize each step individually")
    parser.add_argument("-n", "--step-number", action="store_true", help="Put the step number in each cell except the stk")
    parser.add_argument("-m", "--memory", action="store_true", help="Mark which states have to be stored in memory")
    parser.add_argument("-p", "--pdf", action="store_true", help="Run latexmk and output pdf")
    parser.add_argument('input', action='store', nargs="+", help="input json file")
    args = parser.parse_args()

    for arg in args.input:
        try:
            with open(arg,"r") as f:
                parameter = json.load(f)

            tex_doc_start()
            rounds = parameter['final_round']+1
            find_partial_sum_skinny(parameter['keys'], parameter['tweakey_setting'], parameter['final_round'], parameter['start_round'], parameter['tweakey_cell'], parameter['balanced_cell'], parameter['input_active'])
            tex_doc_final()

            if args.pdf:
                    os.system("latexmk -pdf " + arg.split('.')[0] + ".tex")
                    os.system("latexmk -c")

        except IOError:
            print('error')
            pass
