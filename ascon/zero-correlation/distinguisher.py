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
"""

import logging
from pathlib import Path
from random import randint
logging.basicConfig(filename="minizinc-python.log", level=logging.DEBUG)
import time
import minizinc
import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
from drawdistinguisher import DrawDL
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
    DL_counter = 0

    def __init__(self, param) -> None:
        ID.DL_counter += 1
        self.id = ID.DL_counter
        self.name = "ID" + str(self.id)
        self.type = "ID"
        self.RD = param["RD"]
        self.cp_solver_name = param["solver"]
        self.num_of_threads = param["threads"]
        self.cp_solver = minizinc.Solver.lookup(self.cp_solver_name)
        self.time_limit = param["timelimit"]
        self.mzn_file_name = None
        self.output_file_name = param["output"]
        self.mzn_file_name = "distinguisher.mzn"
    
    #############################################################################################################################################
    #############################################################################################################################################    
    #  ____                           _        __                        ____   _       _    _                       _       _                 
    # / ___|   ___   __ _  _ __  ___ | |__    / _|  ___   _ __    __ _  |  _ \ (_) ___ | |_ (_) _ __    __ _  _   _ (_) ___ | |__    ___  _ __ 
    # \___ \  / _ \ / _` || '__|/ __|| '_ \  | |_  / _ \ | '__|  / _` | | | | || |/ __|| __|| || '_ \  / _` || | | || |/ __|| '_ \  / _ \| '__|
    #  ___) ||  __/| (_| || |  | (__ | | | | |  _|| (_) || |    | (_| | | |_| || |\__ \| |_ | || | | || (_| || |_| || |\__ \| | | ||  __/| |   
    # |____/  \___| \__,_||_|   \___||_| |_| |_|   \___/ |_|     \__,_| |____/ |_||___/ \__||_||_| |_| \__, | \__,_||_||___/|_| |_| \___||_|   
    #                                                                                                  |___/                                   
    # Search for a distinguisher using MiniZinc

    def search(self):
        """
        Search for a distinguisher
        """

        if self.time_limit != -1:
            time_limit = datetime.timedelta(seconds=self.time_limit)
        else:
            time_limit = None
    
        start_time = time.time()
        #############################################################################################################################################
        print(f"Searching for a distinguisher for {self.RD} rounds of Ascon ...")
        self.cp_model = minizinc.Model()
        self.cp_model.add_file(self.mzn_file_name)
        self.cp_inst = minizinc.Instance(solver=self.cp_solver, model=self.cp_model)
        self.cp_inst["RD"] = self.RD        
        self.cp_inst["offset"] = 0
        self.result = self.cp_inst.solve(timeout=time_limit, 
                                         processes=self.num_of_threads, 
                                         verbose=False, 
                                         debug_output=Path("./debug_output.txt",
                                         intermediate_solutions=True),
                                         random_seed=randint(0, 100),
                                         optimisation_level=2)
        #############################################################################################################################################
        elapsed_time = time.time() - start_time
        print("Time used to find a distinguisher: {:0.02f} seconds".format(elapsed_time))
        print(f"Solver status: {self.result.status}")
        if minizinc.Status.has_solution(self.result.status) or self.result.status == minizinc.Status.ERROR:
            self.attack_summary, self.upper_trail, self.lower_trail = self.parse_solution()
            print(self.attack_summary)
            self.attack_summary += "Time used to find a distinguisher: {:0.2f} seconds\n".format(elapsed_time)
            draw = DrawDL(self, output_file_name=self.output_file_name)
            draw.generate_distinguisher_shape()  
        elif self.result.status == minizinc.Status.UNSATISFIABLE:
            print("Model is unsatisfiable") 
        elif self.result.status == minizinc.Status.UNKNOWN:
            print("Unknown error!")
        else:
            print("Solving process was interrupted")

    #############################################################################################################################################
    #############################################################################################################################################
    #  ____                           _    _             ____          _         _    _               
    # |  _ \  __ _  _ __  ___   ___  | |_ | |__    ___  / ___|   ___  | | _   _ | |_ (_)  ___   _ __  
    # | |_) |/ _` || '__|/ __| / _ \ | __|| '_ \  / _ \ \___ \  / _ \ | || | | || __|| | / _ \ | '_ \ 
    # |  __/| (_| || |   \__ \|  __/ | |_ | | | ||  __/  ___) || (_) || || |_| || |_ | || (_) || | | |
    # |_|    \__,_||_|   |___/ \___|  \__||_| |_| \___| |____/  \___/ |_| \__,_| \__||_| \___/ |_| |_|
    # Parse the solution and print the distinguisher's specifications

    def parse_solution(self):
        """
        Parse the solution and print the distinguisher's specifications
        """
        
        upper_trail = {"x": [[[0 for _ in range(64)] for _ in range(5)] for _ in range(self.RD + 1)],
                       "y": [[[0 for _ in range(64)] for _ in range(5)] for _ in range(self.RD)]}
        for r in range(self.RD + 1):
            for row in range(5):
                upper_trail["x"][r][row] = self.result["xu"][r][row]
                if r < self.RD:
                    upper_trail["y"][r][row] = self.result["yu"][r][row]
        lower_trail = {"x": [[[0 for _ in range(64)] for _ in range(5)] for _ in range(self.RD + 1)],
                       "y": [[[0 for _ in range(64)] for _ in range(5)] for _ in range(self.RD)]}
        for r in range(self.RD + 1):
            for row in range(5):
                lower_trail["x"][r][row] = self.result["xl"][r][row]
                if r < self.RD:
                    lower_trail["y"][r][row] = self.result["yl"][r][row]
        input_diff = ""
        for row in range(5):
            input_diff += f"input[{row}] = " + "".join(list(map(str, self.result["xu"][0][row]))).replace("-1", "?") + ";\n"
        output_mask = ""
        for row in range(5):
            output_mask += f"output[{row}] = " + "".join(list(map(str, self.result["xl"][self.RD][row]))).replace("-1", "?") + ";\n"
        
        num_non_fixed_input_bits = self.result["num_non_fixed_input_bits"]
        num_non_fixed_output_bits = self.result["num_non_fixed_output_bits"]

        attack_summary = f"Attack summary:\n"
        attack_summary += f"Setting: RD: {self.RD}\n"
        attack_summary += "#"*50 + "\n"
        attack_summary += f"input.: \n{input_diff}"
        attack_summary += "#"*50 + "\n"
        attack_summary += f"output: \n{output_mask}"
        attack_summary += "#"*50 + "\n"
        attack_summary += f"Number of non-fixed input bits: {num_non_fixed_input_bits}\n"
        attack_summary += f"Number of non-fixed output bits: {num_non_fixed_output_bits}\n"        
        return attack_summary, upper_trail, lower_trail

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
    params = {"RD": 1,              
              "tl"  : -1,
              "solver"  : "ortools",
              "num_of_threads" : 8,
              "output"  : "output.tex"}

    # Override parameters if they are set on command line
    if args.RD is not None:
        params["RD"] = args.RD    
    if args.timelimit is not None:
        params["timelimit"] = args.timelimit
    if args.solver is not None:
        params["solver"] = args.solver
    if args.p is not None:
        params["threads"] = args.p
    if args.output is not None:
        params["output"] = args.output

    return params

def main():
    '''
    Parse the arguments and start the request functionality with the provided
    parameters.
    '''
    
    parser = ArgumentParser(description="This tool finds the best zero-correlation distinguisher",
                            formatter_class=RawTextHelpFormatter)
    
    parser.add_argument("-RD", type=int, default=5, help="Number of rounds for distinguisher")    
    parser.add_argument("-tl", "--timelimit", type=int, default=14400, help="Time limit in seconds")
    # Fetch available solvers from MiniZinc
    available_solvers = [solver_name for solver_name in minizinc.default_driver.available_solvers().keys()]
    parser.add_argument("-sl", "--solver", default="cp-sat", type=str,
                        choices=available_solvers,
                        help="Choose a CP solver") 
    parser.add_argument("-p", default=8, type=int, help="number of threads for solvers supporting multi-threading\n")    
    parser.add_argument("-o", "--output", default="output.tex", type=str, help="Output file name")

    # Parse command line arguments and construct parameter list
    args = parser.parse_args()
    params = loadparameters(args)
    dld = ID(params)
    dld.search()

if __name__ == "__main__":
    main()
