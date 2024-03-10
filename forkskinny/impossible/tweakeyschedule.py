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

from argparse import ArgumentParser, RawTextHelpFormatter
import time
from gurobipy import read
from gurobipy import GRB
import uuid
import os


"""
Modeling the tweakey schedule of SKINNY and ForkSKINNY as a MILP problem

The TK1 which is used in the (i + 1)'th round:
tk1_i_0	    tk1_i_1	    tk1_i_2	    tk1_i_3
tk1_i_4	    tk1_i_5	    tk1_i_6	    tk1_i_7
tk1_i_8	    tk1_i_9	    tk1_i_10	tk1_i_11
tk1_i_12	tk1_i_13	tk1_i_14	tk1_i_15

The TK2 which is used in the (i + 1)'th round:
tk2_i_0	    tk2_i_1	    tk2_i_2	    tk2_i_3
tk2_i_4	    tk2_i_5	    tk2_i_6	    tk2_i_7
tk2_i_8	    tk2_i_9	    tk2_i_10	tk2_i_11
tk2_i_12	tk2_i_13	tk2_i_14	tk2_i_15

The TK3 which is used in the (i + 1)'th round:
tk3_i_0	    tk3_i_1	    tk3_i_2	    tk3_i_3
tk3_i_4	    tk3_i_5	    tk3_i_6	    tk3_i_7
tk3_i_8	    tk3_i_9	    tk3_i_10	tk3_i_11
tk3_i_12	tk3_i_13	tk3_i_14	tk3_i_15

(i + 1)'th round tweakey
tk_i_0	tk_i_1	tk_i_2	tk_i_3
tk_i_4	tk_i_5	tk_i_6	tk_i_7
 
The permuted twakey in the (i + 1)'th round:
ptk1_i_0	    ptk1_i_1	    ptk1_i_2	    ptk1_i_3
ptk1_i_4	    ptk1_i_5	    ptk1_i_6	    ptk1_i_7
ptk1_i_8	    ptk1_i_9	    ptk1_i_10	    ptk1_i_11
ptk1_i_12	    ptk1_i_13	    ptk1_i_14	    ptk1_i_15

ptk2_i_0	    ptk2_i_1	    ptk2_i_2	    ptk2_i_3
ptk2_i_4	    ptk2_i_5	    ptk2_i_6	    ptk2_i_7
ptk2_i_8	    ptk2_i_9	    ptk2_i_10	    ptk2_i_11
ptk2_i_12	    ptk2_i_13	    ptk2_i_14	    ptk2_i_15

ptk3_i_0	    ptk3_i_1	    ptk3_i_2	    ptk3_i_3
ptk3_i_4	    ptk3_i_5	    ptk3_i_6	    ptk3_i_7
ptk3_i_8	    ptk3_i_9	    ptk3_i_10	    ptk3_i_11
ptk3_i_12	    ptk3_i_13	    ptk3_i_14	    ptk3_i_15
ptk1, ptk2, and ptk3 are only used in the code, not in the MILP model
"""


class SKINNYTKSCH:
    """
    Model the tweakey schedule of SKINNY and ForkSKINNY as a MILP problem
    """

    count = 0
    def __init__(self, param):        
        self.cell_size = param['cell_size']
        self.NPT = param['NPT']
        self.RB = param['RB']
        self.RD = param['RD']
        self.RF = param['RF']
        self.RT = param['RT']
        self.Ri = param['Ri']
        self.R0 = param['R0']
        self.nonzero_tweakey_cells = param['nonzero_tweakey_cells']
        self.total_no_of_rounds = self.RT + self.R0
        self.time_limit = param['timelimit']
        self.fixed_variables = param['fixedVariables']        
        self.used_variables = [] # All of the variables used in the MILP model are stored in this list
        self.tk_permutation = [0x9, 0xf, 0x8, 0xd, 0xa, 0xe, 0xc, 0xb, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7]
        self.model_filename = str(uuid.uuid4()) + '.lp'     

    def create_state_variables(self, r, s):
        '''
        Generate the state variables
        '''

        array = [['' for _ in range(0, self.cell_size)] for _ in range(0, 16)]
        for i in range(0, 16):
            for j in range(0, self.cell_size):                
                array[i][j] = f"{s}_{r}_{i}_{j}"
                self.used_variables.append(array[i][j])
        return array

    def create_half_state_variables(self, r, s):
        '''
        Generate the variables to denote the first half of the state matrix
        '''

        array = [['' for _ in range(0, self.cell_size)] for _ in range(0, 8)]
        for i in range(0, 8):
            for j in range(0, self.cell_size):
                array[i][j] = f"{s}_{r}_{i}_{j}"
                self.used_variables.append(array[i][j])
        return array

    def flatten(self, state_array):
        '''
        Get a state array and output a flatten list
        '''

        flat_list = []
        for cell_number in range(len(state_array)):
            for bit_number in range(len(state_array[0])):
                flat_list.append(state_array[cell_number][bit_number])
        return flat_list

    def xor(self, a, b, c):
        '''
        Generate the constraints of a binary XOR
        a xor b = c can be modeled with 4 inequalities (without definition of dummy variable) by removing all impossible vectors (a, b, c)
        '''

        lp_contents = ""
        lp_contents += f"{a} + {b} - {c} >= 0\n"                
        lp_contents += f"{a} - {b} + {c} >= 0\n"
        lp_contents += f"-1 {a} + {b} + {c} >= 0\n"        
        lp_contents += f"-1 {a} - {b} - {c} >= -2\n"        
        return lp_contents

    def xor3(self, b, a2, a1, a0):
        '''
        Generate the constraints of a three-input XOR  (b = a0 xor a1 xor a2)    
        b - a2 - a1 - a0 >= -2
        - b + a2 - a1 - a0 >= -2
        - b - a2 + a1 - a0 >= -2
        b + a2 + a1 - a0 >= 0
        - b - a2 - a1 + a0 >= -2
        b + a2 - a1 + a0 >= 0
        b - a2 + a1 + a0 >= 0
        - b + a2 + a1 + a0 >= 0
        The above inequalities are derived with QuineMcCluskey algorithm
        '''

        lp_contents = ""
        lp_contents += f"{b} - {a2} - {a1} - {a0} >= -2\n"
        lp_contents += f"-1 {b} + {a2} - {a1} - {a0} >= -2\n"
        lp_contents += f"-1 {b} - {a2} + {a1} - {a0} >= -2\n"
        lp_contents += f"{b} + {a2} + {a1} - {a0} >= 0\n"
        lp_contents += f"-1 {b} - {a2} - {a1} + {a0} >= -2\n"
        lp_contents += f"{b} + {a2} - {a1} + {a0} >= 0\n"
        lp_contents += f"{b} - {a2} + {a1} + {a0} >= 0\n"
        lp_contents += f"-1 {b} + {a2} + {a1} + {a0} >= 0\n"
        return lp_contents
    
    def equality(self, x, y):
        '''
        Generate the MILP constraints modeling the equality of two bits
        '''

        lp_contents = f"{x} - {y} = 0\n"
        return lp_contents

    def permute_tweakey(self, state):
        '''
        implementing the tweak permutation (Q)
        No MILP constraint is generated by this operation
        '''
        temp = [0]*16
        for i in range(16):
            temp[i] = state[self.tk_permutation[i]]
        return temp

    def lfsr_tk2(self, a, b):
        '''
        Generate the MILP constraints corresponding to the 8-bit LFSR used through the tweakey path
        It is supposed that a, and b, are 8-bit vectors
        Seminal paper: (x7||x6||x5||x4||x3||x2||x1||x0) -> (x6||x5||x4||x3||x2||x1||x0||x7 xor x5) where x0 is the LSB
        a[0]: msb, a[7]: lsb
        (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]) -> (a[1], a[2], a[3], a[4], a[5], a[6], a[0] xor a[2]) = (b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7])
        '''

        lp_contents = ""
        for i in range(self.cell_size - 1):
            lp_contents += self.equality(a[i + 1], b[i])
        if self.cell_size == 8:
            lp_contents += self.xor(a[0], a[2], b[7])
        elif self.cell_size == 4:
            lp_contents += self.xor(a[0], a[1], b[3])
        return lp_contents

    def lfsr_tk3(self, a, b):
        '''
        Generate the MILP constraints corresponding to the 8-bit LFSR used through the tweakey path
        It is supposed that a, and b, are 8-bit vectors
        Seminal paper: (x7||x6||x5||x4||x3||x2||x1||x0) -> (x0 xor x6||x7||x6||x5||x4||x3||x2||x1) where x0 is the LSB
        a[0]: msb, a[7]: lsb
        (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]) -> (a[7] xor a[1], a[0], a[1], a[2], a[3], a[4], a[5], a[6]) = (b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7])
        '''
        
        lp_contents = ""        
        for i in range(0, self.cell_size - 1):
            lp_contents += self.equality(a[i], b[i + 1])
        if self.cell_size == 8:
            lp_contents += self.xor(a[7], a[1], b[0])
        elif self.cell_size == 4:
            lp_contents += self.xor(a[3], a[0], b[0])
        return lp_contents

    def lfsr_tk4(self, a, b):
        '''
        Generate the MILP constraints for the linear map employed in the fourth tweakey line of SKINNYe-v2
        Note that this linear map is not an LFSR!
        Reference: https://ia.cr/2020/542
        (a[0], a[1], a[2], a[3]) -> (a[2], a[3], a[0] xor a[1], a[1] xor a[2]) = (b[0], b[1], b[2], b[3])
        '''

        lp_contents = ""
        lp_contents += self.xor(a[0], a[1], b[2])
        lp_contents += self.xor(a[1], a[2], b[3])
        lp_contents += self.equality(a[2], b[0])
        lp_contents += self.equality(a[3], b[1])
        return lp_contents
    
    def tweakey_schedule(self):
        '''
        Model the difference propagation through the tweakey schedule
        '''

        lp_contents = ""
        if self.NPT >= 1:
            tk1 = self.create_state_variables(0, 'tk1')
        if self.NPT >= 2:
            tk2 = self.create_state_variables(0, 'tk2')
        if self.NPT >= 3:
            tk3 = self.create_state_variables(0, 'tk3')
        if self.NPT >= 4:
            tk4 = self.create_state_variables(0, 'tk4')
            tk34 = self.create_half_state_variables(0, 'tk34')
        tk = self.create_half_state_variables(0, 'tk')
        # model the round tweakey generation in the first round: TK = FirstHalf(TK1) xor FirstHalf(TK2) xor FirstHalf(TK3)
        for cell_number in range(8):
            for bit_number in range(self.cell_size):
                if self.NPT == 0:
                    lp_contents += self.equality(tk[cell_number][bit_number], 0) # single-tweakey differential analysis
                elif self.NPT == 1:
                    lp_contents += self.equality(tk[cell_number][bit_number], tk1[cell_number][bit_number])
                elif self.NPT == 2:
                    lp_contents += self.xor(tk[cell_number][bit_number], tk1[cell_number][bit_number], tk2[cell_number][bit_number])
                elif self.NPT == 3:
                    lp_contents += self.xor3(tk[cell_number][bit_number], tk1[cell_number][bit_number], tk2[cell_number][bit_number], tk3[cell_number][bit_number])
                elif self.NPT == 4:
                    lp_contents += self.xor(tk34[cell_number][bit_number], tk3[cell_number][bit_number], tk4[cell_number][bit_number])
                    lp_contents += self.xor3(tk[cell_number][bit_number], tk1[cell_number][bit_number], tk2[cell_number][bit_number], tk34[cell_number][bit_number])
        for r in range(1, self.total_no_of_rounds):
            if self.NPT >= 1:
                ptk1 = self.permute_tweakey(tk1)
                tk1 = self.create_state_variables(r, 'tk1')            
                # tk1 = ptk1
                for cell_number in range(16):
                    for bit_number in range(self.cell_size):
                        lp_contents += self.equality(tk1[cell_number][bit_number], ptk1[cell_number][bit_number])
            if self.NPT >= 2:
                # Apply LFSR to the the first half of ptk2
                ptk2 = self.permute_tweakey(tk2)
                tk2 = self.create_state_variables(r, 'tk2')
                for cell_number in range(8):
                    lp_contents += self.lfsr_tk2(ptk2[cell_number], tk2[cell_number])
                for cell_number in range(8, 16):
                    for bit_number in range(self.cell_size):
                        lp_contents += self.equality(ptk2[cell_number][bit_number], tk2[cell_number][bit_number])
            if self.NPT >= 3:
                # Apply LFSR to the first half of ptk3
                ptk3 = self.permute_tweakey(tk3)
                tk3 = self.create_state_variables(r, 'tk3')
                for cell_number in range(8):
                    lp_contents += self.lfsr_tk3(ptk3[cell_number], tk3[cell_number])
                for cell_number in range(8, 16):
                    for bit_number in range(self.cell_size):
                        lp_contents += self.equality(ptk3[cell_number][bit_number], tk3[cell_number][bit_number])
            if self.NPT >= 4:
                # Apply the linear map to the first half of ptk4
                ptk4 = self.permute_tweakey(tk4)
                tk4 = self.create_state_variables(r, 'tk4')
                tk34 = self.create_half_state_variables(r, 'tk34')
                for cell_number in range(8):
                    lp_contents += self.lfsr_tk4(ptk4[cell_number], tk4[cell_number])
                for cell_number in range(8, 16):
                    for bit_number in range(self.cell_size):
                        lp_contents += self.equality(ptk4[cell_number][bit_number], tk4[cell_number][bit_number])
            tk = self.create_half_state_variables(r, 'tk')
            # model the round tweakey generation: TK = FirstHalf(TK1) xor FirstHalf(TK2) xor FirstHalf(TK3) xor FirstHalf(TK4)
            for cell_number in range(8):
                for bit_number in range(self.cell_size):
                    if self.NPT == 0:
                        lp_contents += self.equality(tk[cell_number][bit_number], 0)
                    elif self.NPT == 1:
                        lp_contents += self.equality(tk[cell_number][bit_number], tk1[cell_number][bit_number])
                    elif self.NPT == 2:
                        lp_contents += self.xor(tk[cell_number][bit_number], tk1[cell_number][bit_number], tk2[cell_number][bit_number])
                    elif self.NPT == 3:
                        lp_contents += self.xor3(tk[cell_number][bit_number], tk1[cell_number][bit_number], tk2[cell_number][bit_number], tk3[cell_number][bit_number])
                    elif self.NPT == 4:
                        lp_contents += self.xor(tk34[cell_number][bit_number], tk3[cell_number][bit_number], tk4[cell_number][bit_number])
                        lp_contents += self.xor3(tk[cell_number][bit_number], tk1[cell_number][bit_number], tk2[cell_number][bit_number], tk34[cell_number][bit_number])
        return lp_contents

    def declare_fixed_variables(self):
        lp_contents = ""
        for cond in self.fixed_variables.items():            
            var = cond[0]
            val = cond[1]
            var = var.split('_')
            if len(var) == 2:                
                state_vars = self.create_state_variables(var[1], var[0])
                state_vars = self.flatten(state_vars)
                if "X" not in val:
                    state_values = list(bin(int(val, 16))[2:].zfill(self.cell_size*16))
                    for i in range(self.cell_size*16):
                        lp_contents += f"{state_vars[i]} = {state_values[i]}\n"
                else:
                    fixed_positions = [i for i in range(len(val)) if val[i] != "X"]
                    for i in fixed_positions:
                        cell_value = list(bin(int(val[i], 16))[2:].zfill(self.cell_size))
                        for j in range(self.cell_size):
                            lp_contents += f"{state_vars[i*self.cell_size + j]} = {cell_value[j]}\n"
                    
            elif len(var) == 3:
                state_vars = [f"{var[0]}_{var[1]}_{var[2]}_{i}" for i in range(self.cell_size)]
                if val != "Y":
                    state_values = list(bin(int(val, 16))[2:].zfill(self.cell_size))
                    for i in range(self.cell_size):
                        lp_contents += f"{state_vars[i]} = {state_values[i]}\n"
                elif val == "Y":
                    lp_contents += " + ".join(state_vars) + " >= 1\n"
            elif len(var) == 4:
                lp_contents += f"{cond[0]} = {cond[1]}\n"
        return lp_contents

    def declare_variables_type(self):
        '''
        Specifying variables' type in the LP file
        '''
        
        lp_contents = 'binary\n'
        self.used_variables = list(set(self.used_variables))
        for var in self.used_variables:
            lp_contents += var + '\n'            
        lp_contents += "end\n"
        return lp_contents

    def exclude_zero_solutions(self):
        lp_contents = ""
        for r in  range(self.total_no_of_rounds):
            tk = self.create_half_state_variables(r, 'tk')
            for cell in self.nonzero_tweakey_cells[r]:
                lp_contents += " + ".join([tk[cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        # if self.NPT== 1:
        #     tk1 = self.create_state_variables(0, 'tk1')
        #     for cell in self.nonzero_tweakey_cells:
        #         lp_contents += " + ".join([tk1[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        # elif self.NPT== 2:
        #     tk1 = self.create_state_variables(0, 'tk1')
        #     tk2 = self.create_state_variables(0, 'tk2')
        #     for cell in self.nonzero_tweakey_cells:
        #         lp_contents += " + ".join([tk1[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        #         lp_contents += " + ".join([tk2[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        # elif self.NPT== 3:
        #     tk1 = self.create_state_variables(0, 'tk1')
        #     tk2 = self.create_state_variables(0, 'tk2')
        #     tk3 = self.create_state_variables(0, 'tk3')
        #     for cell in self.nonzero_tweakey_cells:
        #         lp_contents += " + ".join([tk1[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        #         lp_contents += " + ".join([tk2[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        #         lp_contents += " + ".join([tk3[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        # elif self.NPT== 4:
        #     tk1 = self.create_state_variables(0, 'tk1')
        #     tk2 = self.create_state_variables(0, 'tk2')
        #     tk3 = self.create_state_variables(0, 'tk3')
        #     tk4 = self.create_state_variables(0, 'tk4')
        #     for cell in self.nonzero_tweakey_cells:
        #         lp_contents += " + ".join([tk1[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        #         lp_contents += " + ".join([tk2[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        #         lp_contents += " + ".join([tk3[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        #         lp_contents += " + ".join([tk4[0][cell][bit_number] for bit_number in range(self.cell_size)]) + " >= 1\n"
        return lp_contents

    def make_model(self):
        '''
        Generate the MILP model for tweakey schedule of SKINNY and ForkSKINNY
        '''
        
        lp_contents = ""
        print('Generating the MILP model ...')
        lp_contents += "\nsubject to\n"        
        lp_contents += self.tweakey_schedule()
        lp_contents += self.exclude_zero_solutions()
        lp_contents += self.declare_fixed_variables()
        lp_contents += self.declare_variables_type() 
        if os.path.exists(self.model_filename):
            os.remove(self.model_filename)
        with open(self.model_filename, 'w') as fileobj:
            fileobj.write(lp_contents)
        print(f"MILP model was written into {self.model_filename}\n")
    
    def compute_no_of_solutions(self):
        '''
        Compute the number of solutions

        Some general information about Gurobi:

        PoolSolutions: It controls the size of the solution pool. Changing this parameter won't affect the number of solutions that are found - 
        it simply determines how many of those are retained

        You can use the PoolSearchMode parameter to control the approach used to find solutions. In its default setting (0), the MIP search simply aims to find one optimal solution. 
        Setting the parameter to 2 causes the MIP to do a systematic search for the n best solutions. With a setting of 2, it will find the n best solutions, 
        where n is determined by the value of the PoolSolutions parameter        

        SolCount: Number of solutions found during the most recent optimization.
        
        Model status:
        LOADED	1	Model is loaded, but no solution information is available.
        OPTIMAL	2	Model was solved to optimality (subject to tolerances), and an optimal solution is available.
        INFEASIBLE	3	Model was proven to be infeasible.
        '''
        
        self.make_model()        
        self.model = read(self.model_filename)
        if self.time_limit != -1:
            self.model.Params.TIME_LIMIT = self.time_limit
        #self.model.Params.PreSolve = 0 # Activating this flag causes the performance to be decreased        
        self.model.Params.PoolSearchMode = 2
        self.model.Params.PoolSolutions = 2000000000             
        self.model.Params.OutputFlag = False    
        time_start = time.time()
        self.model.optimize()
        num_of_solutions = self.model.SolCount                
        time_end = time.time()        
        print('Elapsed time: {:.2f} seconds'.format(time_end - time_start))
        if (self.model.Status == GRB.OPTIMAL or self.model.Status == GRB.TIME_LIMIT or self.model.Status == GRB.INTERRUPTED):
            print('Number of solutions: {}'.format(num_of_solutions))        
        elif (self.model.Status == GRB.INFEASIBLE):
            print('The model is infeasible!')
        else: 
            print('Unknown Error!')
        os.remove(self.model_filename)
        return num_of_solutions
    


def loadparameters(args):
    '''
    Extract parameters from the argument list and input file
    '''

    # Load default values
    params = {"cell_size" : 4,
            "NPT" : 4,
            "RB" : 4,
            "RD" : 4,
            "RF" : 4,
            "RT" : 4,
            "Ri" : 4,
            "R0" : 4,
            "nonzero_tweakey_cells": dict(),
            "timelimit" : -1,
            "fixedVariables" : {}}

    # Check if there is an input file specified
    if args.inputfile:
        with open(args.inputfile[0], 'r') as input_file:
            doc = yaml.load(input_file, Loader=yaml.FullLoader)            
            params.update(doc)
            if "fixedVariables" in doc:
                fixed_vars = {}
                for variable in doc["fixedVariables"]:
                    fixed_vars = dict(list(fixed_vars.items()) +
                                      list(variable.items()))
                params["fixedVariables"] = fixed_vars

    # Override parameters if they are set on command line
    if args.NPT is not None:
        params["NPT"] = args.NPT
    if args.cs is not None:
        params["cell_size"] = args.cs
    if args.RD is not None:
        params["RD"] = args.RD
    if args.RB is not None:
        params["RB"] = args.RB
    if args.RF is not None:
        params["RF"] = args.RF
    if args.Ri is not None:
        params["Ri"] = args.Ri
    if args.R0 is not None:
        params["R0"] = args.R0
    if args.nonzero_tweakey_cells is not None:
        params["nonzero_tweakey_cells"] = args.nonzero_tweakey_cells
    if args.tl is not None:
        params["time_limit"] = args.tl
    return params

def main():
    '''
    Parse the arguments and start the request functionality with the provided
    parameters.
    '''
    parser = ArgumentParser(description="This tool finds the the number of solutions satisfying a differential pattern for tweakey schedule of SKINNY.",
                            formatter_class=RawTextHelpFormatter)
    
    parser.add_argument("-i", "--inputfile", nargs=1, type=str,
                        help="Input file with parameters")
    parser.add_argument("-c", "--cell_size", nargs=1, type=int,
                        help="Cell size", default=4)
    parser.add_argument("-NPT", "--NPT", nargs=1, type=int,
                        help="Number tweakey lines", default=2)
    parser.add_argument("-cs", default=4, type=int, help="Cell size (4 or 8)\n")
    parser.add_argument("-RB", default=1, type=int, help="Number of rounds for EB")
    parser.add_argument("-RD", default=1, type=int, help="Number of rounds for ED")
    parser.add_argument("-RF", default=1, type=int, help="Number of rounds for EF")
    parser.add_argument("-Ri", default=0, type=int, help="Number of rounds before the fork")
    parser.add_argument("-R0", default=0, type=int, help="Number of rounds in C0-branch")    
    parser.add_argument("-nonzero_tweakey_cells", default={}, type=dict, help="The cells of the tweakey that are not zero\n")
    parser.add_argument("-tl", default=4000, type=int, help="set a time limit for the solver in seconds\n")     

    # Parse command line arguments and construct parameter list
    args = parser.parse_args()
    params = loadparameters(args)
    skinny = SKINNYTKSCH(params)
    skinny.make_model()
    skinny.compute_no_of_solutions()

if __name__ == "__main__":
    main()
