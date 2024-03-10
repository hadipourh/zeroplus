# Programs

## pso.py

Optimize the partial sum guessing order

Usage:

`pso.py [-h] [-s [STEPS]] tweakey_setting final_round start_round tweakey_cell balanced_cell input_active scale`

- `tweakey_setting:       Specify version of Skinny used`
- `final_round:           Final round of the key recovery`
- `start_round:           Start round of the key recovery`
- `tweakey_cell:          Specify which tweakey cell is controlled by the attacker`
- `balanced_cell:         Specify the balanced cell from the output of the distinguisher`
- `input_active:          Specify how many cell are active at the input of the distinguisher`
- `scale:                 Scale the time complexity, must be used since many solver only support limited data types`
- `s [STEPS], --steps [STEPS] Specify the maximum number of steps, default are the involved subtweakey cells`

Example:
`python pso.py 1 18 15 5 4 9 32`


## psvisu.py

Visualize the partial sum recovery steps

Usage:

`psvisu.py [-h] [-c] [-s] [-n] [-m] [-p] input [input ...]`

- `-c, --color   Use different color for every step`
- `-s, --steps   Visualize each step individually`
- `-n, --step-number  Put the step number in each cell except the stk`
- `-m, --memory  Mark which states have to be stored in memory`
- `-p, --pdf     Run latex and output pdf`
- `input: json file with key guess order (output of autopsy2)`

Example:

`python psvisu.py 1_18_15_5_4_9.json -n -p`

or

`python psvisu.py 1_18_15_5_4_9.json -s -m -p`

Output:

Partial Sum Key Recovery Visualization stored in `3_25_17_14_1_4.pdf`

Compiling the file requires the various cipher `*.sty` files in the top-level directory. If using `latexmk` to compile, this path is included  automatically by the `.latexmkrc` file; otherwise, please copy to the same directory as the tex file.
