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
import os
import uuid
import minizinc
import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
from draw import *
from pathlib import Path
from tweakeyschedule import *
line_separator = "#"*55

# Check if "OR Tools" appears in the output of "minizinc --solvers" command 
import subprocess
try:
    output = subprocess.run(['minizinc', '--solvers'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if "cp-sat" in output.stdout.decode("utf-8"):
        ortools_available = True
        print("OR Tools is available")
    else:
        ortools_available = False
        print("OR Tools is not available")
except FileNotFoundError:
    ortools_available = False

class ID:
    ID_counter = 0

    def __init__(self, params) -> None:
        ID.ID_counter += 1
        self.id = ID.ID_counter
        self.name = "ID" + str(self.id)
        self.type = "ID"

        self.variant = params["variant"]
        self.cell_size = params["cell_size"]
        self.RB = params["RB"]
        self.RD = params["RD"]
        self.RF = params["RF"]
        self.Rzero = params["Rzero"]
        self.Rone = params["Rone"]
        self.RT = self.RB + self.RD + self.RF
        self.skip_first_sbox_layer = params["sks"]
        self.is_related_tweakey = params["rt"]
        self.cp_solver_name = params["cp_solver_name"]
        self.time_limit = params["time_limit"]
        self.num_of_threads = params["num_of_threads"]
        self.output_file_name = params["output_file_name"]

        self.supported_cp_solvers = [solver_name for solver_name in minizinc.default_driver.available_solvers().keys()]
        assert(self.cp_solver_name in self.supported_cp_solvers)    
        self.cp_solver = minizinc.Solver.lookup(self.cp_solver_name)

        if self.RB + self.RF == 0:
            self.mzn_file_name = "distinguisherb.mzn"          
        else:
            self.mzn_file_name = "attack.mzn"

        self.tksch_mzn_file_name = "tweakeyschedule.mzn"

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
        self.cp_inst["RB"] = self.RB
        self.cp_inst["RD"] = self.RD
        self.cp_inst["RF"] = self.RF
        self.cp_inst["Rzero"] = self.Rzero
        self.cp_inst["Rone"] = self.Rone
        self.cp_inst["skip_first_sbox_layer"] = self.skip_first_sbox_layer
        self.cp_inst["is_related_tweakey"] = self.is_related_tweakey
        self.cp_inst["cell_size"] = self.cell_size
        self.cp_inst["variant"] = self.variant
        self.cp_inst["NPT"] = self.NPT
        self.cp_inst["GuessingThreshold1"] = self.GuessingThreshold1
        self.cp_inst["GuessingThreshold2"] = self.GuessingThreshold2
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
            params_default = {"cell_size" : self.cell_size,
                            "NPT" : self.NPT,
                            "RB" : self.RB,
                            "RD" : self.RD,
                            "RF" : self.RF,
                            "RT" : self.RT,
                            "Rzero" : self.Rzero,
                            "Rone" : self.Rone,
                            "nonzero_tweakey_cells" : dict(),
                            "timelimit" : self.time_limit,
                            "fixedVariables" : {}}
            self.nonzero_tweakey_cells = dict()            
            for r in range(self.RT + self.Rone):
                self.nonzero_tweakey_cells[r] = list()
                for cell in range(8):
                    if self.result["ASTK"][r][cell] == 0:
                        params_default["fixedVariables"][f"tk_{r}_{cell}"] = "0"
                    else:
                        self.nonzero_tweakey_cells[r].append(cell)
            params_default["nonzero_tweakey_cells"] = self.nonzero_tweakey_cells
            for i in range(16):
                if self.result["ASTK1"][i] == 0:
                    params_default["fixedVariables"][f"tk1_0_{i}"] = "0"
            if self.NPT >= 2:
                for i in range(16):
                    if self.result["ASTK2"][i] == 0:
                        params_default["fixedVariables"][f"tk2_0_{i}"] = "0"
            if self.NPT >= 3:
                for i in range(16):
                    if self.result["ASTK3"][i] == 0:
                        params_default["fixedVariables"][f"tk3_0_{i}"] = "0"
            sktksch = SKINNYTKSCH(param=params_default)
            num_of_solutions = sktksch.compute_no_of_solutions()
            attack_summary = self.print_attack_parameters()
            attack_summary += "\nNumber of distinguishers: {}\n".format(num_of_solutions)
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
        
        if self.RB + self.RF > 0:
            str_output = line_separator + "\n"
            str_output += "Attack parameters:\n"
            str_output += "#Attacked rounds      = \t{:02d}\n".format(self.RT)
            str_output += "RB + RD + RF          = \t{:02d} + {:02d} + {:02d} = {:02d}\n".format(self.RB, self.RD, self.RF, self.RT)
            # str_output += "Rzero                 = \t{:02d}\n".format(self.Rzero)
            # str_output += "Rone                  = \t{:02d}\n".format(self.Rone)
            str_output += "Variant               = \t{:02d}\n".format(self.variant)
            str_output += "Cell size             = \t{:02d}\n".format(self.cell_size)
            str_output += "data_complexity[0]    = \t{:0.02f}\n".format(self.result["data_complexity"][0])
            str_output += "data_complexity[1]    = \t{:0.02f}\n".format(self.result["data_complexity"][1])
            str_output += "data_complexity[2]    = \t{:0.02f}\n".format(self.result["data_complexity"][2])
            str_output += "data_complexity[3]    = \t{:0.02f}\n".format(self.result["data_complexity"][3])
            str_output += "g                     = \t{:03d}\n".format(self.result["g"])
            str_output += "log2(g) - 0.53        = \t{:0.02f}\n".format(self.result["log_2_minus_053_of_g"])
            str_output += "t_complexity[0]       = \t{:0.02f}\n".format(self.result["t_complexity"][0])
            str_output += "t_complexity[1]       = \t{:0.02f}\n".format(self.result["t_complexity"][1])
            str_output += "t_complexity[2]       = \t{:0.02f}\n".format(self.result["t_complexity"][2])
            str_output += "t_complexity[3]       = \t{:0.02f}\n".format(self.result["t_complexity"][3])
            str_output += line_separator + "\n"
            str_output += "#involved key cells   = \t{:02d}\n".format(self.result["KS"])
            str_output += "CB                    = \t{:02d}\n".format(self.result["CB_tot"])
            str_output += "CF                    = \t{:02d}\n".format(self.result["CF_tot"])
            str_output += "WB                    = \t{:02d}\n".format(self.result["WB"])
            str_output += "WF                    = \t{:02d}\n".format(self.result["WF"])
            str_output += "time complexity       = \t{:0.02f}\n".format(self.result["max_term"])
            if self.is_related_tweakey:
                str_output += "data_complexity       = \t{:0.02f}\n".format(self.result["t_complexity"][0] - 1)
            else:
                str_output += "data_complexity       = \t{:0.02f}\n".format(self.result["t_complexity"][0])
            str_output += "memory complexity     = \t{:0.02f}\n".format(self.result["memory_complexity"])          
            str_output += line_separator + "\n"
        else:
            contradict1, contradict2, contradict3, contradict4 = self.result["contradict1"], self.result["contradict2"], self.result["contradict3"], self.result["contradict4"]
            contradiction_locations = [x for x in range(self.RD) if contradict1[x] or contradict2[x] or contradict3[x] or contradict4[x]]
            str_output = line_separator + "\n"
            str_output = "Distinguisher parameters:\n"
            str_output += "Length of distinguisher: {:02d}\n".format(self.RD)
            str_output += "Variant:                 {:02d}\n".format(self.variant)
            str_output += "Rzero:                   {0:2d}\n".format(self.Rzero)
            str_output += "Rone:                    {0:2d}\n".format(self.Rone)
            str_output += "Contradiction happens in the following rounds: {}\n".format(contradiction_locations)
            str_output += line_separator + "\n"
        return str_output
    #############################################################################################################################################
    #############################################################################################################################################
    #############################################################################################################################################
    #   ____                      _     _    _             _   _                    _                           __   ____   _       _    _                       _       _                      
    #  / ___| ___   _   _  _ __  | |_  | |_ | |__    ___  | \ | | _   _  _ __ ___  | |__    ___  _ __    ___   / _| |  _ \ (_) ___ | |_ (_) _ __    __ _  _   _ (_) ___ | |__    ___  _ __  ___ 
    # | |    / _ \ | | | || '_ \ | __| | __|| '_ \  / _ \ |  \| || | | || '_ ` _ \ | '_ \  / _ \| '__|  / _ \ | |_  | | | || |/ __|| __|| || '_ \  / _` || | | || |/ __|| '_ \  / _ \| '__|/ __|
    # | |___| (_) || |_| || | | || |_  | |_ | | | ||  __/ | |\  || |_| || | | | | || |_) ||  __/| |    | (_) ||  _| | |_| || |\__ \| |_ | || | | || (_| || |_| || |\__ \| | | ||  __/| |   \__ \
    #  \____|\___/  \__,_||_| |_| \__|  \__||_| |_| \___| |_| \_| \__,_||_| |_| |_||_.__/  \___||_|     \___/ |_|   |____/ |_||___/ \__||_||_| |_| \__, | \__,_||_||___/|_| |_| \___||_|   |___/
    #                                                                                                                                              |___/                                        
    # Count thenumber of distinguishers
        
    def count_no_of_distinguishers(self):
        """
        Count the number of distinguishers
        """

        if self.time_limit != -1:
            time_limit = datetime.timedelta(seconds=self.time_limit)
        else:
            time_limit = None
    
        start_time = time.time()
        ####################################################################################################
        ####################################################################################################
        cp_model = minizinc.Model()
        cp_solver = minizinc.Solver.lookup('ortools')
        with open(self.tksch_mzn_file_name, "r") as cpfile:
            cp_constraints = cpfile.read() + "\n"
        for r in range(self.RT + self.Rone):
            for i in range(16):
                cp_constraints += "constraint ASTK[{:0d}, {:0d}] = {:0d};\n".format(r, i, self.result["ASTK"][r][i])                
                if self.result["DSTK"][r][i] == 0:
                    cp_constraints += "constraint DSTK[{:0d}, {:0d}] = {:0d};\n".format(r, i, self.result["DSTK"][r][i])
        for i in range(16):
            cp_constraints += "constraint ASTK1[{:0d}] = {:0d};\n".format(i, self.result["ASTK1"][i])
            if self.result["DSTK1"][i] == 0:
                cp_constraints += "constraint DSTK1[{:0d}] = {:0d};\n".format(i, self.result["DSTK1"][i])
        for r in range(self.RT + self.Rone):
            for i in range(16):
                if self.NPT == 2:
                    cp_constraints += "constraint ASTK2[{:0d}] = {:0d};\n".format(i, self.result["ASTK2"][i])          
                    if self.result["DSTK2"][0][i] == 0:
                        cp_constraints += "constraint DSTK2[0, {:0d}] = {:0d};\n".format(i, self.result["DSTK2"][0][i])      
                else:                    
                    cp_constraints += "constraint ASTK2[{:0d}] = {:0d};\n".format(i, self.result["ASTK2"][i])
                    if self.result["DSTK2"][0][i] == 0:
                        cp_constraints += "constraint DSTK2[0, {:0d}] = {:0d};\n".format(i, self.result["DSTK2"][0][i])
                    cp_constraints += "constraint ASTK3[{:0d}] = {:0d};\n".format(i, self.result["ASTK3"][i])
                    if self.result["DSTK3"][0][i] == 0:
                        cp_constraints += "constraint DSTK3[0, {:0d}] = {:0d};\n".format(i, self.result["DSTK3"][0][i])        
        random_uuid = uuid.uuid4()
        random_filename = str(random_uuid) + ".mzn"
        with open(random_filename, "w") as cpfile:
            cpfile.write(cp_constraints)
        cp_model.add_file(random_filename)        
        cp_inst = minizinc.Instance(solver=cp_solver, model=cp_model)        
        cp_inst["RB"] = self.RB
        cp_inst["RD"] = self.RD
        cp_inst["RF"] = self.RF
        cp_inst["Rzero"] = self.Rzero
        cp_inst["Rone"] = self.Rone
        cp_inst["is_related_tweakey"] = self.is_related_tweakey
        cp_inst["cell_size"] = self.cell_size
        cp_inst["variant"] = self.variant
        cp_inst["NPT"] = self.NPT
        result = cp_inst.solve(timeout=time_limit, 
                                processes=self.num_of_threads, 
                                #verbose=True,                                                                       
                                optimisation_level=2,
                                all_solutions=True)
        os.remove(random_filename)
        ####################################################################################################
        ####################################################################################################
        elapsed_time = time.time() - start_time
        print("Elapsed time to find number of distinguishers: {:0.02f} seconds".format(elapsed_time))
        if result.status == minizinc.Status.OPTIMAL_SOLUTION or result.status == minizinc.Status.SATISFIED or \
                            result.status == minizinc.Status.ALL_SOLUTIONS:            
            print(result)
        elif result.status == minizinc.Status.UNSATISFIABLE:
            print("Model is unsatisfiable")
        else:
            print("Solving process was interrupted")
    #############################################################################################################################################
    #############################################################################################################################################
    #############################################################################################################################################

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
              "cell_size" : 4,
              "RB" : 3,
              "RD" : 11,
              "RF" : 5,
              "Rzero" : 0,
              "Rone" : 0,
              "sks" : True,
              "rt" : False,
              "cp_solver_name" : "ortools",
              "num_of_threads" : 8,
              "time_limit" : None,
              "output_file_name" : "output.tex"}
    # Overwrite parameters if they are set on command line
    if args.variant is not None:
        params["variant"] = args.variant
    if args.cs is not None:
        params["cell_size"] = args.cs
    if args.RD is not None:
        params["RD"] = args.RD
    if args.RB is not None:
        params["RB"] = args.RB
    if args.RF is not None:
        params["RF"] = args.RF
    if args.Rzero is not None:
        params["Rzero"] = args.Rzero
    if args.Rone is not None:
        params["Rone"] = args.Rone
    if args.sks is not None:
        params["sks"] = args.sks
    if args.rt is not None:
        params["rt"] = args.rt
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
    parser.add_argument("-v", "--variant", default=2, type=int, help="SKINNY variant\n\
                                                                      SKINNY-n-n   (n-bit tweakey): 1, \n\
                                                                      SKINNY-n-2n (2n-bit tweakey): 2, \n\
                                                                      SKINNY-n-3n (3n-bit tweakey): 3, \n\
                                                                      SKINNY-n-4n (4n-bit tweakey): 4, \n\
                                                                      SKINNY-128-256 (128-bit key): 5, \n\
                                                                      SKINNY-128-192 (192-bit key): 6, \n\
                                                                      SKINNY-128-192 (128-bit key): 7, \n\
                                                                      SKINNY-128-288 (288-bit key): 8, \n\
                                                                      SKINNY-128-288 (128-bit key): 9  \n")
    parser.add_argument("-cs", default=4, type=int, help="Cell size (4 or 8)\n")

    parser.add_argument("-RB", default=0, type=int, help="Number of rounds for EB")
    parser.add_argument("-RD", default=15, type=int, help="Number of rounds for ED")
    parser.add_argument("-RF", default=0, type=int, help="Number of rounds for EF")
    parser.add_argument("-Rzero", default=0, type=int, help="Number of rounds before the fork. It should be zero for SKINNY.")
    parser.add_argument("-Rone", default=0, type=int, help="Number of rounds in C0-branch. It should be zero for SKINNY")

    parser.add_argument("-sks", action='store_false', help="Use this flag to move the fist S-box layer of distinguisher to key-recovery part\n")
    parser.add_argument("-rt", action='store_false', help="Use this flag for related-tweakey setting\n")
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
    id_attack = ID(params)    
    print(line_separator)
    print("Searching for an attack with the following parameters")
    print("Variant:         {}".format(params["variant"]))
    print("Cell size:       {}".format(params["cell_size"]))
    print("RB:              {}".format(params["RB"]))
    print("RD:              {}".format(params["RD"]))
    print("RF:              {}".format(params["RF"]))
    # print("Rzero:           {}".format(params["Rzero"]))
    # print("Rone:            {}".format(params["Rone"]))
    print("Skip S-box:      {}".format(params["sks"]))
    print("Related-Tweakey: {}".format(params["rt"]))
    print("CP solver:       {}".format(params["cp_solver_name"]))
    print("No. of threads:  {}".format(params["num_of_threads"]))
    print("Time limit:      {}".format(params["time_limit"]))
    print(line_separator)
    id_attack.search()
    
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

if __name__ == "__main__":
    main()
