/*
Partial sum optimization for Skinny.
Copyright (C) 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

int: tweakey_setting;
int: start_round;
int: final_round;
int: tweakey_cell;
int: balanced_cell;
int: input_active;
int: steps;
int: scale;

/* -------------------------------------------------------------------------------------------------------------------- */
set of int: ROUNDS = start_round..final_round;
set of int: ROUNDS_APPENDED = start_round..(final_round + 1);
set of int: SIZE = 0..15;
set of int: KEY_SIZE = 0..7;
set of int: STEPS = 0..<steps;
set of int: STEPS_KEY = 1..<steps;
set of int: STEPS_UNINVOLVED = -1..<steps;

/* -------------------------------------------------------------------------------------------------------------------- */
array[0..15] of int: shiftrows = array1d(0..15,[0, 1, 2, 3, 7, 4, 5, 6, 10, 11, 8, 9, 13, 14, 15, 12]);


/* tweakey permutation */

/* calculate tweakey at each position */
/* -------------------------------------------------------------------------------------------------------------------- */
array[0..15] of int: tweakey_permutation = array1d(0..15,[9,15,8,13,10,14,12,11,0,1,2,3,4,5,6,7]);

array[0..final_round, 0..15] of var int: tweakey;

constraint forall (i in 0..15) (tweakey[0,i] = i);
constraint forall (n in 1..final_round, i in 0..15) (tweakey[n,i] = tweakey_permutation[tweakey[n-1,i]]);


/* Propagate involved cells forward */

/* Calculate which cells are involved based on the distinguisher. This has a probability of 1. 
The information is then used in the other parts of the optimisiation.*/
/* -------------------------------------------------------------------------------------------------------------------- */
array[ROUNDS_APPENDED,SIZE] of var bool: state_x_involved_cells;
array[ROUNDS,SIZE] of var bool: state_w_involved_cells;

constraint forall(i in SIZE) (
  if i = balanced_cell then state_x_involved_cells[start_round, i] = true else state_x_involved_cells[start_round, i] = false endif
);

constraint forall(i in ROUNDS, j in SIZE)(state_w_involved_cells[i, j] = state_x_involved_cells[i, shiftrows[j]]);

constraint forall(i in ROUNDS, j in SIZE)(
  if j div 4 = 0 then state_x_involved_cells[i+1, j] = state_w_involved_cells[i, j+3*4]
  elseif j div 4 = 1 then state_x_involved_cells[i+1, j] = (state_w_involved_cells[i, j-4] \/ state_w_involved_cells[i, j] \/ state_w_involved_cells[i,j+4])
  elseif j div 4 = 2 then state_x_involved_cells[i+1, j] = state_w_involved_cells[i, j-4]
  else state_x_involved_cells[i+1, j] = (state_w_involved_cells[i, j-8] \/ state_w_involved_cells[i, j-4] \/ state_w_involved_cells[i,j])
  endif
);


/* |tweakey| <= tweakey_setting */

/* Make sure that the tweakey of a certain value is only guessed the first tweakey_setting(TK1, TK2, TK3,...) times.*/
/* -------------------------------------------------------------------------------------------------------------------- */
array[SIZE] of var 0..((final_round- start_round) div 2 + 1): tweakey_count;
array[ROUNDS,KEY_SIZE] of var -1 .. 15: stk_to_guess;
array[SIZE, ROUNDS] of var -1 .. 15: tweakey_in_round;

/* tweakey_count counts how many times a tweakey value occures. Only consider involved tweakeys(The ones involved in the forward propagation). */
constraint forall(i in SIZE) (
  tweakey_count[i] = sum(j in ROUNDS, k in KEY_SIZE)(state_x_involved_cells[j, k] /\ tweakey[j, k] = i)
);

/* For each tweakey position stk_to_guess stores if the tweakey in that position should be guessed.
Cases:
  - The tweakey position is not involved in the forward propagation or the tweakey value is the same as the input parameter tweakey.
    => stk_to_guess = -1 (Do not have to guess)
  ELSE
    - The tweakey count of that tweakey value is below the tweakey setting
      - stk_to_guess = tweakey (Always have to guess)
    - The tweakey count of that tweakey value is above the tweakey setting
      - stk_to_guess = tweakey or -1 (Either have to guess or not)
*/
constraint forall(i in ROUNDS, j in KEY_SIZE) (
  if state_x_involved_cells[i, j] /\ tweakey[i, j] != tweakey_cell then
    if tweakey_count[tweakey[i, j]] <= tweakey_setting then 
      stk_to_guess[i, j] = tweakey[i, j]
    else
      stk_to_guess[i, j] = tweakey[i, j] \/ stk_to_guess[i, j] = -1
    endif
  else
    stk_to_guess[i, j] = -1
  endif
);

/* limit the amount of tweakey cells to guess to the tweakey setting*/
constraint forall(i in SIZE diff {tweakey_cell}) (
  if tweakey_count[i] > tweakey_setting then tweakey_setting = sum(j in ROUNDS, k in KEY_SIZE)(stk_to_guess[j, k] = i) endif
);

/* tweakey_in_round stores the step in which each tweakey cell is guessed*/
constraint forall(i in SIZE) (
if tweakey_count[i] > tweakey_setting /\ i != tweakey_cell then
  forall(j in ROUNDS) (
    if i in stk_to_guess[j, KEY_SIZE] then 
      forall(k in KEY_SIZE) (
        if i = stk_to_guess[j, k] then
          tweakey_in_round[i, j] = stk[j, k]
        endif)
    else
      tweakey_in_round[i, j] = -1
    endif
  )
else
  forall(j in ROUNDS)(tweakey_in_round[i, j] = -1)
endif
);

/* Make sure that the tweakeys with the same value are guessed in ascending steps.
Once the same tweakey value has been guessed tweakey_setting times stop guessing this tweakey value.*/
constraint forall(i in ROUNDS, j in KEY_SIZE) (
if tweakey[i, j] != tweakey_cell /\ state_x_involved_cells[i, j] /\ tweakey[i, j] != stk_to_guess[i, j] then
  forall(k in ROUNDS) (tweakey_in_round[tweakey[i, j], k] < state_x[i, j])
endif
);


/* Propagate steps backwards */
/* Each state contains the step in which it is guessed. */
/* -------------------------------------------------------------------------------------------------------------------- */
array[ROUNDS_APPENDED,SIZE] of var STEPS_UNINVOLVED: state_x;
array[ROUNDS,KEY_SIZE] of var STEPS_UNINVOLVED: stk;
array[ROUNDS,SIZE] of var STEPS_UNINVOLVED: state_z;
array[ROUNDS,SIZE] of var STEPS_UNINVOLVED: state_w;

/* Set cells in last state_x */
/* All involved cells in the last state are set to step number 0 */
constraint forall(i in SIZE) (
  if state_x_involved_cells[final_round+1, i] then state_x[final_round+1, i] = 0 else state_x[final_round+1, i] = -1 endif
);

/* Mix column */
/* The step number before mix_column is the maximum step number of the cells after mix_column that influence that cell */
constraint forall(i in ROUNDS, j in SIZE ) (
  if state_w_involved_cells[i, j] then mix_column_backward(state_x[i+1, SIZE], state_w[i, j], j)
  else state_w[i, j] = -1
  endif
);

/* Shift rows */
constraint forall(i in ROUNDS, j in SIZE)(state_w[i, j] = state_z[i, shiftrows[j]]);

/* Key */
/* In case stk_to_guess is not -1 the key state has to be bigger than the state_z and state_x is equal to stk
Otherwise state_x = state_z and stk = -1*/
constraint forall(i in ROUNDS, j in KEY_SIZE) (
  if stk_to_guess[i, j] >= 0 then 
    stk[i, j] > state_z[i, j]  /\ state_x[i, j] = stk[i, j]
  else stk[i, j] = -1  /\ state_x[i, j] = state_z[i, j] endif
);

/* Set the lower 8 cells of state_z = state_x*/
constraint forall(i in ROUNDS, j in 8..15) (
  state_x[i, j] = state_z[i, j]
);


/* Key in successive order */
/* Make sure that there is no gap in the steps. */
/* -------------------------------------------------------------------------------------------------------------------- */
array[STEPS_KEY] of var STEPS: key_count;

constraint forall(i in STEPS_KEY) (
  key_count[i] = sum(j in ROUNDS, k in KEY_SIZE)(stk[j, k] = i)
);

constraint forall(i in 1 .. steps - 2) (
  if key_count[i+1] != 0 then key_count[i] > 0 endif
);


/* Mem z count */
/* -------------------------------------------------------------------------------------------------------------------- */
array[STEPS] of var 0..16: mem_z_count;

/* We have to store the cell at state_z if state_z <= STEP AND stk > STEP*/
constraint forall(i in STEPS) (
  mem_z_count[i] = sum(j in ROUNDS, k in KEY_SIZE)(state_z[j, k] <= i /\ stk[j, k] > i)
);


/* Mem x count */
/* -------------------------------------------------------------------------------------------------------------------- */
array[STEPS] of var 0..16: mem_x_count;

/* If state_x <= STEP then we have to store it depending on which row the cell is in:
  - OR_k state_w[k] > STEP, where k is depending on mix_column*/
constraint forall(i in STEPS) (
  mem_x_count[i] = sum(j in ROUNDS, k in SIZE) (
    if state_x[j+1, k] <= i then
      if k div 4 = 0 then (state_w[j, k+12] > i)
      elseif k div 4 = 1 then (state_w[j, k-4] > i \/ state_w[j, k] > i \/ state_w[j, k+4] > i)
      elseif k div 4 = 2 then (state_w[j, k-4] > i)
      else (state_w[j, k-8] > i \/ state_w[j, k-4] > i \/ state_w[j, k] > i)
      endif
    else
      false
    endif
  )
);


/* Mem tweakey count */
/* -------------------------------------------------------------------------------------------------------------------- */
array[STEPS] of var 0..10: mem_tweakey;

/* In the case of the parameter tweakey_cell we need to store this cell until it is guessed */
constraint forall(i in STEPS) (
  mem_tweakey[i] = sum(j in ROUNDS, k in KEY_SIZE where tweakey[j, k] = tweakey_cell /\ state_x_involved_cells[j, k])(state_x[j, k] > i)
);


/* Unit cost */
/* -------------------------------------------------------------------------------------------------------------------- */
array[STEPS_KEY] of var int: unit;

/* Count how many times state_x=STEP, this gives us the amount of SBOX calls per STEP */
constraint forall(i in STEPS_KEY) (
    unit[i] = sum(j in ROUNDS, k in SIZE) (state_x[j, k] == i)
);


/* Time cost */
/* -------------------------------------------------------------------------------------------------------------------- */
var int: data_inital;
array[STEPS_KEY] of var 0..256: time_cost;
array[STEPS_KEY] of var 0..40: time_cost_scaled;
array[STEPS_KEY] of var int: time_cost_t;

constraint data_inital = (16 - input_active + tweakey_setting);

/* For all STEPS where we guess keys (key_count > 0) we calculate the time_cost of this step
This is the minimum(data_initial, CURRENT_MEM) times the key_count up to that point (=amount of keys guessed) */
constraint forall(i in STEPS_KEY) (
  if key_count[i] > 0 then
    if data_inital > (mem_tweakey[i-1] + mem_z_count[i-1] + mem_x_count[i-1]) then 
      time_cost[i] = (sum(j in 1..i) (key_count[j]) + mem_tweakey[i-1] + mem_z_count[i-1] + mem_x_count[i-1]) * 4
    else
      time_cost[i] = (sum(j in 1..i) (key_count[j]) + data_inital) * 4
    endif
  else
    time_cost[i] = 0
  endif
);

/* Scale the cost to avoid integer overflows (Or-tools max int is ~2^40) */
constraint forall(i in STEPS_KEY) (
  time_cost_scaled[i] = max(0, time_cost[i] - scale)
);

/* Take power of cost */
constraint forall(i in STEPS_KEY) (int_pow(2, time_cost_scaled[i], time_cost_t[i]));

/* Minimize time */
/* -------------------------------------------------------------------------------------------------------------------- */
var int: total_time_cost;

/* Sum all time_costs * unit_cost
Since the total SBOX calls for encrypting stays the same, we do not need to devide the unit by it*/
constraint total_time_cost = sum(i in STEPS_KEY where time_cost_t[i] > 1)(time_cost_t[i] * unit[i]);

solve minimize total_time_cost;


/* Predicates */
/* -------------------------------------------------------------------------------------------------------------------- */
predicate mix_column_backward(array[SIZE] of var STEPS_UNINVOLVED: x, var STEPS_UNINVOLVED: w, var SIZE: j) = 
  if j div 4 = 0 then w = x[j+4]
  elseif j div 4 = 1 then w = max(k in {0,4,8})(x[j+k])
  elseif j div 4 = 2 then w = max(k in {-4,4})(x[j+k])
  else w = max(k in {-12,0})(x[j+k])
  endif
;
