#!/usr/env/bin python3
#-*- coding: UTF-8 -*-

"""
MIT License

Copyright (c) 2022 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

email: hsn.hadipour@gmail.com
"""

import itertools
import time
import minizinc
import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from drawattack import *
line_separator = "#"*55

class IntegralAttack:
    Integral_counter = 0

    def __init__(self, params) -> None:
        IntegralAttack.Integral_counter += 1
        self.id = IntegralAttack.Integral_counter
        self.name = "IntegralAttack" + str(self.id)
        self.type = "IntegralAttack"

        self.variant = params["variant"]
        self.RB = params["RB"]
        self.RD = params["RD"]
        self.RF = params["RF"]
        self.RT = self.RB + self.RD + self.RF
        self.Ri = params["Ri"]
        self.R0 = params["R0"]
        self.skip_first_sbox_layer = params["sks"]
        self.cp_solver_name = params["cp_solver_name"]
        self.time_limit = params["time_limit"]
        self.num_of_threads = params["num_of_threads"]
        self.output_file_name = params["output_file_name"]

        self.supported_cp_solvers = ['gecode', 'chuffed', 'cbc', 'gurobi',
                                     'picat', 'scip', 'choco', 'ortools']
        assert(self.cp_solver_name in self.supported_cp_solvers)
        ##################################################
        # Use this block if you install Or-Tools bundeled with MiniZinc
        if self.cp_solver_name == "ortools":
            self.cp_solver_name = "com.google.ortools.sat"
        ##################################################        
        self.cp_solver = minizinc.Solver.lookup(self.cp_solver_name)
        self.mzn_file_name = "attack.mzn"

        # SKINNY-n-n   (n-bit tweakey): 1
        # SKINNY-n-2n (2n-bit tweakey): 2
        # SKINNY-n-3n (3n-bit tweakey): 3
        # SKINNY-n-4n (4n-bit tweakey): 4
        if (self.variant == 1):
            self.NPT = 1
        elif (self.variant == 2):
            self.NPT = 2
        elif (self.variant == 3):
            self.NPT = 3
        elif (self.variant == 4):
            self.NPT = 4
        else:
            raise Exception("Invalid variant")
    
    def search(self):
        """
        Search for an integral distinguisher optimized for key recovery
        """

        if self.time_limit != -1:
            time_limit = datetime.timedelta(seconds=self.time_limit)
        else:
            time_limit = None
    
        start_time = time.time()
        ####################################################################################################
        ####################################################################################################
        self.cp_model = minizinc.Model()
        self.cp_model.add_file(self.mzn_file_name)
        self.cp_inst = minizinc.Instance(solver=self.cp_solver, model=self.cp_model)
        self.cp_inst["RB"] = self.RB
        self.cp_inst["RD"] = self.RD
        self.cp_inst["RF"] = self.RF        
        self.cp_inst["Ri"] = self.Ri
        self.cp_inst["R0"] = self.R0
        self.cp_inst["skip_first_sbox_layer"] = self.skip_first_sbox_layer
        self.cp_inst["variant"] = self.variant
        self.cp_inst["NPT"] = self.NPT
        self.result = self.cp_inst.solve(timeout=time_limit, 
                                         processes=self.num_of_threads, 
                                         #verbose=True, 
                                         debug_output=Path("./debug_output.txt", intermediate_solutions=True),                                         
                                         optimisation_level=2)
        ####################################################################################################
        ####################################################################################################
        elapsed_time = time.time() - start_time
        print("Elapsed time: {:0.02f} seconds".format(elapsed_time))


        if self.result.status == minizinc.Status.OPTIMAL_SOLUTION or self.result.status == minizinc.Status.SATISFIED or \
                            self.result.status == minizinc.Status.ALL_SOLUTIONS:
            attack_summary = self.print_attack_parameters()
            attack_summary += line_separator + "\n"
            print(attack_summary)
            draw = Draw(self, output_file_name=self.output_file_name, attack_summary=attack_summary)         
            draw.generate_attack_shape()  
        elif self.result.status == minizinc.Status.UNSATISFIABLE:
            print("Model is unsatisfiable")
        else:
            print("Solving process was interrupted")
        
    def print_attack_parameters(self):
        """
        Print attack parameters
        """                   

        str_output = line_separator + "\n"
        str_output += "Distinguisher parameters:\n"
        str_output += "Length of distinguisher: {:02d}\n".format(self.RD)
        str_output += "Variant:                 {:02d}\n".format(self.variant)
        str_output += "Ri:                   {0:2d}\n".format(self.Ri)
        str_output += "R0:                    {0:2d}\n".format(self.R0)
        lazy_tweak_cells_numeric = [i for i in range(16) if self.result["contradict"][i] == 1]
        lazy_tweak_cells = ["TK[{:02d}] ".format(i) for i in lazy_tweak_cells_numeric]
        str_output += "Tweakey cells that are active at most {:02d} times:\n".format(self.NPT) + ", ".join(lazy_tweak_cells) + "\n"
        str_output += "Max number of involved tweakey cells in key recovery: {:02d}".format(self.result["max_key_entropy_sum"]) + "\n"
        str_output += line_separator + "\n"
        return str_output
    
    def paint_eb(self, state, permutation_r):
        """
        Paint Eb
        """

        before_sb = ""
        after_sb = ""
        after_addtk = ""
        after_sr = ""
        subtweakey = ""
                            
        for i, j in itertools.product(range(0, 4), range(0, 4)):
            if state[i][j] == 1:
                before_sb += "\Fill[active]{{ss{0}{1}}}".format(i, j)
                after_sr += "\Fill[active]{{ss{0}{1}}}".format(i, (j + i)%4)
                if i <= 1:
                    subtweakey += "\Fill[active]{{ss{0}{1}}}".format(i, j)
                    if permutation_r[4*i + j] in self.lazy_tweak_cells_numeric:
                        subtweakey += "\Fill[lazy, opacity=0.70]{{ss{0}{1}}}".format(i, j)
        after_sb = before_sb
        after_addtk = after_sb
        return before_sb, after_sb, after_addtk, after_sr, subtweakey
    
    def paint_ef(self, state, permutation_r):
        """
        Paint Ef
        """

        before_sb = ""
        after_sb = ""
        after_addtk = ""
        after_sr = ""
        subtweakey = ""
        
        if len(state) == 2:
            for i, j in itertools.product(range(0, 4), range(0, 4)):
                if state[0][i][j] == 1:
                    before_sb += "\TFill{{ss{0}{1}}}".format(i, j)
                    after_sr += "\TFill{{ss{0}{1}}}".format(i, (j + i)%4)
                    if i <= 1:
                        subtweakey += "\TFill{{ss{0}{1}}}".format(i, j)
                        if permutation_r[4*i + j] in self.lazy_tweak_cells_numeric:
                            subtweakey += "\Fill[lazy, opacity=0.70]{{ss{0}{1}}}".format(i, j)                        
            for i, j in itertools.product(range(0, 4), range(0, 4)):
                if state[1][i][j] == 1:
                    before_sb += "\BFill{{ss{0}{1}}}".format(i, j)
                    after_sr += "\BFill{{ss{0}{1}}}".format(i, (j + i)%4)
                    if i <= 1:
                        subtweakey += "\BFill{{ss{0}{1}}}".format(i, j)
                        if permutation_r[4*i + j] in self.lazy_tweak_cells_numeric:
                            subtweakey += "\Fill[lazy, opacity=0.70]{{ss{0}{1}}}".format(i, j)
        else:
            for i, j in itertools.product(range(0, 4), range(0, 4)):
                if state[0][i][j] == 1:
                    before_sb += "\Fill[blue!55]{{ss{0}{1}}}".format(i, j)
                    after_sr += "\Fill[blue!55]{{ss{0}{1}}}".format(i, (j + i)%4)
                    if i <= 1:
                        subtweakey += "\Fill[blue!55]{{ss{0}{1}}}".format(i, j)
                        if permutation_r[4*i + j] in self.lazy_tweak_cells_numeric:
                            subtweakey += "\Fill[lazy, opacity=0.70]{{ss{0}{1}}}".format(i, j)
                        
        after_sb = before_sb
        after_addtk = after_sb
        return before_sb, after_sb, after_addtk, after_sr, subtweakey
    
    @staticmethod
    def gen_subtwaek_text(permutation_r):
        """
        Generate the text content of subtweakey
        """
        
        text = ""
        for i, j in itertools.product(range(2), range(4)):
            text += "\Cell{{ss{0}{1}}}{{\\texttt{{{2}}}}}".format(i, j, hex(permutation_r[4*i + j])[2:])
        return text

    @staticmethod
    def paint_e1_e2(state_before_sb, state_after_sb):
        """
        Paint E1
        """

        before_sb = ""
        after_sb = ""
        after_addtk = ""
        after_sr = ""
        subtweakey = ""

        for i in range(4):
            for j in range(4):
                ######## paint before sb ########
                if state_before_sb[i][j] == 1:
                    before_sb += "\Fill[nonzerofixed]{{ss{0}{1}}}".format(i, j)
                elif state_before_sb[i][j] == 2:
                    before_sb += "\Fill[nonzeroany]{{ss{0}{1}}}".format(i, j)
                elif state_before_sb[i][j] == 3:
                    before_sb += "\Fill[unknown]{{ss{0}{1}}}".format(i, j)
                ######## paint after sb ########
                if state_after_sb[i][j] == 1:
                    after_sb += "\Fill[nonzerofixed]{{ss{0}{1}}}".format(i, j)
                    after_sr += "\Fill[nonzerofixed]{{ss{0}{1}}}".format(i, (j + i)%4)
                elif state_after_sb[i][j] == 2:
                    after_sb += "\Fill[nonzeroany]{{ss{0}{1}}}".format(i, j)
                    after_sr += "\Fill[nonzeroany]{{ss{0}{1}}}".format(i, (j + i)%4)
                elif state_after_sb[i][j] == 3:
                    after_sb += "\Fill[unknown]{{ss{0}{1}}}".format(i, j)
                    after_sr += "\Fill[unknown]{{ss{0}{1}}}".format(i, (j + i)%4)
            if i <= 1:
                subtweakey += after_sb   
        after_addtk = after_sb
        return before_sb, after_sb, after_addtk, after_sr, subtweakey

    def draw_graph(self):
        """
        Draw the figure of the IntegralAttack distinguisher
        """

        contents = ""
        # head lines
        contents += trim(r"""
                    % \documentclass[11pt,a3paper,parskip=half]{scrartcl}
                    \documentclass[varwidth=50cm]{standalone}
                    % \usepackage[margin=1cm]{geometry}
                    \usepackage{skinny}
                    \usepackage{tugcolors}

                    \newcommand{\TFill}[2][blue!55]{\fill[#1] (#2) ++(-.5,.5) -- +(0,-1) -- +(1,0) -- cycle;}
                    \newcommand{\BFill}[2][green!60]{\fill[#1] (#2) ++(.5,-.5) -- +(0,1) -- +(-1,0) -- cycle;}

                    \begin{document}

                    \TKthreefalse % true: show 3 tweakey states / false: show 1 tweakey state
                    \substeptrue  % true: show state after each substep / false: show only 2 state per round
                    \colorlet{nonzerofixed}{tugyellow}
                    \colorlet{nonzeroany}{tugred}
                    \colorlet{unknown}{tugblue}
                    \colorlet{active}{tuggreen}
                    \colorlet{lazy}{gray}""" + "\n")
        contents += trim(r"""
                    % \begin{figure}
                    % \centering
                    \begin{tikzpicture}
                    \SkinnyInit{}{}{}{} % init coordinates, print labels""") + "\n\n"
        # draw Eb
        for r in range(self.RB):
            state = self.result["backward_eb_mask_x"][r]
            subtweak_state = self.result["permutation_per_round"][r]       
            before_sb, after_sb, after_addtk, after_sr, subtweakey = self.paint_eb(state, subtweak_state)                        
            subtweakey += self.gen_subtwaek_text(subtweak_state)
            next_state = self.result["backward_eb_mask_x"][r + 1]
            after_mixcol, _, _, _, _ = self.paint_eb(next_state, subtweak_state)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(r) + r"""]
                          {""" + before_sb + r"""} % state (input)
                          {""" + subtweakey + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + after_sb + """} % state (after subcells)
                          {""" + after_addtk + r"""} % state (after addtweakey)
                          {""" + after_sr + r"""} % state (after shiftrows)""") + "\n\n"
            if r % 2 == 1:
                contents += r"""\SkinnyNewLine[""" + str(r + 1) + r"""]{""" + after_mixcol + r"""} % state (after mixcols)""" + "\n"                
        # draw E1
        for r in range(self.RU):
            state_before_sb = self.result["forward_mask_x"][r]
            state_after_sb = self.result["forward_mask_sbx"][r]
            before_sb, after_sb, after_addtk, after_sr, subtweakey = self.paint_e1_e2(state_before_sb, state_after_sb)
            subtweak_state = self.result["permutation_per_round"][r + self.RB]
            subtweakey += self.gen_subtwaek_text(subtweak_state)
            next_state_before_sb = self.result["forward_mask_x"][r + 1]
            if r == self.RU - 1:
                next_state_after_sb = next_state_before_sb
            else:
                next_state_after_sb = self.result["forward_mask_sbx"][r + 1]
            after_mixcol, _, _, _, _ = self.paint_e1_e2(next_state_before_sb, next_state_after_sb)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(self.RB + r) + r"""]
                          {""" + before_sb + r"""} % state (input)
                          {""" + subtweakey + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + after_sb + """} % state (after subcells)
                          {""" + after_addtk + r"""} % state (after addtweakey)
                          {""" + after_sr + r"""} % state (after shiftrows)""") + "\n\n"
            if r == self.RU - 1:
                contents += r"""\SkinnyFin[""" + str(self.RB + r + 1) + r"""]{""" + after_mixcol + r"""} % state (after mixcols)""" + "\n\n"                
            elif (r + self.RB) % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(self.RB + r + 1) + r"""]{""") + after_mixcol + r"""} % state (after mixcols)""" + "\n"                
        
        contents += r"""\end{tikzpicture}""" + "\n" + r"""\bigskip""" + "\n\n" + r"""\begin{tikzpicture}""" + "\n\n"
        contents += r"""\SkinnyInit{}{}{}{}""" + "\n\n"
        # draw E2
        for r in range(self.RL):
            state_before_sb = self.result["backward_mask_x"][r]
            state_after_sb = self.result["backward_mask_sbx"][r]
            before_sb, after_sb, after_addtk, after_sr, subtweakey = self.paint_e1_e2(state_before_sb, state_after_sb)
            subtweak_state = self.result["permutation_per_round"][r + self.RB + self.RU]
            subtweakey += self.gen_subtwaek_text(subtweak_state)
            next_state_before_sb = self.result["backward_mask_x"][r + 1]
            if r == self.RL - 1:
                next_state_after_sb = next_state_before_sb
            else:
                next_state_after_sb = self.result["backward_mask_sbx"][r + 1]
            after_mixcol, _, _, _, _ = self.paint_e1_e2(next_state_before_sb, next_state_after_sb)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(self.RB + self.RU + r) + r"""]
                          {""" + before_sb + r"""} % state (input)
                          {""" + subtweakey + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + after_sb + """} % state (after subcells)
                          {""" + after_addtk + r"""} % state (after addtweakey)
                          {""" + after_sr + r"""} % state (after shiftrows)""") + "\n\n"
            if (r + self.RB + self.RU) % 2 == 1:                
                if r == self.RL - 1 and self.RB + self.RF == 0:
                        contents += trim(r"""\SkinnyFin[""" + str(self.RB + self.RU + r + 1) + r"""]{""") + after_mixcol + r"""} % state (after mixcols)""" + "\n\n"
                else:
                    contents += trim(r"""\SkinnyNewLine[""" + str(self.RB + self.RU + r + 1) + r"""]{""") + after_mixcol + r"""} % state (after mixcols)""" + "\n"                
        # draw Ef
        # detect the balanced positions
        # check if all elements of a two dimensional array are zero
        
        balanced_positions = [k for k in range(16) if not self.is_zero_state(self.result["forward_ef_mask_x"][k][0])]
        # check if the size of balanced_positions is at most 2 otherwise raise and error
        if len(balanced_positions) > 2:
            raise Exception("The size of balanced_positions is greater than 2")
        for r in range(self.RF):
            state = [self.result["forward_ef_mask_x"][k][r] for k in balanced_positions]
            subtweak_state = self.result["permutation_per_round"][r + self.RB + self.RU + self.RL]        
            before_sb, after_sb, after_addtk, after_sr, subtweakey = self.paint_ef(state, subtweak_state)            
            subtweakey += self.gen_subtwaek_text(subtweak_state)
            next_state = [self.result["forward_ef_mask_x"][k][r + 1] for k in balanced_positions]
            after_mixcol, _, _, _, _ = self.paint_ef(next_state, subtweak_state)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(self.RB + self.RU + self.RL + r) + r"""]
                          {""" + before_sb + r"""} % state (input)
                          {""" + subtweakey + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + after_sb + """} % state (after subcells)
                          {""" + after_addtk + r"""} % state (after addtweakey)
                          {""" + after_sr + r"""} % state (after shiftrows)""") + "\n\n"
            if (r + self.RB + self.RU + self.RL) % 2 == 1:                
                if r != self.RF - 1:
                    contents += r"""\SkinnyNewLine["""+ str(self.RB + self.RU + self.RL + r + 1) + r"""]{""" + after_mixcol + r"""} % state (after mixcols)""" + "\n"
                else:
                    contents += r"""\SkinnyFin["""+ str(self.RB + self.RU + self.RL + r + 1) + r"""]{""" + after_mixcol + r"""} % state (after mixcols)""" + "\n\n"
            else:
              contents += trim(r"""\SkinnyFin[""" + str(self.RB + self.RU + self.RL + r + 1) + r"""]{""") + after_mixcol + r"""} % state (after mixcols)""" + "\n\n"         
        # end lines
        contents += r"""\end{tikzpicture}""" + "\n"
        contents += r"""%\caption{IntegralAttack/Integral attack on """ +  str(self.num_of_attacked_rounds) +\
                    r""" rounds of """ + self.target_variant +\
                    r""". Twakeys cells that are active at most """ + str(self.NPT) + " times: " + ", ".join(self.lazy_tweak_cells) + \
                    r""". \#Involved key cells (maximum): """ +  str(self.max_num_of_involved_key_cells) + "}\n"
        contents += trim(r"""%\end{figure}
                             \end{document}""")
        with open(self.output_file_name, "w") as output_file:
            output_file.write(contents)

#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#  _   _                    ___         _                __                   
# | | | | ___   ___  _ __  |_ _| _ __  | |_  ___  _ __  / _|  __ _   ___  ___ 
# | | | |/ __| / _ \| '__|  | | | '_ \ | __|/ _ \| '__|| |_  / _` | / __|/ _ \
# | |_| |\__ \|  __/| |     | | | | | || |_|  __/| |   |  _|| (_| || (__|  __/
#  \___/ |___/ \___||_|    |___||_| |_| \__|\___||_|   |_|   \__,_| \___|\___|
    
def loadparameters(args):
    '''
    Extract parameters from the argument list and input file
    '''

    # Load default values
    params = {"variant" : 2,
              "RB": 1,
              "RD" : 11,
              "RF": 6,
              "Ri" : 0,
              "R0" : 0,
              "sks" : True,              
              "cp_solver_name" : "ortools",
              "num_of_threads" : 8,
              "time_limit" : None,
              "output_file_name" : "output.tex"}
    # Overwrite parameters if they are set on command line
    if args.variant is not None:
        params["variant"] = args.variant
    if args.nroundsEB is not None:
        params["RB"] = args.nroundsEB
    if args.nroundsED is not None:
        params["RD"] = args.nroundsED
    if args.nroundsEF is not None:
        params["RF"] = args.nroundsEF
    if args.Ri is not None:
        params["Ri"] = args.Ri
    if args.R0 is not None:
        params["R0"] = args.R0
    if args.sks is not None:
        params["sks"] = args.sks
    if args.solver is not None:
        params["cp_solver_name"] = args.solver
    if args.processes is not None:
        params["num_of_threads"] = args.processes
    if args.timelimit is not None:
        params["time_limit"] = args.timelimit
    if args.outputfile is not None:
        params["output_file_name"] = args.outputfile
    return params

def main():
    '''
    Parse the arguments and start the request functionality with the provided
    parameters
    '''

    parser = ArgumentParser(description="This tool finds a nearly optimum integral attack for SKINNY",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", "--variant", default=3, type=int, help="choose the SKINNY variant\n")
    parser.add_argument("-RB", "--nroundsEB", default=1, type=int, help="choose the number of rounds for EB. It should be 1 for SKINNY and ForkSKINNY.\n")
    parser.add_argument("-RD", "--nroundsED", default=17, type=int, help="choose the number of rounds for ED\n")
    parser.add_argument("-RF", "--nroundsEF", default=9, type=int, help="choose the number of rounds for EF\n")
    parser.add_argument("-Ri", default=9, type=int, help="Number of rounds before the fork")
    parser.add_argument("-R0", default=23, type=int, help="Number of rounds in C0-branch")
    parser.add_argument("-sks", action='store_true', help="Use this flag to move the fist S-box layer of distinguisher to key-recovery part\n")   

    parser.add_argument("-sl", "--solver", default="ortools", type=str,
                        choices=['gecode', 'chuffed', 'coin-bc', 'gurobi', 'picat', 'scip', 'choco', 'ortools'],
                        help="choose a cp solver\n")
    parser.add_argument("-p", "--processes", default=8, type=int, help="number of threads for solvers supporting multi-threading\n")
    parser.add_argument("-tl", "--timelimit", default=3600, type=int, help="set a time limit for the solver in seconds\n")
    parser.add_argument("-o", "--outputfile", default="output.tex", type=str, help="output file including the Tikz code to generate the figure of the attack\n")
    
    # Parse command line arguments and construct parameter list
    args = parser.parse_args()
    params = loadparameters(args)
    integral_attack = IntegralAttack(params)    
    print(line_separator)
    print("Searching for an attack with the following parameters")
    print("Variant:         {}".format(params["variant"]))
    print("RB:              {}".format(params["RB"]))
    print("RD:              {}".format(params["RD"]))
    print("RF:              {}".format(params["RF"]))
    print("Ri:              {}".format(params["Ri"]))
    print("R0:              {}".format(params["R0"]))
    print("Skip S-box:      {}".format(params["sks"]))
    print("CP solver:       {}".format(params["cp_solver_name"]))
    print("No. of threads:  {}".format(params["num_of_threads"]))
    print("Time limit:      {}".format(params["time_limit"]))
    print(line_separator)
    integral_attack.search()    

if __name__ == '__main__':
    main()