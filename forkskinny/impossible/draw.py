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

    def __init__(self, id_object, output_file_name="output.tex", attack_summary=""):
        self.result = id_object.result
        self.RB = id_object.RB
        self.RD = id_object.RD
        self.RF = id_object.RF
        self.RT = id_object.RT
        self.Ri = id_object.Ri
        self.R0 = id_object.R0
        self.attack_summary = attack_summary
        if self.RB + self.RF > 0:
            self.num_of_involved_key_cells = id_object.result["KS"]
            self.CB_tot = id_object.result["CB_tot"]
            self.CF_tot = id_object.result["CF_tot"]
            self.WB = id_object.result["WB"]
            self.WF = id_object.result["WF"]
        self.variant = id_object.variant
        self.inv_permutation = [0, 1, 2, 3, 5, 6, 7, 4, 10, 11, 8, 9, 15, 12, 13, 14]
        self.tweakey_permutation = [9, 15, 8, 13, 10, 14, 12, 11, 0, 1, 2, 3, 4, 5, 6, 7]
        self.output_file_name = output_file_name
        self.fillcolor = {0: "white", 1: "nonzerofixed", 2: "nonzeroany", 3: "unknown"}

    def gen_round_tweakey_labels(self, round_number):
        """
        Generate the round tweakey labels
        """
        if round_number == 0 and (self.RB + self.RF > 0):
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
        if self.result["ASTK"][0][0] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(0)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(4)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(12)
        if self.result["ASTK"][0][1] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(1)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(5)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(13)
        if self.result["ASTK"][0][2] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(2)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(6)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(14)
        if self.result["ASTK"][0][3] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(3)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(7)
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(15)
        if self.result["ASTK"][0][4] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(9)                
        if self.result["ASTK"][0][5] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(10)
        if self.result["ASTK"][0][6] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(11)
        if self.result["ASTK"][0][7] == 1:
            output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(8)
        for i in range(16):
            if self.result["AXB"][1][i] == 1:
                output["after_mix_columns"] += "\Fill[active]{{s{0}}}".format(i)
            if self.result["KDXB"][1][i] == 1:
                output["after_mix_columns"] += "\PattCell[black]{{s{0}}}".format(i)                
            if self.result["KXB"][1][i] == 1:
                output["after_mix_columns"] += "\MarkCellN{{s{0}}}".format(i)
                output["subtweakey"] += "\MarkCellN{{s{0}}}".format(i)
        for i in range(16):
            if self.result["GXB"][1][i] == 1:
                output["after_mix_columns"] += "\MarkCellN{{s{0}}}".format(i)
                output["subtweakey"] += "\MarkCellN{{s{0}}}".format(i)
        return output

    def draw_eb(self, r):
        """
        Draw the shape of EB
        """
        
        if r == 0:
            return self.draw_1st_round_eb()
        output = dict()    
        output["before_sb"] = ""              
        output["after_sb"] = ""
        output["after_addtk"] = ""
        output["after_sr"] = ""
        output["subtweakey"] = ""
        output["after_mix_columns"] = ""
        for i in range(16):
            if self.result["AXB"][r][i] == 1:
                output["before_sb"] += "\Fill[active]{{s{0}}}".format(i)
                if self.result["IsFixedDZB"][r][i] == 1:
                    output["after_sb"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
                else:
                    output["after_sb"] += "\Fill[active]{{s{0}}}".format(i)
            if self.result["AZB"][r][i] == 1:
                if self.result["IsFixedDZB"][r][i] == 1:                    
                    output["after_addtk"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
                    output["after_sr"] += "\Fill[nonzerofixed]{{s{0}}}".format(self.inv_permutation[i])
                else:
                    output["after_addtk"] += "\Fill[active]{{s{0}}}".format(i)
                    output["after_sr"] += "\Fill[active]{{s{0}}}".format(self.inv_permutation[i])
            if self.result["AXB"][r + 1][i] == 1:
                if self.result["IsFixedDXB"][r + 1][i] == 1:
                    output["after_mix_columns"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
                else:
                    output["after_mix_columns"] += "\Fill[active]{{s{0}}}".format(i)
            if r < self.Ri:
                offset = 0
            else:
                offset = self.R0
            if self.result["ASTK"][r + offset][i] == 1 and i <= 7:
                output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
        for i in range(16):
            if self.result["KDXB"][r][i] == 1:
                output["before_sb"] += "\PattCell[black]{{s{0}}}".format(i)
            if self.result["KDXB"][r + 1][i] == 1:
                output["after_mix_columns"] += "\PattCell[black]{{s{0}}}".format(i)
            if self.result["KDZB"][r][i] == 1:
                output["after_sb"] += "\PattCell[black]{{s{0}}}".format(i)
                output["after_addtk"] += "\PattCell[black]{{s{0}}}".format(i)
                output["after_sr"] += "\PattCell[black]{{s{0}}}".format(self.inv_permutation[i])
            else:
                if self.result["FilterZB"][r][i] == 1 and self.result["AXB"][r][i] == 1:
                    output["after_sb"] += "\PattCell[black]{{s{0}}}".format(i)
        for i in range(16):
            if self.result["KXB"][r][i] == 1:
                output["before_sb"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["KXB"][r + 1][i] == 1:
                output["after_mix_columns"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["KZB"][r][i] == 1:
                output["after_sb"] += "\MarkCellN{{s{0}}}".format(i)
                if i <= 7:
                    output["subtweakey"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_addtk"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_sr"] += "\MarkCellN{{s{0}}}".format(self.inv_permutation[i])
        for i in range(16):
            if self.result["GXB"][r][i] == 1:
                output["before_sb"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["GXB"][r + 1][i] == 1:
                output["after_mix_columns"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["GZB"][r][i] == 1:
                output["after_sb"] += "\MarkCellN{{s{0}}}".format(i)
                if i <= 7:
                    output["subtweakey"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_addtk"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_sr"] += "\MarkCellN{{s{0}}}".format(self.inv_permutation[i])
        for i in range(16):
            if self.result["FilterZB"][r][i] == 1:
                output["after_sb"] += "\FrameCell[filter]{{s{0}}}".format(i)
            if self.result["FilterXB"][r + 1][i] == 1:
                output["after_mix_columns"] += "\FrameCell[filter]{{s{0}}}".format(i)                   
            if self.result["FilterXB"][r][i] == 1 and r >= 2:
                output["before_sb"] += "\FrameCell[filter]{{s{0}}}".format(i)

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
        for i in range(16):
            if self.result["AXF"][r][i] == 1:
                if self.result["IsFixedDXF"][r][i] == 1:
                    output["before_sb"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
                else:
                    output["before_sb"] += "\Fill[active]{{s{0}}}".format(i)
                output["after_sb"] += "\Fill[active]{{s{0}}}".format(i)
            if self.result["AZF"][r][i] == 1:
                if self.result["IsFixedDZF"][r][i] == 1:
                    output["after_addtk"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)                
                    output["after_sr"] += "\Fill[nonzerofixed]{{s{0}}}".format(self.inv_permutation[i])
                else:
                    output["after_addtk"] += "\Fill[active]{{s{0}}}".format(i)                
                    output["after_sr"] += "\Fill[active]{{s{0}}}".format(self.inv_permutation[i])
            if self.result["AXF"][r + 1][i] == 1:
                if self.result["IsFixedDXF"][r + 1][i] == 1:
                    output["after_mix_columns"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
                else:
                    output["after_mix_columns"] += "\Fill[active]{{s{0}}}".format(i)
            if r + self.RB + self.RD < self.Ri:
                offset = 0
            else:
                offset = self.R0
            if self.result["ASTK"][offset + r + self.RB + self.RD][i] == 1 and i <= 7:
                output["subtweakey"] += "\Fill[nonzerofixed]{{s{0}}}".format(i)
        for i in range(16):
            if self.result["KDXF"][r][i] == 1:
                output["before_sb"] += "\PattCell[black]{{s{0}}}".format(i)
            if self.result["KDXF"][r + 1][i] == 1:
                output["after_mix_columns"] += "\PattCell[black]{{s{0}}}".format(i)
            if self.result["KDZF"][r][i] == 1:
                output["after_sb"] += "\PattCell[black]{{s{0}}}".format(i)
                output["after_addtk"] += "\PattCell[black]{{s{0}}}".format(i)
                output["after_sr"] += "\PattCell[black]{{s{0}}}".format(self.inv_permutation[i])
        for i in range(16):
            if self.result["KXF"][r][i] == 1:
                output["before_sb"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["KXF"][r + 1][i] == 1:
                output["after_mix_columns"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["KZF"][r][i] == 1:
                output["after_sb"] += "\MarkCellN{{s{0}}}".format(i)
                if i <= 7:
                    output["subtweakey"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_addtk"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_sr"] += "\MarkCellN{{s{0}}}".format(self.inv_permutation[i])
        for i in range(16):
            if self.result["GXF"][r][i] == 1:
                output["before_sb"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["GXF"][r + 1][i] == 1:
                output["after_mix_columns"] += "\MarkCellN{{s{0}}}".format(i)
            if self.result["GZF"][r][i] == 1:
                output["after_sb"] += "\MarkCellN{{s{0}}}".format(i)
                if i <= 7:
                    output["subtweakey"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_addtk"] += "\MarkCellN{{s{0}}}".format(i)
                output["after_sr"] += "\MarkCellN{{s{0}}}".format(self.inv_permutation[i])
        for i in range(16):
            if self.result["FilterZF"][r][i] == 1 and r <= self.RF - 2:
                output["after_sr"] += "\FrameCell[filter]{{s{0}}}".format(self.inv_permutation[i])
            if self.result["FilterXF"][r][i] == 1:
                output["before_sb"] += "\FrameCell[filter]{{s{0}}}".format(i)
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
        if r + self.RB < self.Ri:
            offset = 0
        else:
            offset = self.R0
        for i in range(16):
            if r != 0:
                output["before_sb"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXU"][r][i]], i)
            output["after_sb"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYU"][r][i]], i)
            output["after_addtk"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AZU"][r][i]], i)                
            output["after_sr"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AZU"][r][i]], self.inv_permutation[i])
            output["after_mix_columns"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXU"][r + 1][i]], i)
            if i <= 7:
                output["subtweakey"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["ASTK"][offset + self.RB + r][i]], i)
        for i in range(16):
            if r != 0:
                output["before_sb"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXL"][r][i]], i)
            output["after_sb"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYL"][r][i]], i)
            output["after_addtk"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AZL"][r][i]], i)
            output["after_sr"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AZL"][r][i]], self.inv_permutation[i])
            output["after_mix_columns"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXL"][r + 1][i]], i)
            if i <= 7:
                output["subtweakey"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["ASTK"][offset + self.RB + r][i]], i)
        if r == 0 and (self.RB + self.RF > 0):
            for i in range(16):
                if self.result["AXB"][self.RB][i] == 1:
                    output["before_sb"] += "\Fill[active]{{s{0}}}".format(i)
                if self.result["KDXB"][self.RB][i] == 1:
                    output["before_sb"] += "\PattCell[black]{{s{0}}}".format(i)
                if self.result["KXB"][self.RB][i] == 1:
                    output["before_sb"] += "\MarkCellN{{s{0}}}".format(i)
            for i in range(16):
                if self.result["FilterXB"][self.RB][i] == 1:
                    output["before_sb"] += "\FrameCell[filter]{{s{0}}}".format(i)
            for i in range(8):
                if self.result["CB"][i + 12] == 1:
                    output["after_addtk"] += "\FrameCell[filter]{{s{0}}}".format(i)
        if r == 1 and (self.RB + self.RF > 0):
            for i in range(4):
                if self.result["CB"][i] == 1:
                    output["before_sb"] += "\FrameCell[filter]{{s{0}}}".format(i + 8)
                if self.result["CB"][i + 4] == 1:
                    output["before_sb"] += "\FrameCell[filter]{{s{0}}}".format(i + 12)
                if self.result["CB"][i + 8] == 1:
                    output["before_sb"] += "\FrameCell[filter]{{s{0}}}".format(i)
        if r == (self.RD - 1) and (self.RB + self.RF > 0):
            for i in range(8):
                if self.result["CF"][i] == 1:
                    output["after_sb"] += "\FrameCell[filter]{{s{0}}}".format(i)
            for i in range(4):
                if self.result["CF"][i + 8] == 1:
                    output["after_sr"] += "\FrameCell[filter]{{s{0}}}".format(i + 4)
                if self.result["CF"][i + 12] == 1:
                    output["after_sr"] += "\FrameCell[filter]{{s{0}}}".format(i + 8)
                if self.result["CF"][i + 16] == 1:
                    output["after_sr"] += "\FrameCell[filter]{{s{0}}}".format(i + 12)
             
        return output

    def generate_attack_shape(self):
        """
        Draw the figure of the impossible-differential attack
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
        for r in range(self.RB):
            state = self.draw_eb(r)
            state["subtweakey"] += self.gen_round_tweakey_labels(r)
            if r == 0:                
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
            else:
                contents += trim(r"""
                \SkinnyRoundTK[""" + str(r) + """]
                            {""" + state["before_sb"] + r"""} % state (input)
                            {""" + state["subtweakey"] + r"""} % tk[1]
                            {""" + r"""} % tk[2]
                            {""" + r"""} % tk[3]
                            {""" + state["after_sb"] + """} % state (after subcells)
                            {""" + state["after_addtk"] + r"""} % state (after addtweakey)
                            {""" + state["after_sr"] + r"""} % state (after shiftrows)""") + "\n\n"
            if r % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(r + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"

        # draw ED
        for r in range(0, self.RD):
            state = self.draw_ed(r)
            state["subtweakey"] += self.gen_round_tweakey_labels(r + self.RB)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(r + self.RB) + """]
                          {""" + state["before_sb"] + r"""} % state (input)
                          {""" + state["subtweakey"] + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + state["after_sb"] + """} % state (after subcells)
                          {""" + state["after_addtk"] + r"""} % state (after addtweakey)
                          {""" + state["after_sr"] + r"""} % state (after shiftrows)""") + "\n\n"
            if r == self.RD - 1 and self.RF == 0:
                contents += trim(r"""\SkinnyFin[""" + str(r + self.RB + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
            elif (r + self.RB) % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(r + self.RB + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
            
        # draw EF
        for r in range(self.RF):
            state = self.draw_ef(r)
            state["subtweakey"] += self.gen_round_tweakey_labels(r + self.RB + self.RD)
            contents += trim(r"""            
            \SkinnyRoundTK[""" + str(r + self.RB + self.RD) + """]
                          {""" + state["before_sb"] + r"""} % state (input)
                          {""" + state["subtweakey"] + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + state["after_sb"] + """} % state (after subcells)
                          {""" + state["after_addtk"] + r"""} % state (after addtweakey)
                          {""" + state["after_sr"] + r"""} % state (after shiftrows)""") + "\n\n"
            if r == self.RF - 1:
                contents += trim(r"""\SkinnyFin[""" + str(r + self.RB + self.RD + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
            elif (r + self.RB + self.RD) % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(r + self.RB + self.RD + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
        if self.RB + self.RF > 0:
            contents += r"""\ZeroIDLegend""" + "\n"
        else:
            contents += r"""\ZeroIDDistinguisherLegend""" + "\n"
        contents += r"""\end{tikzpicture}""" + "\n"
        if self.RB + self.RF > 0:
            contents += r"""%\caption{ID attack on """ +  str(self.RT) +\
                        r""" rounds of SKINNY-TK""" + str(self.variant) +\
                        r""". $|k\In \cup k\Out| = """ +  str(self.num_of_involved_key_cells) + "$" +\
                        r""". $c\In = """ + str(self.CB_tot) + "$" + \
                        r""". $c\Out = """ + str(self.CF_tot) + "$" + \
                        r""". $\Delta\In = """ + str(self.WB) + "$" + \
                        r""". $\Delta\Out = """ + str(self.WF) + "$" + "}\n"
        else:
            contents += r"""%\caption{ID distinguisher for """ +  str(self.RD) +\
                        r""" rounds of ForkSKINNY-TK""" + str(self.variant) + "}\n"
        contents += trim(r"""%\end{figure}""") + "\n"
        contents += trim(r"""\begin{comment}""") + "\n"
        contents += self.attack_summary
        contents += trim(r"""\end{comment}""") + "\n"
        contents += trim(r"""\end{document}""")
        with open(self.output_file_name, "w") as output_file:
            output_file.write(contents)
