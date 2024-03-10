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
        self.RD = integral_object.RD
        self.Ri = integral_object.Ri
        self.R0 = integral_object.R0
        self.attack_summary = attack_summary
        self.variant = integral_object.variant
        self.inv_permutation = [0, 1, 2, 3, 5, 6, 7, 4, 10, 11, 8, 9, 15, 12, 13, 14]
        self.tweakey_permutation = [9, 15, 8, 13, 10, 14, 12, 11, 0, 1, 2, 3, 4, 5, 6, 7]
        self.output_file_name = output_file_name
        self.fillcolor = {0: "white", 1: "nonzerofixed", 2: "nonzeroany", 3: "unknown"}
        self.lazy_tweak_cells_numeric = [i for i in range(16) if self.result["contradict"][i] == 1]

    def gen_round_tweakey_labels(self, round_number):
        """
        Generate the round tweakey labels
        """

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
        if r < self.Ri:
            tkpermutation_at_round = self.result["tkpermutation_at_round"][r]
        else:
            tkpermutation_at_round = self.result["tkpermutation_at_round"][self.R0 + r]                
        for i in range(16):
            output["before_sb"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXU"][r][i]], i)
            output["after_sb"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYU"][r][i]], i)
            output["after_addtk"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYU"][r][i]], i)                
            output["after_sr"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYU"][r][i]], self.inv_permutation[i])
            output["after_mix_columns"] += "\TFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXU"][r + 1][i]], i)        
        for i in range(16):
            output["before_sb"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXL"][r][i]], i)
            output["after_sb"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYL"][r][i]], i)
            output["after_addtk"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYL"][r][i]], i)
            output["after_sr"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AYL"][r][i]], self.inv_permutation[i])
            output["after_mix_columns"] += "\BFill[{0}]{{s{1}}}".format(self.fillcolor[self.result["AXL"][r + 1][i]], i)
        for i in range(8):                        
            output["subtweakey"] += "\Fill[{0}]{{s{1}}}".format(self.fillcolor[min(self.result["AYU"][r][i], self.result["AYL"][r][i])], i)
        for i in range(8):
            if tkpermutation_at_round[i] in self.lazy_tweak_cells_numeric:
                output["subtweakey"] += "\FrameCell[filter]{{s{0}}}".format(i)
        return output

    def generate_attack_shape(self):
        """
        Draw the figure of the Rectangle distinguisher
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
        # draw ED
        for r in range(0, self.RD):
            state = self.draw_ed(r)
            state["subtweakey"] += self.gen_round_tweakey_labels(r)
            contents += trim(r"""
            \SkinnyRoundTK[""" + str(r) + """]
                          {""" + state["before_sb"] + r"""} % state (input)
                          {""" + state["subtweakey"] + r"""} % tk[1]
                          {""" + r"""} % tk[2]
                          {""" + r"""} % tk[3]
                          {""" + state["after_sb"] + """} % state (after subcells)
                          {""" + state["after_addtk"] + r"""} % state (after addtweakey)
                          {""" + state["after_sr"] + r"""} % state (after shiftrows)""") + "\n\n"
            if r == self.RD - 1:
                contents += trim(r"""\SkinnyFin[""" + str(r + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
            elif (r) % 2 == 1:
                contents += trim(r"""\SkinnyNewLine[""" + str(r + 1) + r"""]{""") + state["after_mix_columns"] + r"""} % state (after mixcols)""" + "\n"
            
        contents += r"""\IntegralDistinguisherLegend""" + "\n"
        contents += r"""\end{tikzpicture}""" + "\n"
        contents += r"""%\caption{ID distinguisher for """ +  str(self.RD) +\
                    r""" rounds of ForkSKINNY-TK""" + str(self.variant) + "}\n"
        contents += trim(r"""%\end{figure}""") + "\n"
        contents += trim(r"""\begin{comment}""") + "\n"
        contents += self.attack_summary
        contents += trim(r"""\end{comment}""") + "\n"
        contents += trim(r"""\end{document}""")
        with open(self.output_file_name, "w") as output_file:
            output_file.write(contents)
