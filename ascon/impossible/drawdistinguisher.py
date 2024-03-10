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

class DrawDL():
    """
    Draw the shape of a given differential-linear distinguisher
    """

    def __init__(self, idobject, output_file_name="output.tex"):
        self.result = idobject.result
        self.RD = idobject.RD
        self.output_file_name = output_file_name
        self.upper_trail = idobject.upper_trail
        self.lower_trail = idobject.lower_trail
        self.attack_summary = idobject.attack_summary

    def generate_distinguisher_shape(self):
        """
        Draw the figure of the Rectangle distinguisher
        """

        contents = ""
        # head lines
        contents += trim(r"""
                    \documentclass[varwidth=100cm]{standalone}
                    \usepackage{ascon}
                    \usepackage{comment}
                    \begin{document}
                    \begin{tikzpicture}""") + "\n\n"
        # draw EU
        for r in range(self.RD + 1):
            fillcolor_x = []
            for row in range(5):
                for column in range(64):
                    if self.upper_trail["x"][r][row][column] == 1:
                        fillcolor_x.append(r"""\TFill[one]""" + f"{{{row}}}{{{column}}}")
                    elif self.upper_trail["x"][r][row][column] == -1:
                        fillcolor_x.append(r"""\TFill[upperunknown]""" + f"{{{row}}}{{{column}}}")
            fillcolor_x = ",".join(fillcolor_x)
            if r < self.RD:
                fillcolor_y = []
                for row in range(5):
                    for column in range(64):
                        if self.upper_trail["y"][r][row][column] == 1:
                            fillcolor_y.append(r"""\TFill[one]""" + f"{{{row}}}{{{column}}}")
                        elif self.upper_trail["y"][r][row][column] == -1:
                            fillcolor_y.append(r"""\TFill[upperunknown]""" + f"{{{row}}}{{{column}}}")
                fillcolor_y = ",".join(fillcolor_y)
            if r == 0:
                contents += trim(r"""
                        \node[matrix node]""" + "(x" + str(r) + "){" +
                    r"""\drawArray{""" + fillcolor_x + r"""}};""") + "\n"
            else:
                contents += trim(r"""
                        \node[matrix node, below=5cm of """ + "y" + str(r - 1) + ".center]" + "(x" + str(r) + "){" +
                    r"""\drawArray{""" + fillcolor_x + r"""}};""") + "\n"
                contents += r""" \draw[-latex, line width=3.5pt]""" + "(y" + str(r - 1) + r""".south) --node[right]{\Huge$L$}""" + "(x" + str(r) + ".north);"
            if r < self.RD:
                contents += trim(r"""
                            \node[matrix node, below=5cm of """ + "x" + str(r) + ".center]" + "(y" + str(r) + "){" +
                        r"""\drawArray{""" + fillcolor_y + r"""}};""") + "\n"
                contents += r""" \draw[-latex, line width=3.5pt]""" + "(x" + str(r) + r""".south) --node[right]{\Huge$S$}""" + "(y" + str(r) + ".north);"

        # draw EL
        for r in range(self.RD + 1):
            fillcolor_x = []
            for row in range(5):
                for column in range(64):
                    if self.lower_trail["x"][r][row][column] == 1:
                        fillcolor_x.append(r"""\BFill[one]""" + f"{{{row}}}{{{column}}}")
                    elif self.lower_trail["x"][r][row][column] == -1:
                        fillcolor_x.append(r"""\BFill[lowerunknown]""" + f"{{{row}}}{{{column}}}")
            fillcolor_x = ",".join(fillcolor_x)
            if r < self.RD:
                fillcolor_y = []
                for row in range(5):
                    for column in range(64):
                        if self.lower_trail["y"][r][row][column] == 1:
                            fillcolor_y.append(r"""\BFill[one]""" + f"{{{row}}}{{{column}}}")
                        elif self.lower_trail["y"][r][row][column] == -1:
                            fillcolor_y.append(r"""\BFill[lowerunknown]""" + f"{{{row}}}{{{column}}}")
                fillcolor_y = ",".join(fillcolor_y)
            if r == 0:
                contents += trim(r"""
                        \node[matrix node]""" + "(x" + str(r) + "){" +
                    r"""\drawArray{""" + fillcolor_x + r"""}};""") + "\n"
            else:
                contents += trim(r"""
                        \node[matrix node, below=5cm of """ + "y" + str(r - 1) + ".center]" + "(x" + str(r) + "){" +
                    r"""\drawArray{""" + fillcolor_x + r"""}};""") + "\n"
                contents += r""" \draw[-latex, line width=3.5pt]""" + "(y" + str(r - 1) + r""".south) --node[right]{\Huge$L$}""" + "(x" + str(r) + ".north);" + "\n"
            if r < self.RD:
                contents += trim(r"""
                        \node[matrix node, below=5cm of """ +  "x" + str(r) + ".center]" + "(y" + str(r) + "){" +
                    r"""\drawArray{""" + fillcolor_y + r"""}};""") + "\n"
                contents += r""" \draw[-latex, line width=3.5pt]""" + "(x" + str(r) + r""".south) --node[right]{\Huge$S$}""" + "(y" + str(r) + ".north);" + "\n"
        contents += "\n\n" + r"""\begin{comment}""" + "\n"
        contents += self.attack_summary
        contents += r"""\end{comment}""" + "\n"
        contents += r"""\end{tikzpicture}""" + "\n"
        contents += trim(r"""\end{document}""")
        with open(self.output_file_name, "w") as output_file:
            output_file.write(contents)
