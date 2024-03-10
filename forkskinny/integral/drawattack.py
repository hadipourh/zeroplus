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

Email: hsn.hadipour@gmail.com
"""


import sys

def trim(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

class Draw():
    """
    Draw the shape of ID attack
    """

    def __init__(self, integral_object, output_file_name="output.tex", attack_summary=""):
        self.result = integral_object.result
        self.RB = integral_object.RB
        self.RD = integral_object.RD
        self.RF = integral_object.RF
        self.RT = integral_object.RT
        self.Ri = integral_object.Ri
        self.R0 = integral_object.R0
        self.attack_summary = attack_summary
        self.variant = integral_object.variant
        self.inv_permutation = [0, 1, 2, 3, 5, 6, 7, 4, 10, 11, 8, 9, 15, 12, 13, 14]
        self.tweakey_permutation = [9, 15, 8, 13, 10, 14, 12, 11, 0, 1, 2, 3, 4, 5, 6, 7]
        self.output_file_name = output_file_name
        self.fillcolor_distinguisher = {0: "white", 1: "nonzerofixed", 2: "nonzeroany", 3: "unknown"}
        self.lazy_tweak_cells_numeric = [i for i in range(16) if self.result["contradict"][i] == 1]
        self.balanced_positions = [k for k in range(16) if not all(list(map(lambda x: x == 0, self.result["AXF"][k][0])))]
        if len(self.balanced_positions) > 2:
            raise Exception("The size of balanced_positions is greater than 2")
    
    def gen_round_tweakey_labels(self, round_number):
        """
        Generate the round tweakey labels
        """
        if round_number == 0:
            text = \
                r"""\Cell{ss00}{\texttt{0}}\Cell{ss01}{\texttt{1}}\Cell{ss02}{\texttt{2}}\Cell{ss03}{\texttt{3}}""" + \
                r"""\Cell{ss10}{\texttt{0}}\Cell{ss11}{\texttt{1}}\Cell{ss12}{\texttt{2}}\Cell{ss13}{\texttt{3}}""" + \
                r"""\Cell{ss20}{\texttt{7}}\Cell{ss21}{\texttt{4}}\Cell{ss22}{\texttt{5}}\Cell{ss23}{\texttt{6}}""" + \
                r"""\Cell{ss30}{\texttt{0}}\Cell{ss31}{\texttt{1}}\Cell{ss32}{\texttt{2}}\Cell{ss33}{\texttt{3}}"""
            return text
        round_tweakey_state = list(range(16))
        if round_number < self.Ri:
            offset = 0
        else:
            offset = self.R0
        for r in range(round_number + offset):
            round_tweakey_state = [self.tweakey_permutation[i] for i in round_tweakey_state]
        text = ""
        for i in range(8):
            text += "\Cell{{s{0}}}{{\\texttt{{{1}}}}}".format(i, hex(round_tweakey_state[i])[2:])
        return text
    
    def draw_1st_round_eb(self):
        """
        Paint first round of Eb
        """

        output = dict()    
        output["before_sb"] = ""              
        output["after_sb"] = ""
        output["after_addtk"] = ""
        output["after_sr"] = ""
        output["subtweakey"] = ""
        output["after_mix_columns"] = ""
        tkpermutation_at_round = self.result["tkpermutation_at_round"][0]
        for i in range(8):
            if tkpermutation_at_round[i] in self.lazy_tweak_cells_numeric:
                    output["subtweakey"] += "\FrameCell[filter]{{s{0}}}".format(i)
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][0]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 0)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 4)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 12)
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][1]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 1)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 5)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 13)
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][2]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 2)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 6)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 14)            
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][3]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 3)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 7)
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 15)
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][4]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 9)            
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][5]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 10)            
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][6]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 11)        
        # color = self.fillcolor_distinguisher[self.result["AXU"][0][7]]
        # output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(color, 8)            
        for i in range(16):
            if self.result["AXB"][0][i] == 1:
                output["before_sb"] += "\Fill[active]{{s{0}}}".format(i)
                output["after_sb"] += "\Fill[active]{{s{0}}}".format(i)
                output["after_addtk"] += "\Fill[active]{{s{0}}}".format(i)
                output["after_sr"] += "\Fill[active]{{s{0}}}".format(self.inv_permutation[i])
            if self.result["AXB"][1][i] == 1:
                output["after_mix_columns"] += "\Fill[active]{{s{0}}}".format(i)
        return output
            
    def draw_ed(self, r):
        """
        Paint ED
        """
        
        output = dict()
        output["before_sb"] = ""              
        output["after_sb"] = ""
        output["after_addtk"] = ""
        output["after_sr"] = ""
        output["subtweakey"] = ""
        output["after_mix_columns"] = ""
        if self.RB + r < self.Ri:
            tkpermutation_at_round = self.result["tkpermutation_at_round"][self.RB + r]
        else:
            tkpermutation_at_round = self.result["tkpermutation_at_round"][self.RB + self.R0 + r]        
        for i in range(16):
            output["before_sb"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AXU"][r][i]], i)
            output["after_sb"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AYU"][r][i]], i)
            output["after_addtk"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AYU"][r][i]], i)                
            output["after_sr"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AYU"][r][i]], self.inv_permutation[i])
            output["after_mix_columns"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AXU"][r + 1][i]], i)        
        for i in range(16):
            output["before_sb"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AXL"][r][i]], i)
            output["after_sb"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AYL"][r][i]], i)
            output["after_addtk"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AYL"][r][i]], i)
            output["after_sr"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AYL"][r][i]], self.inv_permutation[i])
            output["after_mix_columns"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[self.result["AXL"][r + 1][i]], i)
        for i in range(8):                        
            output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(self.fillcolor_distinguisher[min(self.result["AYU"][r][i], self.result["AYL"][r][i])], i)
        for i in range(8):
            if tkpermutation_at_round[i] in self.lazy_tweak_cells_numeric:
                output["subtweakey"] += "\FrameCell[filter]{{s{0}}}".format(i)
        return output

    def draw_ef(self, r):
        """
        Draw the shape of EF
        """

        output = dict()
        output["before_sb"] = ""              
        output["after_sb"] = ""
        output["after_addtk"] = ""
        output["after_sr"] = ""
        output["subtweakey"] = ""
        output["after_mix_columns"] = ""
        
        if self.RB + self.RD + r < self.Ri:
            tkpermutation_at_round = self.result["tkpermutation_at_round"][self.RB + self.RD + r]
        else:
            tkpermutation_at_round = self.result["tkpermutation_at_round"][self.RB + self.RD + r + self.R0]
        state = [self.result["AXF"][k][r] for k in self.balanced_positions]
        next_state = [self.result["AXF"][k][r + 1] for k in self.balanced_positions]       
        if len(state) == 2:
            for i in range(16):
                if state[0][i] == 1:
                    output["before_sb"] += "\TFill{{s{0}}}".format(i)
                    output["after_sb"] += "\TFill{{s{0}}}".format(i)
                    output["after_sr"] += "\TFill{{s{0}}}".format(self.inv_permutation[i])
                    if i <= 7:
                        output["subtweakey"] += "\TFill{{s{0}}}".format(i)
                if i <= 7:
                    if tkpermutation_at_round[i] in self.lazy_tweak_cells_numeric:
                        output["subtweakey"] += "\FrameCell[filter]{{s{0}}}".format(i)
                if next_state[0][i] == 1:
                    output["after_mix_columns"] += "\TFill{{s{0}}}".format(i)
            for i in range(16):
                if state[1][i] == 1:
                    output["before_sb"] += "\BFill{{s{0}}}".format(i)
                    output["after_sb"] += "\BFill{{s{0}}}".format(i)
                    output["after_sr"] += "\BFill{{s{0}}}".format(self.inv_permutation[i])
                    if i <= 7:
                        output["subtweakey"] += "\BFill{{s{0}}}".format(i)
                if i <= 7:
                    if tkpermutation_at_round[i] in self.lazy_tweak_cells_numeric:
                        output["subtweakey"] += "\FrameCell[filter]{{s{0}}}".format(i)
                if next_state[1][i] == 1:
                    output["after_mix_columns"] += "\BFill{{s{0}}}".format(i)               
        if len(state) == 1:
            for i in range(16):
                if state[0][i] == 1:
                    if r >= 1:
                        output["before_sb"] += "\Fill[active]{{s{0}}}".format(i)
                    output["after_sb"] += "\TFill{{s{0}}}".format(i)
                    output["after_sr"] += "\Fill[active]{{s{0}}}".format(self.inv_permutation[i])
                    if i <= 7:
                        output["subtweakey"] += "\Fill[active]{{s{0}}}".format(i)
                if i <= 7:
                    if tkpermutation_at_round[i] in self.lazy_tweak_cells_numeric:
                        output["subtweakey"] += "\FrameCell[filter]{{s{0}}}".format(i)
                if next_state[1][i] == 1:
                    output["after_mix_columns"] += "\Fill[active]{{s{0}}}".format(i)
        
        output["after_addtk"] = output["after_sb"]
        return output
    
    def generate_attack_shape(self):
        """
        Draw the figure of the integral attack
        """

        contents = ""
        # head lines
        contents += trim(r"""
                    \documentclass[varwidth=50cm]{standalone}
                    \usepackage{skinnyzero}
                    \usepackage{comment}
                    \begin{document}
                    %\begin{figure}
                    %\centering
                    \begin{tikzpicture}
                    \SkinnyInit{}{}{}{} % init coordinates, print labels""") + "\n\n"
        # draw EB        
        state = self.draw_1st_round_eb()
        state["subtweakey"] += self.gen_round_tweakey_labels(0)            
        contents += trim(r"""
        \SkinnyRoundEK[0]
                    {""" + state["before_sb"] + r"""} % state (input)
                    {""" + state["subtweakey"] + r"""} % etk[1] (xored AFTER mixcolumns)
                    {} % tk[2] (ignored)
                    {} % tk[3] (ignored)
                    {""" + state["after_sb"] + r"""} % state (after subcells)
                    {""" + state["after_sr"] + r"""} % state (after shiftrows)
                    {""" + state["after_mix_columns"] + r"""} % state (after mixcolumns)
        """) + "\n\n"  
        # draw ED
        for r in range(self.RD):
            state = self.draw_ed(r)
            state["subtweakey"] += self.gen_round_tweakey_labels(self.RB + r)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(self.RB + r) + """]
                          {""" + state["before_sb"] + r"""} % state (input)
                          {""" + state["subtweakey"] + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + state["after_sb"] + """} % state (after subcells)
                          {""" + state["after_addtk"] + r"""} % state (after addtweakey)
                          {""" + state["after_sr"] + r"""} % state (after shiftrows)""") + "\n\n"           
            if (r + self.RB) % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(self.RB + r + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
        # draw EF
        for r in range(self.RF):
            state = self.draw_ef(r)
            state["subtweakey"] += self.gen_round_tweakey_labels(self.RB + self.RD + r)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(self.RB + self.RD + r) + """]
                          {""" + state["before_sb"] + r"""} % state (input)
                          {""" + state["subtweakey"] + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + state["after_sb"] + """} % state (after subcells)
                          {""" + state["after_addtk"] + r"""} % state (after addtweakey)
                          {""" + state["after_sr"] + r"""} % state (after shiftrows)""") + "\n\n"
            if r == self.RF - 1:
                contents += trim(r"""\SkinnyFin[""" + str(self.RB + self.RD + r + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
            elif (self.RB + self.RD + r) % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(self.RB + self.RD + r + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"

        contents += r"""\ZeroZILegend""" + "\n"
        contents += r"""\end{tikzpicture}""" + "\n"
        contents += r"""%\caption{Integral attack on """ +  str(self.RT) +\
                    r""" rounds of SKINNY (ForkSKINNY-TK)""" + str(self.variant) + "}\n"
        contents += trim(r"""%\end{figure}""") + "\n"
        contents += trim(r"""\begin{comment}""") + "\n"
        contents += self.attack_summary
        contents += trim(r"""\end{comment}""") + "\n"
        contents += trim(r"""\end{document}""")
        with open(self.output_file_name, "w") as output_file:
            output_file.write(contents)
