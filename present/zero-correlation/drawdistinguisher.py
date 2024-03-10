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

    def __init__(self, zc_object, output_file_name="output.tex"):
        self.result = zc_object.result
        self.RD = zc_object.RD
        self.output_file_name = output_file_name
        self.upper_trail = zc_object.upper_trail
        self.lower_trail = zc_object.lower_trail
        self.attack_summary = zc_object.attack_summary
        self.meeting_point = zc_object.contradiction_locations[0][0]

    def generate_distinguisher_shape(self):
        """
        Draw the figure of the Rectangle distinguisher
        """

        contents = ""
        # head lines
        contents += trim(r"""
                        \documentclass[varwidth=12cm]{standalone}
                        \usepackage{amsmath,amssymb}
                        \usepackage{subcaption}
                        \usepackage{tikz}
                        \usepackage{comment}
                        \usepackage{tugcolors}
                        \usetikzlibrary{positioning,cipher, calc}

                        % Define your custom colors
                        \colorlet{zero}{white}
                        \colorlet{one}{tugred}
                        \colorlet{upperunknown}{tugblue}
                        \colorlet{lowerunknown}{tuggreen!70!green}

                        \newif\ifshowhelpers\showhelpersfalse % set \showhelperstrue to display indexing helper labels
                        \ifshowhelpers
                        \usepackage[final]{microtype}
                        \microtypesetup{letterspace=-80}
                        \fi

                        \newcommand{\activeInputUpper}[2]{
                        \draw[->, #2, very thick] (i0-#1) -- (i0-#1|-S1-0.north);
                        }

                        \newcommand{\activeLinearUpper}[3]{
                        % #1 = round, #2 = bit position at sboxout
                        \pgfmathsetmacro{\newPos}{int(mod(\nbits/4*#2,\lastBit)+div(#2,\lastBit)*\lastBit)}
                        \draw[#3,->, double distance=.5pt, fill=none] ($(i0-#2|-S#1-0.south) + (0, -0.25em)$) -- +(0,-.5em) -- (i#1-\newPos) -- (xor#1-\newPos.south);
                        \pgfmathsetmacro{\actSbx}{int(div(#2,4))}
                        \activeSboxUpper{#1}{\actSbx}{#3}
                        }

                        \newcommand{\activeSboxUpper}[3]{
                        % #1 = round, #2 = sbox position
                        \node[box, minimum size=0.5cm, fill=#3] (S#1-#2) at (#2*3em+1.1em,7em-#1*9em) {\color{white}$\mathcal{S}$};
                        }

                        \newcommand{\activeInputLower}[2]{
                        \draw[->, #2, thick, double distance=.5pt, fill=none] (i0-#1|-S1-0.north) -- (i0-#1);
                        }

                        \newcommand{\activeLinearLower}[3]{
                        % #1 = round, #2 = bit position at sboxout
                        \pgfmathsetmacro{\newPos}{int(mod(\nbits/4*#2,\lastBit)+div(#2,\lastBit)*\lastBit)}
                        \draw[#3,->, thick] (xor#1-\newPos.north) -- (i#1-\newPos) -- ($(i0-#2|-S#1-0.south) + (0,-.5em)$) -- ($(S#1-0-|i0-#2) + (0,-1em)$);
                        \pgfmathsetmacro{\actSbx}{int(div(#2,4))}
                        \activeSboxLower{#1}{\actSbx}{#3}
                        }

                        \newcommand{\activeSboxLower}[3]{
                        % #1 = round, #2 = sbox position
                        \node[box, thick, draw=#3, double distance=.2pt, fill=none] (S#1-#2) at (#2*3em+1.1em,7em-#1*9em) {$\mathcal{S}$};
                        }


                        \begin{document}
                        %\begin{figure}
                        \centering
                        \begin{tikzpicture}[scale=.625,                              % adapt size
                                            box/.append style={minimum size=.625cm}, % adapt size
                                            activebit/.style={tug, thin, double distance=.5pt},
                                            rounded corners, >=latex]""") + "\n"
        contents += r"""\pgfmathsetmacro{\nrounds}{""" + str(self.RD) + r"""} % set nr rounds""" + "\n"
        contents += trim(r"""
                    \pgfmathsetmacro{\nbits}{64}  % set bitsize of state
                    \pgfmathsetmacro{\lastBit}{int(\nbits-1)}
                    \pgfmathsetmacro{\secondlastBit}{int(\nbits-2)}
                    \pgfmathsetmacro{\lastSbox}{int(\nbits/4-1)}
                    \foreach \r in {0,...,\nrounds} {
                    \foreach \z in {0,...,\lastBit} {
                        \node[xor, scale=0.6] (xor\r-\z) at (\z*0.75em,-\r*9em) {};
                        \coordinate[above = 0.5em of xor\r-\z] (i\r-\z) ;
                    }
                    \node[left = 0em of xor\r-0] (K\r) {};
                    }
                    \foreach \z in {0,...,\lastBit} {
                    \draw[->] (i0-\z) -- (xor0-\z);
                    \ifshowhelpers
                        \pgfmathsetmacro{\idxraise}{2-4*mod(\z,2)} % indexing helper
                        \draw (i0-\z) node[above=\idxraise pt,gray] {\tiny\ttfamily\lsstyle \z}; % indexing helper
                    \fi
                    }
                    \foreach \r [evaluate=\r as \rr using {int(\r-1)}] in {1,...,\nrounds} {
                    \foreach \z in {0,...,\lastSbox} {
                        \node[box] (S\r-\z) at (\z*3em+1.1em,7em-\r*9em) {$\mathcal{S}$};
                    }
                    \foreach \z [evaluate=\z as \zz using {int(mod(\nbits/4*\z,\lastBit))}] in {0,...,\secondlastBit} {
                        \draw[->] (xor\rr-\z|-S\r-0.south) -- +(0,-.5em) -- (i\r-\zz) -- (xor\r-\zz);
                        \draw     (xor\rr-\z) -- (xor\rr-\z|-S\r-0.north);
                    }
                    \draw[->] (xor\rr-\lastBit|-S\r-0.south) -- +(0,-.5em) -- (i\r-\lastBit) -- (xor\r-\lastBit);
                    \draw     (xor\rr-\lastBit) -- (xor\rr-\lastBit|-S\r-0.north);
                    }""")
        contents += "\n\n"       
        # draw EU
        for i in range(64):
            if self.upper_trail["x"][0][i] == 1:
                contents += r"""\activeInputUpper{""" + str(i) + r"""}{one}""" + "\n"
            elif self.upper_trail["x"][0][i] == -1:
                contents += r"""\activeInputUpper{""" + str(i) + r"""}{upperunknown}""" + "\n"
        for r in range(self.meeting_point):
            for i in range(64):
                if self.upper_trail["y"][r][i] == 1:
                    contents += r"""\activeLinearUpper{""" + str(r + 1) + r"""}{""" + str(i) + r"""}{one}""" + "\n"
                elif self.upper_trail["y"][r][i] == -1:
                    contents += r"""\activeLinearUpper{""" + str(r + 1) + r"""}{""" + str(i) + r"""}{upperunknown}""" + "\n"
        for r in range(self.meeting_point - 1, self.RD):
            for i in range(64):
                if self.lower_trail["y"][r][i] == 1:
                    contents += r"""\activeLinearLower{""" + str(r + 1) + r"""}{""" + str(i) + r"""}{one}""" + "\n"
                elif self.lower_trail["y"][r][i] == -1:
                    contents += r"""\activeLinearLower{""" + str(r + 1) + r"""}{""" + str(i) + r"""}{lowerunknown}""" + "\n"
        # for i in range(64):
        #     if self.lower_trail["x"][0][i] == 1:
        #         contents += r"""\activeInputLower{""" + str(i) + r"""}{one}""" + "\n"
        #     elif self.lower_trail["x"][0][i] == -1:
        #         contents += r"""\activeInputLower{""" + str(i) + r"""}{lowerunknown}""" + "\n"

        contents += "\n\n" + r"""\begin{comment}""" + "\n"
        contents += self.attack_summary
        contents += r"""\end{comment}""" + "\n"
        contents += r"""\end{tikzpicture}""" + "\n"
        contents += r"""%\caption{ZC distinguisher for""" + str(self.RD) + r"""rounds of \texttt{PRESENT}.}""" + "\n"
        contents += r"""%\end{figure}""" + "\n"
        contents += trim(r"""\end{document}""")
        with open(self.output_file_name, "w") as output_file:
            output_file.write(contents)
