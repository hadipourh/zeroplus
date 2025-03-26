#!/usr/env/bin python3
#-*- coding: UTF-8 -*-

"""
MIT License

Copyright (c) 2023 Hosein Hadipour

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

import time
import minizinc
import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
from drawdistinguisher import *
from pathlib import Path
line_separator = "#"*55

class IntegralDistinguisher:
    ID_counter = 0

    def __init__(self, params) -> None:
        IntegralDistinguisher.ID_counter += 1
        self.id = IntegralDistinguisher.ID_counter
        self.name = "IntegralDistinguisher" + str(self.id)
        self.type = "IntegralDistinguisher"

        self.variant = params["variant"]
        self.RD = params["RD"]
        self.Ri = params["Ri"]
        self.R0 = params["R0"]
        self.skip_first_sbox_layer = params["sks"]
        self.cp_solver_name = params["cp_solver_name"]
        self.time_limit = params["time_limit"]
        self.num_of_threads = params["num_of_threads"]
        self.output_file_name = params["output_file_name"]
        self.supported_cp_solvers = [solver_name for solver_name in minizinc.default_driver.available_solvers().keys()]
        assert(self.cp_solver_name in self.supported_cp_solvers)      
        self.cp_solver = minizinc.Solver.lookup(self.cp_solver_name)
        self.mzn_file_name = "distinguisher.mzn"              

        # SKINNY-n-n   (n-bit tweakey): 1
        # SKINNY-n-2n (2n-bit tweakey): 2
        # SKINNY-n-3n (3n-bit tweakey): 3
        # SKINNY-n-4n (4n-bit tweakey): 4
        # SKINNY-128-256 (128-bit key): 5
        # SKINNY-128-192 (192-bit key): 6  (The same as SKINNY-128-256, but the last 8 tweakey cells are set to zero)
        # SKINNY-128-192 (128-bit key): 7  (The same as SKINNY-128-256, but the last 8 tweakey cells are set to zero)
        # SKINNY-128-288 (288-bit key): 8  (The same as SKINNY-128-384, but the last 12 tweakey cells are set to zero) 
        # SKINNY-128-288 (128-bit key): 9  (The same as SKINNY-128-384, but the last 12 tweakey cells are set to zero) 
        if (self.variant == 1):
            self.NPT = 1
            self.GuessingThreshold1 = 1
            self.GuessingThreshold2 = 1
        elif (self.variant == 2):
            self.NPT = 2
            self.GuessingThreshold1 = 2
            self.GuessingThreshold2 = 2
        elif (self.variant == 3):
            self.NPT = 3
            self.GuessingThreshold1 = 3
            self.GuessingThreshold2 = 3
        elif (self.variant == 4):
            self.NPT = 4
            self.GuessingThreshold1 = 4
            self.GuessingThreshold2 = 4
        elif (self.variant == 5):
            self.NPT = 2
            self.GuessingThreshold1 = 1
            self.GuessingThreshold2 = 0
        elif (self.variant == 6):
            self.NPT = 2
            self.GuessingThreshold1 = 2
            self.GuessingThreshold2 = 1
        elif (self.variant == 7):
            self.NPT = 2
            self.GuessingThreshold1 = 1
            self.GuessingThreshold2 = 0
        elif (self.variant == 8):
            self.NPT = 3
            self.GuessingThreshold1 = 3
            self.GuessingThreshold2 = 2
        elif (self.variant == 9):
            self.NPT = 3
            self.GuessingThreshold1 = 1
            self.GuessingThreshold2 = 0
        else:
            raise Exception("Invalid variant")
                    
    #############################################################################################################################################
    #############################################################################################################################################
    #############################################################################################################################################
    #  ____          _               _    _             __  __             _        _ 
    # / ___|   ___  | |__   __ ___  | |_ | |__    ___  |  \/  |  ___    __| |  ___ | |
    # \___ \  / _ \ | |\ \ / // _ \ | __|| '_ \  / _ \ | |\/| | / _ \  / _` | / _ \| |
    #  ___) || (_) || | \ V /|  __/ | |_ | | | ||  __/ | |  | || (_) || (_| ||  __/| |
    # |____/  \___/ |_|  \_/  \___|  \__||_| |_| \___| |_|  |_| \___/  \__,_| \___||_|
        
    def search(self):
        """
        Search for a zero-correlation distinguisher optimized for key recovery
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
        self.cp_inst["RD"] = self.RD
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
    #############################################################################################################################################
    #############################################################################################################################################
    #############################################################################################################################################

    def print_attack_parameters(self):
        """
        Print attack parameters
        """                   
        str_output = line_separator + "\n"
        str_output += "Distinguisher parameters:\n"
        str_output += "Length of distinguisher: {:02d}\n".format(self.RD)
        str_output += "Variant:                 {:02d}\n".format(self.variant)
        str_output += "Ri:                      {0:2d}\n".format(self.Ri)
        str_output += "R0:                      {0:2d}\n".format(self.R0)
        lazy_tweak_cells_numeric = [i for i in range(16) if self.result["contradict"][i] == 1]             
        lazy_tweak_cells = ["TK[{:02d}] ".format(i) for i in lazy_tweak_cells_numeric]
        str_output += "Tweakey cells that are active at most {:02d} times:\n".format(self.NPT) + ", ".join(lazy_tweak_cells) + "\n"
        str_output += line_separator + "\n"
        return str_output

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
              "RD" : 11,              
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
    if args.RD is not None:
        params["RD"] = args.RD
    if args.Ri is not None:
        params["Ri"] = args.Ri
    if args.R0 is not None:
        params["R0"] = args.R0
    if args.sks is not None:
        params["sks"] = args.sks
    if args.solver is not None:
        params["cp_solver_name"] = args.solver
    if args.p is not None:
        params["num_of_threads"] = args.p
    if args.tl is not None:
        params["time_limit"] = args.tl
    if args.o is not None:
        params["output_file_name"] = args.o
    return params

def main():
    '''
    Parse the arguments and start the request functionality with the provided
    parameters
    '''

    parser = ArgumentParser(description="This tool finds the optimum impossible-differential attack",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", "--variant", default=3, type=int, help="SKINNY variant\
                                                                      SKINNY-n-n   (n-bit tweakey): 1, \n\
                                                                      SKINNY-n-2n (2n-bit tweakey): 2, \n\
                                                                      SKINNY-n-3n (3n-bit tweakey): 3, \n\
                                                                      SKINNY-n-4n (4n-bit tweakey): 4, \n\
                                                                      SKINNY-128-256 (128-bit key): 5, \n\
                                                                      SKINNY-128-192 (192-bit key): 6, \n\
                                                                      SKINNY-128-192 (128-bit key): 7, \n\
                                                                      SKINNY-128-288 (288-bit key): 8, \n\
                                                                      SKINNY-128-288 (128-bit key): 9  \n")
    
    parser.add_argument("-RD", default=13, type=int, help="Number of rounds for ED")
    parser.add_argument("-Ri", default=0, type=int, help="Number of rounds before the fork")
    parser.add_argument("-R0", default=0, type=int, help="Number of rounds in C0-branch")

    parser.add_argument("-sks", action='store_true', help="Use this flag to move the fist S-box layer of distinguisher to key-recovery part\n")    
    # Fetch available solvers from MiniZinc
    available_solvers = [solver_name for solver_name in minizinc.default_driver.available_solvers().keys()]
    parser.add_argument("-sl", "--solver", default="cp-sat", type=str,
                        choices=available_solvers,
                        help="Choose a CP solver") 
    parser.add_argument("-p", default=8, type=int, help="number of threads for solvers supporting multi-threading\n")    
    parser.add_argument("-tl", default=4000, type=int, help="set a time limit for the solver in seconds\n")
    parser.add_argument("-o", default="output.tex", type=str, help="output file including the Tikz code to generate the shape of the attack\n")

    # Parse command line arguments and construct parameter list
    args = parser.parse_args()
    params = loadparameters(args)
    integral__distinguisher = IntegralDistinguisher(params)    
    print(line_separator)
    print("Searching for an attack with the following parameters")
    print("Variant:         {}".format(params["variant"]))
    print("RD:              {}".format(params["RD"]))
    print("Ri:              {}".format(params["Ri"]))
    print("R0:              {}".format(params["R0"]))
    print("Skip S-box:      {}".format(params["sks"]))
    print("CP solver:       {}".format(params["cp_solver_name"]))
    print("No. of threads:  {}".format(params["num_of_threads"]))
    print("Time limit:      {}".format(params["time_limit"]))
    print(line_separator)
    integral__distinguisher.search()
    
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

if __name__ == "__main__":
    main()
