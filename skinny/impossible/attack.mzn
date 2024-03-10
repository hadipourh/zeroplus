/*
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
*/

include "table.mzn";
int: variant;
int: NPT; % number of parallel tweakey lines in the tweakey schedule (used for distinguisher part)
int: GuessingThreshold1; % Guess each key tweakey cells no more than GuessingThreshold1 times
int: GuessingThreshold2; % Guess each key tweakey cells no more than GuessingThreshold2 times
int: RD; % the length of distinguisher
int: Rzero; % the number of rounds before fork
int: Rone; % the number of rounds in C0-fork
int: RB; % number of prepended rounds in key-recovery
int: RF; % number of appended rounds in key-recovery
int: RT = RB + RD + RF; % total number of attacked rounds
bool: skip_first_sbox_layer; % skip the first S-box layer in distinguisher or not
bool: is_related_tweakey; % related-tweak setting vs. single-tweakey setting
int: block_size; % block size
int: cell_size; % cell size
int: tolerance; % tolerance from the valid domain in time or data complexity
block_size = 16*cell_size; 
tolerance = 0;

constraint assert(RB >= 0, "Invalid value for RB: " ++
                  "RB must be greater than or equal to 0");
constraint assert(RD >= 1, "Invalid value for RD: " ++
                  "RD must be greater than or equal to 1");
constraint assert(RF >= 0, "Invalid value for RF: " ++
                  "RF must be greater than or equal to 0");
constraint assert(variant in 1..9, "Invalid value for variant: " ++
                  "variant must be in {1, 2, 3, 4, 5, 6, 7, 8, 9}");


% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%  ____          __  _                _                   _                    _____       _      _            
% |  _ \   ___  / _|(_) _ __    ___  | |     ___    ___  | | __ _   _  _ __   |_   _|__ _ | |__  | |  ___  ___ 
% | | | | / _ \| |_ | || '_ \  / _ \ | |    / _ \  / _ \ | |/ /| | | || '_ \    | | / _` || '_ \ | | / _ \/ __|
% | |_| ||  __/|  _|| || | | ||  __/ | |___| (_) || (_) ||   < | |_| || |_) |   | || (_| || |_) || ||  __/\__ \
% |____/  \___||_|  |_||_| |_| \___| |_____|\___/  \___/ |_|\_\ \__,_|| .__/    |_| \__,_||_.__/ |_| \___||___/
%                                                                     |_|                 
% define lookup tables

% define the log2(x) - 0.53 function
array[1..384, 1..2] of int: log2_minus_053_times_1000_lookup_table = array2d(1..384, 1..2, [1, -530, 2, 470, 3, 1054, 4, 1470, 5, 1791, 6, 2054, 7, 2277, 8, 2469, 9, 2639, 10, 2791, 11, 2929, 12, 3054, 13, 3170, 14, 3277, 15, 3376, 16, 3469, 17, 3557, 18, 3639, 19, 3717, 20, 3791, 21, 3862, 22, 3929, 23, 3993, 24, 4054, 25, 4113, 26, 4170, 27, 4224, 28, 4277, 29, 4327, 30, 4376, 31, 4424, 32, 4470, 33, 4514, 34, 4557, 35, 4599, 36, 4639, 37, 4679, 38, 4717, 39, 4755, 40, 4791, 41, 4827, 42, 4862, 43, 4896, 44, 4929, 45, 4961, 46, 4993, 47, 5024, 48, 5054, 49, 5084, 50, 5113, 51, 5142, 52, 5170, 53, 5197, 54, 5224, 55, 5251, 56, 5277, 57, 5302, 58, 5327, 59, 5352, 60, 5376, 61, 5400, 62, 5424, 63, 5447, 64, 5470, 65, 5492, 66, 5514, 67, 5536, 68, 5557, 69, 5578, 70, 5599, 71, 5619, 72, 5639, 73, 5659, 74, 5679, 75, 5698, 76, 5717, 77, 5736, 78, 5755, 79, 5773, 80, 5791, 81, 5809, 82, 5827, 83, 5845, 84, 5862, 85, 5879, 86, 5896, 87, 5912, 88, 5929, 89, 5945, 90, 5961, 91, 5977, 92, 5993, 93, 6009, 94, 6024, 95, 6039, 96, 6054, 97, 6069, 98, 6084, 99, 6099, 100, 6113, 101, 6128, 102, 6142, 103, 6156, 104, 6170, 105, 6184, 106, 6197, 107, 6211, 108, 6224, 109, 6238, 110, 6251, 111, 6264, 112, 6277, 113, 6290, 114, 6302, 115, 6315, 116, 6327, 117, 6340, 118, 6352, 119, 6364, 120, 6376, 121, 6388, 122, 6400, 123, 6412, 124, 6424, 125, 6435, 126, 6447, 127, 6458, 128, 6470, 129, 6481, 130, 6492, 131, 6503, 132, 6514, 133, 6525, 134, 6536, 135, 6546, 136, 6557, 137, 6568, 138, 6578, 139, 6588, 140, 6599, 141, 6609, 142, 6619, 143, 6629, 144, 6639, 145, 6649, 146, 6659, 147, 6669, 148, 6679, 149, 6689, 150, 6698, 151, 6708, 152, 6717, 153, 6727, 154, 6736, 155, 6746, 156, 6755, 157, 6764, 158, 6773, 159, 6782, 160, 6791, 161, 6800, 162, 6809, 163, 6818, 164, 6827, 165, 6836, 166, 6845, 167, 6853, 168, 6862, 169, 6870, 170, 6879, 171, 6887, 172, 6896, 173, 6904, 174, 6912, 175, 6921, 176, 6929, 177, 6937, 178, 6945, 179, 6953, 180, 6961, 181, 6969, 182, 6977, 183, 6985, 184, 6993, 185, 7001, 186, 7009, 187, 7016, 188, 7024, 189, 7032, 190, 7039, 191, 7047, 192, 7054, 193, 7062, 194, 7069, 195, 7077, 196, 7084, 197, 7092, 198, 7099, 199, 7106, 200, 7113, 201, 7121, 202, 7128, 203, 7135, 204, 7142, 205, 7149, 206, 7156, 207, 7163, 208, 7170, 209, 7177, 210, 7184, 211, 7191, 212, 7197, 213, 7204, 214, 7211, 215, 7218, 216, 7224, 217, 7231, 218, 7238, 219, 7244, 220, 7251, 221, 7257, 222, 7264, 223, 7270, 224, 7277, 225, 7283, 226, 7290, 227, 7296, 228, 7302, 229, 7309, 230, 7315, 231, 7321, 232, 7327, 233, 7334, 234, 7340, 235, 7346, 236, 7352, 237, 7358, 238, 7364, 239, 7370, 240, 7376, 241, 7382, 242, 7388, 243, 7394, 244, 7400, 245, 7406, 246, 7412, 247, 7418, 248, 7424, 249, 7430, 250, 7435, 251, 7441, 252, 7447, 253, 7452, 254, 7458, 255, 7464, 256, 7470, 257, 7475, 258, 7481, 259, 7486, 260, 7492, 261, 7497, 262, 7503, 263, 7508, 264, 7514, 265, 7519, 266, 7525, 267, 7530, 268, 7536, 269, 7541, 270, 7546, 271, 7552, 272, 7557, 273, 7562, 274, 7568, 275, 7573, 276, 7578, 277, 7583, 278, 7588, 279, 7594, 280, 7599, 281, 7604, 282, 7609, 283, 7614, 284, 7619, 285, 7624, 286, 7629, 287, 7634, 288, 7639, 289, 7644, 290, 7649, 291, 7654, 292, 7659, 293, 7664, 294, 7669, 295, 7674, 296, 7679, 297, 7684, 298, 7689, 299, 7694, 300, 7698, 301, 7703, 302, 7708, 303, 7713, 304, 7717, 305, 7722, 306, 7727, 307, 7732, 308, 7736, 309, 7741, 310, 7746, 311, 7750, 312, 7755, 313, 7760, 314, 7764, 315, 7769, 316, 7773, 317, 7778, 318, 7782, 319, 7787, 320, 7791, 321, 7796, 322, 7800, 323, 7805, 324, 7809, 325, 7814, 326, 7818, 327, 7823, 328, 7827, 329, 7831, 330, 7836, 331, 7840, 332, 7845, 333, 7849, 334, 7853, 335, 7858, 336, 7862, 337, 7866, 338, 7870, 339, 7875, 340, 7879, 341, 7883, 342, 7887, 343, 7892, 344, 7896, 345, 7900, 346, 7904, 347, 7908, 348, 7912, 349, 7917, 350, 7921, 351, 7925, 352, 7929, 353, 7933, 354, 7937, 355, 7941, 356, 7945, 357, 7949, 358, 7953, 359, 7957, 360, 7961, 361, 7965, 362, 7969, 363, 7973, 364, 7977, 365, 7981, 366, 7985, 367, 7989, 368, 7993, 369, 7997, 370, 8001, 371, 8005, 372, 8009, 373, 8013, 374, 8016, 375, 8020, 376, 8024, 377, 8028, 378, 8032, 379, 8036, 380, 8039, 381, 8043, 382, 8047, 383, 8051, 384, 8054]);
% define the ceil(log2(x) - 0.53) function
array[1..256, 1..2] of int: log2_minus_053_table = array2d(1..256, 1..2, [1, 0, 2, 1, 3, 2, 4, 2, 5, 2, 6, 3, 7, 3, 8, 3, 9, 3, 10, 3, 11, 3, 12, 4, 13, 4, 14, 4, 15, 4, 16, 4, 17, 4, 18, 4, 19, 4, 20, 4, 21, 4, 22, 4, 23, 4, 24, 5, 25, 5, 26, 5, 27, 5, 28, 5, 29, 5, 30, 5, 31, 5, 32, 5, 33, 5, 34, 5, 35, 5, 36, 5, 37, 5, 38, 5, 39, 5, 40, 5, 41, 5, 42, 5, 43, 5, 44, 5, 45, 5, 46, 5, 47, 6, 48, 6, 49, 6, 50, 6, 51, 6, 52, 6, 53, 6, 54, 6, 55, 6, 56, 6, 57, 6, 58, 6, 59, 6, 60, 6, 61, 6, 62, 6, 63, 6, 64, 6, 65, 6, 66, 6, 67, 6, 68, 6, 69, 6, 70, 6, 71, 6, 72, 6, 73, 6, 74, 6, 75, 6, 76, 6, 77, 6, 78, 6, 79, 6, 80, 6, 81, 6, 82, 6, 83, 6, 84, 6, 85, 6, 86, 6, 87, 6, 88, 6, 89, 6, 90, 6, 91, 6, 92, 6, 93, 7, 94, 7, 95, 7, 96, 7, 97, 7, 98, 7, 99, 7, 100, 7, 101, 7, 102, 7, 103, 7, 104, 7, 105, 7, 106, 7, 107, 7, 108, 7, 109, 7, 110, 7, 111, 7, 112, 7, 113, 7, 114, 7, 115, 7, 116, 7, 117, 7, 118, 7, 119, 7, 120, 7, 121, 7, 122, 7, 123, 7, 124, 7, 125, 7, 126, 7, 127, 7, 128, 7, 129, 7, 130, 7, 131, 7, 132, 7, 133, 7, 134, 7, 135, 7, 136, 7, 137, 7, 138, 7, 139, 7, 140, 7, 141, 7, 142, 7, 143, 7, 144, 7, 145, 7, 146, 7, 147, 7, 148, 7, 149, 7, 150, 7, 151, 7, 152, 7, 153, 7, 154, 7, 155, 7, 156, 7, 157, 7, 158, 7, 159, 7, 160, 7, 161, 7, 162, 7, 163, 7, 164, 7, 165, 7, 166, 7, 167, 7, 168, 7, 169, 7, 170, 7, 171, 7, 172, 7, 173, 7, 174, 7, 175, 7, 176, 7, 177, 7, 178, 7, 179, 7, 180, 7, 181, 7, 182, 7, 183, 7, 184, 7, 185, 8, 186, 8, 187, 8, 188, 8, 189, 8, 190, 8, 191, 8, 192, 8, 193, 8, 194, 8, 195, 8, 196, 8, 197, 8, 198, 8, 199, 8, 200, 8, 201, 8, 202, 8, 203, 8, 204, 8, 205, 8, 206, 8, 207, 8, 208, 8, 209, 8, 210, 8, 211, 8, 212, 8, 213, 8, 214, 8, 215, 8, 216, 8, 217, 8, 218, 8, 219, 8, 220, 8, 221, 8, 222, 8, 223, 8, 224, 8, 225, 8, 226, 8, 227, 8, 228, 8, 229, 8, 230, 8, 231, 8, 232, 8, 233, 8, 234, 8, 235, 8, 236, 8, 237, 8, 238, 8, 239, 8, 240, 8, 241, 8, 242, 8, 243, 8, 244, 8, 245, 8, 246, 8, 247, 8, 248, 8, 249, 8, 250, 8, 251, 8, 252, 8, 253, 8, 254, 8, 255, 8, 256, 8]);
% skinny round permutation
array[0..15] of int: round_permutation = array1d(0..15, [0, 1, 2, 3, 7, 4, 5, 6, 10, 11, 8, 9, 13, 14, 15, 12]);
% skinny tweakey permutation
array[0..15] of int: inv_tweakey_permutation = array1d(0..15, [8, 9, 10, 11, 12, 13, 14, 15, 2, 0, 4, 7, 6, 3, 5, 1]);

array[0..15, 1..8] of 0..1: fixed_filter_backward = array2d(0..15, 1..8,[0,0,0,0,0,0,0,0,
                                                                         0,0,0,1,0,0,0,1,
                                                                         0,0,1,0,0,0,1,0,
                                                                         0,0,1,1,0,0,1,1,
                                                                         0,1,0,0,0,0,0,0,
                                                                         0,1,0,1,0,0,0,0,
                                                                         0,1,1,0,0,0,1,0,
                                                                         0,1,1,1,0,0,0,0,
                                                                         1,0,0,0,1,0,0,0,
                                                                         1,0,0,1,0,0,0,1,
                                                                         1,0,1,0,1,0,1,0,
                                                                         1,0,1,1,0,0,1,1,
                                                                         1,1,0,0,1,0,0,0,
                                                                         1,1,0,1,0,0,0,0,
                                                                         1,1,1,0,1,0,1,0,
                                                                         1,1,1,1,0,0,0,0]);

array[0..15, 1..8] of 0..1: fixed_filter_forward = array2d(0..15, 1..8,[0,0,0,0,0,0,0,0,
                                                                        0,0,0,1,0,0,0,1,
                                                                        0,0,1,0,0,0,1,0,
                                                                        0,0,1,1,0,0,1,1,
                                                                        0,1,0,0,0,1,0,0,
                                                                        0,1,0,1,0,1,0,1,
                                                                        0,1,1,0,0,0,1,0,
                                                                        0,1,1,1,0,0,1,1,
                                                                        1,0,0,0,0,0,0,0,
                                                                        1,0,0,1,0,0,0,1,
                                                                        1,0,1,0,0,0,0,0,
                                                                        1,0,1,1,0,0,0,0,
                                                                        1,1,0,0,0,1,0,0,
                                                                        1,1,0,1,0,1,0,1,
                                                                        1,1,1,0,0,0,0,0,
                                                                        1,1,1,1,0,0,0,0]);

% 4-bit LFSR in tweakey schedule of SKINNY-64
array[0..15, 1..2] of int: lfsr_tk2_64 = array2d(0..15, 1..2, [0, 0, 1, 2, 2, 4, 3, 6, 4, 9, 5, 11, 6, 13, 7, 15, 8, 1, 9, 3, 10, 5, 11, 7, 12, 8, 13, 10, 14, 12, 15, 14]); % LFSR for TK2 tweakey schedule
array[0..15, 1..2] of int: lfsr_tk3_64 = array2d(0..15, 1..2, [0, 0, 1, 8, 2, 1, 3, 9, 4, 2, 5, 10, 6, 3, 7, 11, 8, 12, 9, 4, 10, 13, 11, 5, 12, 14, 13, 6, 14, 15, 15, 7]); % LFSR for TK3 tweakey schedule
array[0..15] of int: tweakey_permutation = array1d(0..15,[9,15,8,13,10,14,12,11,0,1,2,3,4,5,6,7]);
array[0..(Rone + RT - 1),0..15] of var int: tkperm_at_round;
constraint forall (i in 0..15) (tkperm_at_round[0, i] = i);
constraint forall (n in 1..(Rone + RT - 1), i in 0..15) (tkperm_at_round[n, i] = tweakey_permutation[tkperm_at_round[n - 1, i]]);
array[0..(Rone + RT - 1), 0..15] of var int: inv_tkp;
constraint forall(i in 0..15) (inv_tkp[0, i] = i);
constraint forall(r in 1..(Rone + RT - 1), i in 0..15)
(
    inv_tkp[r, i] = inv_tweakey_permutation[inv_tkp[r - 1, i]]
);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____                        _                  ____         _                _         _       
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  |_   _|__      __ ___   __ _ | | __ ___  _   _  / ___|   ___ | |__    ___   __| | _   _ | |  ___ 
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__|   | |  \ \ /\ / // _ \ / _` || |/ // _ \| | | | \___ \  / __|| '_ \  / _ \ / _` || | | || | / _ \
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |      | |   \ V  V /|  __/| (_| ||   <|  __/| |_| |  ___) || (__ | | | ||  __/| (_| || |_| || ||  __/
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|      |_|    \_/\_/  \___| \__,_||_|\_\\___| \__, | |____/  \___||_| |_| \___| \__,_| \__,_||_| \___|
%                                                                                                                            |___/                                                   

% tweakey line 1
array[0..15] of var 0..3: ASTK1;
array[0..15] of var -2..15: DSTK1;
constraint forall(i in 0..15) (link_difference(ASTK1[i], DSTK1[i]));

% tweakey line 2
array[0..15] of var 0..3: ASTK2;
array[0..(RT + Rone - 1), 0..15] of var -2..15: DSTK2;
constraint forall(i in 0..15) (link_difference(ASTK2[i], DSTK2[0, i]));

% tweakey line 3
array[0..15] of var 0..3: ASTK3;
array[0..(RT + Rone - 1), 0..15] of var -2..15: DSTK3;
constraint forall(i in 0..15) (link_difference(ASTK3[i], DSTK3[0, i]));

array[0..(RT + Rone - 1), 0..15] of var -2..15: DSTK2xor3;

% subtweakey
array[0..(RT + Rone - 1), 0..15] of var 0..3: ASTK;
array[0..(RT + Rone - 1), 0..15] of var -2..15: DSTK;
constraint forall(i in 0..(RT + Rone - 1), j in 0..15) (link_difference(ASTK[i, j], DSTK[i, j]));

constraint if NPT == 1 then 
(
    forall(i in 0..(RT + Rone - 1), j in 0..15) (DSTK[i, j] = DSTK1[tkperm_at_round[i, j]])
) elseif NPT == 2 then
(
    forall(i in 0..(RT + Rone - 2), j in 0..7) (table([DSTK2[i, tweakey_permutation[j]], DSTK2[i + 1, j]], lfsr_tk2_64)) /\
    forall(i in 0..(RT + Rone - 2), j in 8..15) (DSTK2[i + 1, j] = DSTK2[i, tweakey_permutation[j]]) /\
    forall(i in 0..(RT + Rone - 1), j in 0..15) (xor_nibbles(DSTK1[tkperm_at_round[i, j]], DSTK2[i, j], DSTK[i, j]))
) else
(
    forall(i in 0..(RT + Rone - 2), j in 0..7) (table([DSTK2[i, tweakey_permutation[j]], DSTK2[i + 1, j]], lfsr_tk2_64)) /\
    forall(i in 0..(RT + Rone - 2), j in 8..15) (DSTK2[i + 1, j] = DSTK2[i, tweakey_permutation[j]]) /\
    forall(i in 0..(RT + Rone - 2), j in 0..7) (table([DSTK3[i, tweakey_permutation[j]], DSTK3[i + 1, j]], lfsr_tk3_64)) /\
    forall(i in 0..(RT + Rone - 2), j in 8..15) (DSTK3[i + 1, j] = DSTK3[i, tweakey_permutation[j]]) /\
    forall(i in 0..(RT + Rone - 1), j in 0..15) (xor_nibbles(DSTK1[tkperm_at_round[i, j]], DSTK2[i, j], DSTK2xor3[i, j])) /\
    forall(i in 0..(RT + Rone - 1), j in 0..15) (xor_nibbles(DSTK2xor3[i, j], DSTK3[i, j], DSTK[i, j]))
) endif;

% constraint for the related-tweak vs. single-tweakey settings
constraint if (is_related_tweakey == false) then 
(
    sum(i in 0..(RT + Rone - 1), j in 0..15)(ASTK[i, j]) = 0
) endif;

% constraint for SKINNY-128-192
constraint if variant in 6..7 then 
(
    sum(i in 8..15)(ASTK2[i]) = 0
) endif;

% constraint for SKINNY-128-288
constraint if variant in 8..9 then 
(
    sum(i in 4..15)(ASTK3[i]) = 0
) endif;

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____  _   _ 
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  | ____|| | | |
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__| |  _|  | | | |
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |    | |___ | |_| |
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|    |_____| \___/ 
% constraints for EU

array[0..RD, 0..15] of var 0..3: AXU;
array[0..RD, 0..15] of var -2..15: DXU;
constraint forall(i in 0..RD, j in 0..15) (
    link_difference(AXU[i,j], DXU[i,j])
);

array[0..(RD - 1), 0..15] of var 0..3: AYU;
array[0..(RD - 1), 0..15] of var -2..15: DYU;
constraint forall(i in 0..(RD - 1), j in 0..15) (
    link_difference(AYU[i,j], DYU[i,j])
);

array[0..(RD - 1), 0..15] of var 0..3: AZU;
array[0..(RD - 1), 0..15] of var -2..15: DZU;
constraint forall(i in 0..(RD - 1), j in 0..15) (
    link_difference(AZU[i,j], DZU[i,j])
);

% exclude all-zero input difference
constraint sum(i in 0..15)(AXU[0, i]) + sum(i in 0..(RT + Rone - 1), j in 0..15)(ASTK[i, j]) != 0;

% S-box
constraint if (skip_first_sbox_layer) then 
(
    forall(i in 0..15)
    (
        AYU[0, i] = AXU[0, i] /\
        DYU[0, i] = DXU[0, i]
    )
) else 
(
    forall(i in 0..15)
    (
        sbox(AXU[0, i], AYU[0, i])
    )
) endif;

constraint forall(r in 1..(RD - 1), i in 0..15)
(
    sbox(AXU[r, i], AYU[r, i])
);

% xor with round tweakey
constraint forall(r in 0..(RD - 1), i in 0..7)
(
    if RB + r < Rzero then
    (
        xor_operation(AYU[r, i], DYU[r, i], ASTK[RB + r, i], DSTK[RB + r, i], AZU[r, i], DZU[r, i])
        /\
        AZU[r, i + 8] = AYU[r, i + 8]
        /\
        DZU[r, i + 8] = DYU[r, i + 8]
    ) else
    (
        xor_operation(AYU[r, i], DYU[r, i], ASTK[Rone + RB + r, i], DSTK[Rone + RB + r, i], AZU[r, i], DZU[r, i])
        /\
        AZU[r, i + 8] = AYU[r, i + 8]
        /\
        DZU[r, i + 8] = DYU[r, i + 8]
    ) endif
);

% mix-column and shift-rows
constraint forall(r in 0..(RD - 1), i in 0..3)
(
    mix_column_forward(AZU[r, round_permutation[i]], DZU[r, round_permutation[i]],
                       AZU[r, round_permutation[i + 4]], DZU[r, round_permutation[i + 4]],
                       AZU[r, round_permutation[i + 8]], DZU[r, round_permutation[i + 8]],
                       AZU[r, round_permutation[i + 12]], DZU[r, round_permutation[i + 12]],
                       AXU[r + 1, i], DXU[r + 1, i],
                       AXU[r + 1, i + 4], DXU[r + 1, i + 4],
                       AXU[r + 1, i + 8], DXU[r + 1, i + 8],
                       AXU[r + 1, i + 12], DXU[r + 1, i + 12])
);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____  _     
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  | ____|| |    
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__| |  _|  | |    
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |    | |___ | |___ 
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|    |_____||_____|
% constraints for EL

array[0..RD, 0..15] of var 0..3: AXL;
array[0..RD, 0..15] of var -2..15: DXL;
constraint forall(i in 0..RD, j in 0..15) (
    link_difference(AXL[i, j], DXL[i, j])
);

array[0..(RD - 1), 0..15] of var 0..3: AYL;
array[0..(RD - 1), 0..15] of var -2..15: DYL;
constraint forall(i in 0..(RD - 1), j in 0..15) (
    link_difference(AYL[i, j], DYL[i, j])
);

array[0..(RD - 1), 0..15] of var 0..3: AZL;
array[0..(RD - 1), 0..15] of var -2..15: DZL;
constraint forall(i in 0..(RD - 1), j in 0..15) (
    link_difference(AZL[i, j], DZL[i, j])
);

% exclude all-zero output difference
constraint sum(i in 0..15)(AXL[RD, i]) + sum(i in 0..(RT + Rone - 1), j in 0..15)(ASTK[i, j]) != 0;

% mix-column and shift-rows
constraint forall(r in 0..(RD - 1), i in 0..3)
(
    mix_column_backward(AXL[r + 1, i], DXL[r + 1, i],
                        AXL[r + 1, i + 4], DXL[r + 1, i + 4],
                        AXL[r + 1, i + 8], DXL[r + 1, i + 8],
                        AXL[r + 1, i + 12], DXL[r + 1, i + 12],
                        AZL[r, round_permutation[i]], DZL[r, round_permutation[i]],
                        AZL[r, round_permutation[i + 4]], DZL[r, round_permutation[i + 4]],
                        AZL[r, round_permutation[i + 8]], DZL[r, round_permutation[i + 8]],
                        AZL[r, round_permutation[i + 12]], DZL[r, round_permutation[i + 12]])
);

% xor with round tweakey
constraint forall(r in 0..(RD - 1), i in 0..7)
(
    if RB + r < Rzero then 
    (
        xor_operation(AZL[r, i], DZL[r, i], ASTK[RB + r, i], DSTK[RB + r, i], AYL[r, i], DYL[r, i])
        /\
        AYL[r, i + 8] = AZL[r, i + 8]
        /\
        DYL[r, i + 8] = DZL[r, i + 8]
    ) else
    (
        xor_operation(AZL[r, i], DZL[r, i], ASTK[Rone + RB + r, i], DSTK[Rone + RB + r, i], AYL[r, i], DYL[r, i])
        /\
        AYL[r, i + 8] = AZL[r, i + 8]
        /\
        DYL[r, i + 8] = DZL[r, i + 8]
    ) endif
);

% S-box
constraint forall(r in 0..(RD - 1), i in 0..15)
(
    sbox(AYL[r, i], AXL[r, i])
);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%  _____  _         _    _             ___  ___            __   ____   _       _    _                       _       _                 
% |  ___|(_)__  __ | |_ | |__    ___  |_ _|/ _ \    ___   / _| |  _ \ (_) ___ | |_ (_) _ __    __ _  _   _ (_) ___ | |__    ___  _ __ 
% | |_   | |\ \/ / | __|| '_ \  / _ \  | || | | |  / _ \ | |_  | | | || |/ __|| __|| || '_ \  / _` || | | || |/ __|| '_ \  / _ \| '__|
% |  _|  | | >  <  | |_ | | | ||  __/  | || |_| | | (_) ||  _| | |_| || |\__ \| |_ | || | | || (_| || |_| || |\__ \| | | ||  __/| |   
% |_|    |_|/_/\_\  \__||_| |_| \___| |___|\___/   \___/ |_|   |____/ |_||___/ \__||_||_| |_| \__, | \__,_||_||___/|_| |_| \___||_|   
%                                                                                             |___/                                   
% fix the input/output difference of distinguisher

% array[0..15] of 0..1: alpha = array1d(0..15, [0, 0, 0, 1,
%                                               0, 0, 0, 1,
%                                               0, 0, 0, 0,
%                                               0, 0, 0, 0]);
% constraint forall(i in 0..15)(AXU[0, i] = alpha[i]);


% array[0..15] of 0..1: delta = array1d(0..15, [1, 1, 0, 0,
%                                               1, 1, 0, 0,
%                                               0, 0, 0, 0,
%                                               1, 1, 0, 0]);
% constraint forall(i in 0..15)(AXL[RD, i] = delta[i]);

% array[0..15] of 0..1: input_tk_diff = array1d(0..15, [0, 0, 0, 0,
%                                                       0, 1, 0, 1,
%                                                       0, 0, 0, 0,
%                                                       0, 1, 0, 0]);
% constraint forall(i in 0..15)(ASTK[i] = input_tk_diff[i]);


% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                                   _                _    _              ____               _                    _  _        _    _               
%  / ___| _   _   __ _  _ __  __ _  _ __  | |_  ___   ___  | |_ | |__    ___   / ___| ___   _ __  | |_  _ __  __ _   __| |(_)  ___ | |_ (_)  ___   _ __  
% | |  _ | | | | / _` || '__|/ _` || '_ \ | __|/ _ \ / _ \ | __|| '_ \  / _ \ | |    / _ \ | '_ \ | __|| '__|/ _` | / _` || | / __|| __|| | / _ \ | '_ \ 
% | |_| || |_| || (_| || |  | (_| || | | || |_|  __/|  __/ | |_ | | | ||  __/ | |___| (_) || | | || |_ | |  | (_| || (_| || || (__ | |_ | || (_) || | | |
%  \____| \__,_| \__,_||_|   \__,_||_| |_| \__|\___| \___|  \__||_| |_| \___|  \____|\___/ |_| |_| \__||_|   \__,_| \__,_||_| \___| \__||_| \___/ |_| |_|
%                                                                                                                                        |___/                              
% constraints for the meeting point
array[0..RD] of var 0..16: contradict1;
array[0..RD] of var 0..16: contradict2;
constraint forall(r in 0..RD)
(
    contradict1[r] = sum(i in 0..15)(bool2int((AXU[r, i] + AXL[r, i] > 0) /\ (AXU[r, i] + AXL[r, i] < 3) /\ (AXU[r, i] != AXL[r, i]))) /\
    contradict2[r] = sum(i in 0..15)(bool2int(AXU[r, i] == 1 /\ AXL[r, i] == 1 /\ (DXU[r, i] != DXL[r, i])))
);
var 0..(16*RD): contradict;
constraint contradict = sum(r in 0..RD)(contradict1[r] + contradict2[r]);
constraint contradict > 0;

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____  ____  
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  | ____|| __ ) 
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__| |  _|  |  _ \ 
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |    | |___ | |_) |
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|    |_____||____/ 
% constraints for EB

array[0..RB, 0..15] of var 0..1: AXB;
array[0..(RB - 1), 0..15] of var 0..1: AZB;
constraint forall(i in 0..15) (
    if AXU[0, i] != 0 then AXB[RB, i] = 1 else AXB[RB, i] = 0 endif
);
constraint forall(r in 0..(RB - 1), i in 0..3)
(
    MinvdiffD(AXB[r + 1, i], AXB[r + 1, i + 4], AXB[r + 1, i + 8], AXB[r + 1, i + 12],
              AZB[r, round_permutation[i]], AZB[r, round_permutation[i + 4]], AZB[r, round_permutation[i + 8]], AZB[r, round_permutation[i + 12]])
);
constraint forall (r in 0..(RB - 1), i in 0..7)
(
    if r < Rzero then 
    (
        XORD(AZB[r, i], ASTK[r, i], AXB[r, i])
    ) else
    (
        XORD(AZB[r, i], ASTK[Rone + r, i], AXB[r, i])
    ) endif
    /\
    AXB[r, i + 8] = AZB[r, i + 8]
);

%##################################################################################
% model the propagation of the fixed differences and encoding the filters

array[0..RB, 0..15] of var 0..1: IsFixedDXB;
array[0..(RB - 1), 0..15] of var 0..1: IsFixedDZB;
constraint forall(r in 0..RB, i in 0..15) (IsFixedDXB[r, i] = 1 - AXB[r, i]);
constraint forall(r in 0..(RB - 1), i in 0..3)
(
    Minvfixed(IsFixedDXB[r + 1, i], IsFixedDXB[r + 1, i + 4], IsFixedDXB[r + 1, i + 8], IsFixedDXB[r + 1, i + 12],
              IsFixedDZB[r, round_permutation[i]], IsFixedDZB[r, round_permutation[i + 4]], IsFixedDZB[r, round_permutation[i + 8]], IsFixedDZB[r, round_permutation[i + 12]])
);
array[0..RB, 0..15] of var 0..1: FilterXB;
array[0..(RB - 1), 0..15] of var 0..1: FilterZB;
constraint forall(r in 0..(RB - 1), i in 0..3) (table([IsFixedDXB[r + 1, i], IsFixedDXB[r + 1, i + 4], IsFixedDXB[r + 1, i + 8], IsFixedDXB[r + 1, i + 12],
                                                       FilterXB[r + 1, i], FilterXB[r + 1, i + 4], FilterXB[r + 1, i + 8], FilterXB[r + 1, i + 12]],
                                                       fixed_filter_backward));
constraint forall(r in 0..(RB - 1), i in 0..15) (FilterZB[r, i] = bool2int(IsFixedDZB[r, i] + AXB[r, i] == 2));

%##################################################################################
% model the guess-and-determine in EB for checking all filters

array[0..RB, 0..15] of var 0..1: KXB;
% constraint forall(i in 0..15) (KXB[RB, i] = 0);
array[0..RB, 0..15] of var 0..1: KDXB;
constraint forall(r in 0..RB, i in 0..15) (KDXB[r, i] <= AXB[r, i]);
array[0..(RB - 1), 0..15] of var 0..1: KDZB;
constraint forall(r in 0..(RB - 1), i in 0..15) (KDZB[r, i] <= AZB[r, i]);
array[0..(RB - 1), 0..15] of var 0..1: KZB;
array[0..(RB - 1), 0..15] of var 0..1: IKB;

constraint forall(r in 0..(RB - 1), i in 0..3)
(
    if (KDXB[r + 1, i] + FilterXB[r + 1, i] >= 1) then
    (
        KDZB[r, round_permutation[i]] = AZB[r, round_permutation[i]]
        /\
        KDZB[r, round_permutation[i + 8]] = AZB[r, round_permutation[i + 8]]
        /\
        KDZB[r, round_permutation[i + 12]] = AZB[r, round_permutation[i + 12]]
    ) endif
    /\
    if (KDXB[r + 1, i + 4] + FilterXB[r + 1, i + 4] >= 1) then 
    (
        KDZB[r, round_permutation[i]] = AZB[r, round_permutation[i]]
    ) endif
    /\
    if (KDXB[r + 1, i + 8] + FilterXB[r + 1, i + 8] >= 1) then 
    (
        KDZB[r, round_permutation[i + 4]] = AZB[r, round_permutation[i + 4]]
        /\
        KDZB[r, round_permutation[i + 8]] = AZB[r, round_permutation[i + 8]]
    ) endif
    /\
    if (KDXB[r + 1, i + 12] + FilterXB[r + 1, i + 12] >= 1) then 
    (
        KDZB[r, round_permutation[i]] = AZB[r, round_permutation[i]]
        /\
        KDZB[r, round_permutation[i + 8]] = AZB[r, round_permutation[i + 8]]
    ) endif
);
constraint forall(r in 0..(RB - 1), i in 0..15)
(    
    % if (FilterZB[r, i] == 1) then KDZB[r, i] = 1 endif
    % /\
    XORD(KDZB[r, i], FilterZB[r, i], KDXB[r, i])
);
constraint forall(r in 0..(RB - 1), i in 0..3)
(
    Minvgd(KXB[r + 1, i], KXB[r + 1, i + 4], KXB[r + 1, i + 8], KXB[r + 1, i + 12],
           KZB[r, round_permutation[i]], KZB[r, round_permutation[i + 4]], KZB[r, round_permutation[i + 8]], KZB[r, round_permutation[i + 12]])
);
constraint forall(r in 0..(RB - 1), i in 0..15)
(
    XORD3(KZB[r, i], KDZB[r, i], FilterZB[r, i], KXB[r, i])
);

constraint if RB >= 1 then (
    IKB[0, 0] >= KXB[1, 0]
    /\
    IKB[0, 0] >= KXB[1, 4]
    /\

    IKB[0, 0] >= KXB[1, 12]
    /\
    IKB[0, 0] <= KXB[1, 0] + KXB[1, 4] + KXB[1, 12]
    /\
    IKB[0, 1] >= KXB[1, 1]
    /\
    IKB[0, 1] >= KXB[1, 5]
    /\
    IKB[0, 1] >= KXB[1, 13]
    /\
    IKB[0, 1] <= KXB[1, 1] + KXB[1, 5] + KXB[1, 13]
    /\
    IKB[0, 2] >= KXB[1, 2]
    /\
    IKB[0, 2] >= KXB[1, 6]
    /\
    IKB[0, 2] >= KXB[1, 14]
    /\
    IKB[0, 2] <= KXB[1, 2] + KXB[1, 6] + KXB[1, 14]
    /\
    IKB[0, 3] >= KXB[1, 3]
    /\
    IKB[0, 3] >= KXB[1, 7]
    /\
    IKB[0, 3] >= KXB[1, 15]
    /\
    IKB[0, 3] <= KXB[1, 3] + KXB[1, 7] + KXB[1, 15]
    /\
    IKB[0, 7] = KXB[1, 8]
    /\
    IKB[0, 4] = KXB[1, 9]
    /\
    IKB[0, 5] = KXB[1, 10]
    /\
    IKB[0, 6] = KXB[1, 11]
    /\
    forall(i in 8..15) (IKB[0, i] = 0)
) endif;
constraint forall(r in 1..(RB - 1), i in 0..7) 
(
    IKB[r, i] = KZB[r, i] /\ IKB[r, i + 8] = 0
);

%##################################################################################
% model the guess-and-determine in EB for checking the fast filters

array[0..RB, 0..15] of var 0..1: GXB;
% constraint forall(i in 0..15) (GXB[RB, i] = 0);
constraint forall(r in 0..RB, i in 0..15) (GXB[r, i] <= KXB[r, i]);
array[0..RB, 0..15] of var 0..1: GDXB;
constraint forall(r in 0..RB, i in 0..15) (GDXB[r, i] <= AXB[r, i]);
array[0..(RB - 1), 0..15] of var 0..1: GZB;
constraint forall(r in 0..(RB - 1), i in 0..15) (GZB[r, i] <= KZB[r, i]);
array[0..(RB - 1), 0..15] of var 0..1: GDZB;
constraint forall(r in 0..(RB - 1), i in 0..15) (GDZB[r, i] <= AZB[r, i]);
array[0..(RB - 1), 0..15] of var 0..1: GIKB;
constraint forall(r in 0..(RB - 1), i in 0..15) (GIKB[r, i] <= IKB[r, i]);
array[0..RB, 0..15] of var 0..1: IsFilterXB;
constraint forall(r in 0..RB, i in 0..15) (IsFilterXB[r, i] <= FilterXB[r, i]);
array[0..(RB - 1), 0..15] of var 0..1: IsFilterZB;
constraint forall(r in 0..(RB - 1), i in 0..15) (IsFilterZB[r, i] <= FilterZB[r, i]);
constraint forall(r in 0..(RB - 1), i in 0..3)
(
    if (GDXB[r + 1, i] + IsFilterXB[r + 1, i] >= 1) then
    (
        GDZB[r, round_permutation[i]] = AZB[r, round_permutation[i]]
        /\
        GDZB[r, round_permutation[i + 8]] = AZB[r, round_permutation[i + 8]]
        /\
        GDZB[r, round_permutation[i + 12]] = AZB[r, round_permutation[i + 12]]
    ) endif
    /\
    if (GDXB[r + 1, i + 4] + IsFilterXB[r + 1, i + 4] >= 1) then 
    (
        GDZB[r, round_permutation[i]] = AZB[r, round_permutation[i]]
    ) endif
    /\
    if (GDXB[r + 1, i + 8] + IsFilterXB[r + 1, i + 8] >= 1) then 
    (
        GDZB[r, round_permutation[i + 4]] = AZB[r, round_permutation[i + 4]]
        /\
        GDZB[r, round_permutation[i + 8]] = AZB[r, round_permutation[i + 8]]
    ) endif
    /\
    if (GDXB[r + 1, i + 12] + IsFilterXB[r + 1, i + 12] >= 1) then 
    (
        GDZB[r, round_permutation[i]] = AZB[r, round_permutation[i]]
        /\
        GDZB[r, round_permutation[i + 8]] = AZB[r, round_permutation[i + 8]]
    ) endif
);
constraint forall(r in 0..(RB - 1), i in 0..15)
(
    % if (IsFilterZB[r, i] == 1) then GDZB[r, i] = 1 endif
    % /\
    XORD(GDZB[r, i], IsFilterZB[r, i], GDXB[r, i])
);
constraint forall(r in 0..(RB - 1), i in 0..3)
(
    Minvgd(GXB[r + 1, i], GXB[r + 1, i + 4], GXB[r + 1, i + 8], GXB[r + 1, i + 12],
           GZB[r, round_permutation[i]], GZB[r, round_permutation[i + 4]], GZB[r, round_permutation[i + 8]], GZB[r, round_permutation[i + 12]])
);
constraint forall(r in 0..(RB - 1), i in 0..15)
(
    XORD3(GZB[r, i], GDZB[r, i], IsFilterZB[r, i], GXB[r, i])
);

constraint if RB >= 1 then
(
    GIKB[0, 0] >= GXB[1, 0]
    /\
    GIKB[0, 0] >= GXB[1, 4]
    /\
    GIKB[0, 0] >= GXB[1, 12]
    /\
    GIKB[0, 0] <= GXB[1, 0] + GXB[1, 4] + GXB[1, 12]
    /\
    GIKB[0, 1] >= GXB[1, 1]
    /\
    GIKB[0, 1] >= GXB[1, 5]
    /\
    GIKB[0, 1] >= GXB[1, 13]
    /\
    GIKB[0, 1] <= GXB[1, 1] + GXB[1, 5] + GXB[1, 13]
    /\
    GIKB[0, 2] >= GXB[1, 2]
    /\
    GIKB[0, 2] >= GXB[1, 6]
    /\
    GIKB[0, 2] >= GXB[1, 14]
    /\
    GIKB[0, 2] <= GXB[1, 2] + GXB[1, 6] + GXB[1, 14]
    /\
    GIKB[0, 3] >= GXB[1, 3]
    /\
    GIKB[0, 3] >= GXB[1, 7]
    /\
    GIKB[0, 3] >= GXB[1, 15]
    /\
    GIKB[0, 3] <= GXB[1, 3] + GXB[1, 7] + GXB[1, 15]
    /\
    GIKB[0, 7] = GXB[1, 8]
    /\
    GIKB[0, 4] = GXB[1, 9]
    /\
    GIKB[0, 5] = GXB[1, 10]
    /\
    GIKB[0, 6] = GXB[1, 11]
    /\
    forall(i in 8..15) (GIKB[0, i] = 0)
) endif;
constraint forall(r in 1..(RB - 1), i in 0..7) (
    GIKB[r, i] = GZB[r, i] /\ GIKB[r, i + 8] = 0
);

% #############################################################################################################################################
% determine the filters at the boundary of EB and EU
array[0..19] of var 0..1: CB;
array[0..19] of var 0..1: IsCB;
constraint forall(i in 0..19) (IsCB[i] <= CB[i]);
array[0..1, 0..15] of var 0..1: AXBU;
array[0..0, 0..15] of var 0..1: AZBU;

constraint forall(r in 0..1, i in 0..15) (AXBU[r, i] = bool2int(AXU[r, i] != 0));
constraint forall(r in 0..0, i in 0..15) (AZBU[r, i] = bool2int(AZU[0, i] != 0));

constraint forall(r in 0..0, i in 0..3)
(
    XOR_P(AZBU[r, round_permutation[i + 4]], AZBU[r, round_permutation[i + 8]], AXBU[r + 1, i + 8], CB[i])
    /\
    XOR_P(AZBU[r, round_permutation[i]], AZBU[r, round_permutation[i + 8]], AXBU[r + 1, i + 12], CB[i + 4])
    /\
    XOR_P(AXBU[r + 1, i + 12], AZBU[r, round_permutation[i + 12]], AXBU[r + 1, i], CB[i + 8])
);

constraint forall(r in 0..0, i in 0..7)
(
    if RB + r < Rzero then
    (
        XOR_P(AXBU[r, i], ASTK[RB + r, i], AZBU[r, i], CB[i + 12])
    ) else
    (
        XOR_P(AXBU[r, i], ASTK[Rone + RB + r, i], AZBU[r, i], CB[i + 12])
    ) endif
);

constraint forall(i in 0..3)
(
    if (CB[i] == 1) then 
    (
        KDXB[RB, round_permutation[i + 4]] = AXB[RB, round_permutation[i + 4]]
        /\
        KDXB[RB, round_permutation[i + 8]] = AXB[RB, round_permutation[i + 8]]
    ) endif
    /\
    if (CB[i + 4] == 1) then 
    (
        KDXB[RB, round_permutation[i]] = AXB[RB, round_permutation[i]]
        /\
        KDXB[RB, round_permutation[i + 8]] = AXB[RB, round_permutation[i + 8]]
    ) endif
    /\
    if (CB[i + 8] == 1) then 
    (
        KDXB[RB, round_permutation[i]] = AXB[RB, round_permutation[i]]
        /\
        KDXB[RB, round_permutation[i + 8]] = AXB[RB, round_permutation[i + 8]]
        /\
        KDXB[RB, round_permutation[i + 12]] = AXB[RB, round_permutation[i + 12]]
    ) endif
);

constraint forall(i in 0..7)
(
    if CB[i + 12] == 1 then KDXB[RB, i] = AXB[RB, i] endif
);

constraint forall(i in 0..15)
(
    if KDXB[RB, i] == 1 then KXB[RB, i] = 1 else KXB[RB, i] = 0 endif
);

constraint forall(i in 0..3)
(
    if (IsCB[i] == 1) then 
    (
        GDXB[RB, round_permutation[i + 4]] = AXB[RB, round_permutation[i + 4]]
        /\
        GDXB[RB, round_permutation[i + 8]] = AXB[RB, round_permutation[i + 8]]
    ) endif
    /\
    if (IsCB[i + 4] == 1) then 
    (
        GDXB[RB, round_permutation[i]] = AXB[RB, round_permutation[i]]
        /\
        GDXB[RB, round_permutation[i + 8]] = AXB[RB, round_permutation[i + 8]]
    ) endif
    /\
    if (IsCB[i + 8] == 1) then 
    (
        GDXB[RB, round_permutation[i]] = AXB[RB, round_permutation[i]]
        /\
        GDXB[RB, round_permutation[i + 8]] = AXB[RB, round_permutation[i + 8]]
        /\
        GDXB[RB, round_permutation[i + 12]] = AXB[RB, round_permutation[i + 12]]
    ) endif
);

constraint forall(i in 0..7)
(
    if IsCB[i + 12] == 1 then GDXB[RB, i] = AXB[RB, i] endif
);

constraint forall(i in 0..15)
(
    if GDXB[RB, i] == 1 then GXB[RB, i] = 1 else GXB[RB, i] = 0 endif
);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____  _____ 
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  | ____||  ___|
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__| |  _|  | |_   
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |    | |___ |  _|  
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|    |_____||_|    
% constraints for EF

array[0..RF, 0..15] of var 0..1: AXF;
array[0..(RF - 1), 0..15] of var 0..1: AZF;
constraint forall(i in 0..15) (
    if AXL[RD, i] != 0 then AXF[0, i] = 1 else AXF[0, i] = 0 endif
);
constraint forall(r in 0..(RF - 1), i in 0..7)
(
    if RB + RD + r < Rzero then
    (
        XORD(AXF[r, i], ASTK[RB + RD + r, i], AZF[r, i])
    ) else
    (
        XORD(AXF[r, i], ASTK[Rone + RB + RD + r, i], AZF[r, i])
    ) endif
    /\
    AZF[r, i + 8] = AXF[r, i + 8]
);
constraint forall(r in 0..(RF - 1), i in 0..3)
(
    MdiffD(AZF[r, round_permutation[i]], AZF[r, round_permutation[i + 4]], AZF[r, round_permutation[i + 8]], AZF[r, round_permutation[i + 12]],
           AXF[r + 1, i], AXF[r + 1, i + 4], AXF[r + 1, i + 8], AXF[r + 1, i + 12])
);

%##################################################################################
% model the propagation of the fixed differences and encoding the filters

array[0..RF, 0..15] of var 0..1: IsFixedDXF;
array[0..(RF - 1), 0..15] of var 0..1: IsFixedDZF;
constraint forall(i in 0..15) (
    if AXL[RD, i] <= 1 then IsFixedDXF[0, i] = 1 else IsFixedDXF[0, i] = 0 endif
);
constraint forall(r in 0..(RF - 1), i in 0..15) (IsFixedDZF[r, i] = (1 - AXF[r, i]));
constraint forall(r in 0..(RF - 1), i in 0..3)
(
    Mfixed(IsFixedDZF[r, round_permutation[i]], IsFixedDZF[r, round_permutation[i + 4]], IsFixedDZF[r, round_permutation[i + 8]], IsFixedDZF[r, round_permutation[i + 12]],
           IsFixedDXF[r + 1, i], IsFixedDXF[r + 1, i + 4], IsFixedDXF[r + 1, i + 8], IsFixedDXF[r + 1, i + 12])
);

array[0..RF, 0..15] of var 0..1: FilterXF;
array[0..(RF - 1), 0..15] of var 0..1: FilterZF;

constraint forall(i in 0..15) (FilterXF[0, i] = 0);
constraint forall(r in 1..(RF - 1), i in 0..15) (FilterXF[r, i] = bool2int(IsFixedDXF[r, i] + AXF[r, i] == 2));
constraint forall(r in 0..(RF - 1), i in 0..3) (table([IsFixedDZF[r, round_permutation[i]], IsFixedDZF[r, round_permutation[i + 4]], IsFixedDZF[r, round_permutation[i + 8]], IsFixedDZF[r, round_permutation[i + 12]], 
                                                       FilterZF[r, round_permutation[i]], FilterZF[r, round_permutation[i + 4]], FilterZF[r, round_permutation[i + 8]], FilterZF[r, round_permutation[i + 12]]], 
                                                       fixed_filter_forward));

%##################################################################################
% model the guess-and-determine in EF for checking all filters

array[0..RF, 0..15] of var 0..1: KXF;
constraint forall(i in 0..15) (KXF[0, i] = 0);
array[0..RF, 0..15] of var 0..1: KDXF;
constraint forall(r in 0..RF, i in 0..15) (KDXF[r, i] <= AXF[r, i]);
constraint forall(i in 0..15) (if AXL[RD, i] == 1 then KDXF[0, i] = 1 else KDXF[0, i] = 0 endif);
array[0..(RF - 1), 0..15] of var 0..1: KZF;
array[0..(RF - 1), 0..15] of var 0..1: KDZF;
constraint forall(r in 0..(RF - 1), i in 0..15) (KDZF[r, i] <= AZF[r, i]);
array[0..(RF - 1), 0..15] of var 0..1: IKF;
constraint forall(r in 0..(RF - 1), i in 0..15)
(
    if (FilterXF[r, i] == 1) then KDXF[r, i] = 1 endif
    /\
    XORD(KDXF[r, i], FilterXF[r, i], KDZF[r, i])
);
constraint forall(r in 0..(RF - 1), i in 0..3)
(
    if (KDZF[r, round_permutation[i]] + FilterZF[r, round_permutation[i]] >= 1) then 
    (
        KDXF[r + 1, i + 4] = AXF[r + 1, i + 4] 
    ) endif
    /\
    if (KDZF[r, round_permutation[i + 4]] + FilterZF[r, round_permutation[i + 4]] >= 1) then 
    (
        KDXF[r + 1, i + 4] = AXF[r + 1, i + 4]
        /\
        KDXF[r + 1, i + 8] = AXF[r + 1, i + 8]
        /\
        KDXF[r + 1, i + 12] = AXF[r + 1, i + 12]
    ) endif
    /\
    if (KDZF[r, round_permutation[i + 8]] + FilterZF[r, round_permutation[i + 8]] >= 1) then
    (
        KDXF[r + 1, i + 4] = AXF[r + 1, i + 4]
        /\
        KDXF[r + 1, i + 12] = AXF[r + 1, i + 12]
    ) endif
    /\
    if (KDZF[r, round_permutation[i + 12]] + FilterZF[r, round_permutation[i + 12]] >= 1) then
    (
        KDXF[r + 1, i] = AXF[r + 1, i]
        /\
        KDXF[r + 1, i + 12] = AXF[r + 1, i + 12]
    ) endif    
);
constraint forall(r in 0..(RF - 1), i in 0..15)
(
    XORD(KXF[r, i], KDXF[r, i], KZF[r, i])
);
constraint forall(r in 0..(RF - 1), i in 0..7)
(
    IKF[r, i] = KZF[r, i] /\ IKF[r, i + 8] = 0
);
constraint forall(r in 0..(RF - 1), i in 0..3)
(
    Mgd(KZF[r, round_permutation[i]], KZF[r, round_permutation[i + 4]], KZF[r, round_permutation[i + 8]], KZF[r, round_permutation[i + 12]],
        KXF[r + 1, i], KXF[r + 1, i + 4], KXF[r + 1, i + 8], KXF[r + 1, i + 12])
);
%##################################################################################
% model the guess-and-determine in EF for fast filters

array[0..RF, 0..15] of var 0..1: GXF;
constraint forall(r in 0..RF, i in 0..15) (GXF[r, i] <= KXF[r, i]);
array[0..RF, 0..15] of var 0..1: GDXF;
constraint forall(r in 0..RF, i in 0..15) (GDXF[r, i] <= KDXF[r, i]);
array[0..(RF - 1), 0..15] of var 0..1: GZF;
constraint forall(r in 0..(RF - 1), i in 0..15) (GZF[r, i] <= KZF[r, i]);
array[0..(RF - 1), 0..15] of var 0..1: GDZF;
constraint forall(r in 0..(RF - 1), i in 0..15) (GDZF[r, i] <= KDZF[r, i]);
array[0..(RF - 1), 0..15] of var 0..1: GIKF;
constraint forall(r in 0..(RF -  1), i in 0..15) (GIKF[r, i] <= IKF[r, i]);
array[0..RF, 0..15] of var 0..1: IsFilterXF;
constraint forall(r in 0..RF, i in 0..15)(IsFilterXF[r, i] <= FilterXF[r, i]);
array[0..(RF - 1), 0..15] of var 0..1: IsFilterZF;
constraint forall(r in 0..(RF - 1), i in 0..15)(IsFilterZF[r, i] <= FilterZF[r, i]);
constraint forall(r in 0..(RF - 1), i in 0..15)
(
    if (IsFilterXF[r, i] == 1) then GDXF[r, i] = 1 endif
    /\
    XORD(GDXF[r, i], IsFilterXF[r, i], GDZF[r, i])
);
constraint forall(r in 0..(RF - 1), i in 0..3)
(
    if (GDZF[r, round_permutation[i]] + IsFilterZF[r, round_permutation[i]] >= 1) then 
    (
        GDXF[r + 1, i + 4] = AXF[r + 1, i + 4] 
    ) endif
    /\
    if (GDZF[r, round_permutation[i + 4]] + IsFilterZF[r, round_permutation[i + 4]] >= 1) then 
    (
        GDXF[r + 1, i + 4] = AXF[r + 1, i + 4]
        /\
        GDXF[r + 1, i + 8] = AXF[r + 1, i + 8]
        /\
        GDXF[r + 1, i + 12] = AXF[r + 1, i + 12]
    ) endif
    /\
    if (GDZF[r, round_permutation[i + 8]] + IsFilterZF[r, round_permutation[i + 8]] >= 1) then
    (
        GDXF[r + 1, i + 4] = AXF[r + 1, i + 4]
        /\
        GDXF[r + 1, i + 12] = AXF[r + 1, i + 12]
    ) endif
    /\
    if (GDZF[r, round_permutation[i + 12]] + IsFilterZF[r, round_permutation[i + 12]] >= 1) then
    (
        GDXF[r + 1, i] = AXF[r + 1, i]
        /\
        GDXF[r + 1, i + 12] = AXF[r + 1, i + 12]
    ) endif    
);
constraint forall(r in 0..(RF - 1), i in 0..15)
(
    XORD(GXF[r, i], GDXF[r, i], GZF[r, i])
);
constraint forall(r in 0..(RF - 1), i in 0..7)
(
    GIKF[r, i] = GZF[r, i] /\ GIKF[r, i + 8] = 0
);
constraint forall(r in 0..(RF - 1), i in 0..3)
(
    Mgd(GZF[r, round_permutation[i]], GZF[r, round_permutation[i + 4]], GZF[r, round_permutation[i + 8]], GZF[r, round_permutation[i + 12]],
        GXF[r + 1, i], GXF[r + 1, i + 4], GXF[r + 1, i + 8], GXF[r + 1, i + 12])
);
% #############################################################################################################################################
% determine the number of filters at the boundary of EL and EF
array[0..19] of var 0..1: CF;
array[0..1, 0..15] of var 0..1: AXFL;
array[0..0, 0..15] of var 0..1: AZFL;
constraint forall(r in 0..1, i in 0..15) (AXFL[r, i] = bool2int(AXL[RD - 1 + r, i] != 0));
constraint forall(r in 0..0, i in 0..15) (AZFL[r, i] = bool2int(AZL[RD - 1, i] != 0));

constraint forall(r in 0..0, i in 0..7)
(
    if RB + RD - 1 + r < Rzero then
    (
        XOR_P(AZFL[r, i], ASTK[RB + RD - 1 + r, i], AXFL[r, i], CF[i])
    ) else
    (
        XOR_P(AZFL[r, i], ASTK[Rone + RB + RD - 1 + r, i], AXFL[r, i], CF[i])
    ) endif    
);

constraint forall(r in 0..0, i in 0..3)
(
    XOR_P(AZFL[r, round_permutation[i + 8]], AXFL[r + 1, i + 8], AZFL[r, round_permutation[i + 4]], CF[i + 8])
    /\
    XOR_P(AXFL[r + 1, i + 4], AXFL[r + 1, i + 12], AZFL[r, round_permutation[i + 8]], CF[i + 12])
    /\
    XOR_P(AXFL[r + 1, i], AXFL[r + 1, i + 12], AZFL[r, round_permutation[i + 12]], CF[i + 16])
);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%  _  __                    ____         _      _         _               
% | |/ / ___  _   _        | __ )  _ __ (_)  __| |  __ _ (_) _ __    __ _ 
% | ' / / _ \| | | | _____ |  _ \ | '__|| | / _` | / _` || || '_ \  / _` |
% | . \|  __/| |_| ||_____|| |_) || |   | || (_| || (_| || || | | || (_| |
% |_|\_\\___| \__, |       |____/ |_|   |_| \__,_| \__, ||_||_| |_| \__, |
%             |___/                                |___/            |___/ 
% constraints for key-bridging

array[0..15] of var 0..(RB + RF): IK;
array[0..15] of var 0..NPT: KE;
var 0..(NPT*16): KS;
array[0..15] of var 0..(RB + RF): GIK;
array[0..15] of var 0..NPT: GKE;
var 0..(NPT*16): GKS;

constraint forall(i in 0..15)
(
    IK[i] = sum(r in 0..(RB - 1) where r < Rzero)(IKB[r, inv_tkp[r, i]]) + 
            sum(r in 0..(RB - 1) where r >= Rzero)(IKB[r, inv_tkp[Rone + r, i]]) + 
            sum(r in 0..(RF - 1) where RB + RD + r < Rzero)(IKF[r, inv_tkp[RB + RD + r, i]]) +
            sum(r in 0..(RF - 1) where RB + RD + r >= Rzero)(IKF[r, inv_tkp[Rone + RB + RD + r, i]])
);

constraint if variant < 5 then
(
    forall(i in 0..15)
    (
        if (IK[i] >= GuessingThreshold1) then (KE[i] = GuessingThreshold1) else (KE[i] = IK[i]) endif
    )
) elseif variant == 5 then 
(
    forall(i in 0..15)
    (
        if (IK[i] >= GuessingThreshold1) then (KE[i] = GuessingThreshold1) else (KE[i] = IK[i]) endif
    )
) elseif variant == 6 then 
(
    forall(i in 0..7)
    (
        if (IK[i] >= GuessingThreshold1) then (KE[i] = GuessingThreshold1) else (KE[i] = IK[i]) endif
    )
    /\
    forall(i in 8..15)
    (
        if (IK[i] >= GuessingThreshold2) then (KE[i] = GuessingThreshold2) else (KE[i] = IK[i]) endif
    )
) elseif variant == 7 then 
(
    forall(i in 0..15)
    (
        if (IK[i] >= GuessingThreshold1) then (KE[i] = GuessingThreshold1) else (KE[i] = IK[i]) endif
    )
) elseif variant == 8 then 
(
    forall(i in 0..3)
    (
        if (IK[i] >= GuessingThreshold1) then (KE[i] = GuessingThreshold1) else (KE[i] = IK[i]) endif
    )
    /\
    forall(i in 4..15)
    (
        if (IK[i] >= GuessingThreshold2) then (KE[i] = GuessingThreshold2) else (KE[i] = IK[i]) endif
    )
) else
(
    forall(i in 0..15)
    (
        if (IK[i] >= GuessingThreshold1) then (KE[i] = GuessingThreshold1) else (KE[i] = IK[i]) endif
    )
) endif;

constraint KS = sum(i in 0..15)(KE[i]);

%##################################################################################

constraint forall(i in 0..15)
(
    GIK[i] = sum(r in 0..(RB - 1) where r < Rzero)(GIKB[r, inv_tkp[r, i]]) +
             sum(r in 0..(RB - 1) where r >= Rzero)(GIKB[r, inv_tkp[Rone + r, i]]) + 
             sum(r in 0..(RF - 1) where RB + RD + r < Rzero)(GIKF[r, inv_tkp[RB + RD + r, i]]) + 
             sum(r in 0..(RF - 1) where RB + RD + r >= Rzero)(GIKF[r, inv_tkp[Rone + RB + RD + r, i]])
);

% please look at the above consitariant for IK and KE and repeat them for GIK and GKE
constraint if variant < 5 then 
(
    forall(i in 0..15)
    (
        if (GIK[i] >= GuessingThreshold1) then (GKE[i] = GuessingThreshold1) else (GKE[i] = GIK[i]) endif
    )
) elseif variant == 5 then 
(
    forall(i in 0..15)
    (
        if (GIK[i] >= GuessingThreshold1) then (GKE[i] = GuessingThreshold1) else (GKE[i] = GIK[i]) endif
    )
) elseif variant == 6 then 
(
    forall(i in 0..7)
    (
        if (GIK[i] >= GuessingThreshold1) then (GKE[i] = GuessingThreshold1) else (GKE[i] = GIK[i]) endif
    )
    /\
    forall(i in 8..15)
    (
        if (GIK[i] >= GuessingThreshold2) then (GKE[i] = GuessingThreshold2) else (GKE[i] = GIK[i]) endif
    )
) elseif variant == 7 then 
(
    forall(i in 0..15)
    (
        if (GIK[i] >= GuessingThreshold1) then (GKE[i] = GuessingThreshold1) else (GKE[i] = GIK[i]) endif
    )
) elseif variant == 8 then 
(
    forall(i in 0..3)
    (
        if (GIK[i] >= GuessingThreshold1) then (GKE[i] = GuessingThreshold1) else (GKE[i] = GIK[i]) endif
    )
    /\
    forall(i in 4..15)
    (
        if (GIK[i] >= GuessingThreshold2) then (GKE[i] = GuessingThreshold2) else (GKE[i] = GIK[i]) endif
    )
) else
(
    forall(i in 0..15)
    (
        if (GIK[i] >= GuessingThreshold1) then (GKE[i] = GuessingThreshold1) else (GKE[i] = GIK[i]) endif
    )
) endif;

constraint GKS = sum(i in 0..15)(GKE[i]);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                          _              _  _               _                   _              _      
%  / ___| ___   _ __ ___   _ __  | |  ___ __  __(_)| |_  _   _     / \    _ __    __ _ | | _   _  ___ (_) ___ 
% | |    / _ \ | '_ ` _ \ | '_ \ | | / _ \\ \/ /| || __|| | | |   / _ \  | '_ \  / _` || || | | |/ __|| |/ __|
% | |___| (_) || | | | | || |_) || ||  __/ >  < | || |_ | |_| |  / ___ \ | | | || (_| || || |_| |\__ \| |\__ \
%  \____|\___/ |_| |_| |_|| .__/ |_| \___|/_/\_\|_| \__| \__, | /_/   \_\|_| |_| \__,_||_| \__, ||___/|_||___/
%                         |_|                            |___/                             |___/              
% constraints for complexity analysis

var 0..(RB*32 + 32): CB_tot;
var 0..(RF*32 + 32): CF_tot;
var 0..(RB*32 + 32): FCB_tot;
var 0..(RF*32 + 32): FCF_tot;
var 0..16: WB;
var 0..16: WF;
var 0..9: log_2_minus_053_of_g;
var 1..384: g;
var 0..384: key_size;
array[0..3] of var 0..384: data_complexity;
var 0..384: memory_complexity;
array[0..3] of var 0..384: t_complexity;
var 0..384: max_term;
var 0..16: no_of_active_cells_in_tk1;
constraint no_of_active_cells_in_tk1 = sum(i in 0..15)(ASTK1[i]);

constraint if (sum(i in 0..15)(bool2int(AYU[0, i] <= 1)) + sum(i in 0..15)(bool2int(AXL[RD, i] <= 1)) == 32) then 
(
    CB_tot = sum(r in 1..(RB - 1), i in 0..15)(FilterZB[r, i]) + sum(r in 2..RB, i in 0..15)(FilterXB[r, i]) + sum(i in 0..19)(CB[i]) - no_of_active_cells_in_tk1    
    % CB_tot = sum(r in 1..(RB - 1), i in 0..15)(FilterZB[r, i]) + sum(r in 2..RB, i in 0..15)(FilterXB[r, i]) + sum(i in 0..19)(CB[i])
) else 
(
    CB_tot = sum(r in 1..(RB - 1), i in 0..15)(FilterZB[r, i]) + sum(r in 2..RB, i in 0..15)(FilterXB[r, i]) + sum(i in 0..19)(CB[i])
) endif;
constraint CF_tot = sum(r in 0..(RF - 1), i in 0..15)(FilterXF[r, i]) + sum(r in 0..(RF - 2), i in 0..15)(FilterZF[r, i]) + sum(i in 0..19)(CF[i]);
constraint FCB_tot = sum(r in 1..(RB - 1), i in 0..15)(IsFilterZB[r, i]) + sum(r in 2..RB, i in 0..15)(IsFilterXB[r, i]);
constraint FCF_tot = sum(r in 0..(RF - 1), i in 0..15)(IsFilterXF[r, i]) + sum(r in 0..(RF - 2), i in 0..15)(IsFilterZF[r, i]);
constraint if RB >= 1 then
(
    WB = sum(i in 0..15)(AXB[1, i])
) endif;
constraint if RF >= 1 then
(
    WF = sum(i in 0..15)(AXF[RF - 1, i])
) endif;

% #############################################################################################################################################
% #############################################################################################################################################

constraint table([g, log_2_minus_053_of_g], log2_minus_053_table);
constraint if variant < 5 then 
(
    key_size = NPT*block_size
) elseif variant == 5 then
(
    key_size = 128
) elseif variant == 6 then 
(
    key_size = 192
) elseif variant == 7 then 
(
    key_size = 128
) elseif variant == 8 then 
(
    key_size = 288
) else 
(
    key_size = 128
) endif;

constraint data_complexity[0] = ((cell_size*CB_tot + cell_size*CF_tot + block_size + 1 - cell_size*WF) div 2) + (log_2_minus_053_of_g div 2);
constraint data_complexity[1] = ((cell_size*CB_tot + cell_size*CF_tot + block_size + 1 - cell_size*WB) div 2) + (log_2_minus_053_of_g div 2);
constraint data_complexity[2] = min(data_complexity[0], data_complexity[1]);
constraint data_complexity[3] = cell_size*CB_tot + cell_size*CF_tot + block_size + 1 - cell_size*WB - cell_size*WF + log_2_minus_053_of_g;
constraint t_complexity[0] = max(data_complexity[2], data_complexity[3]);
constraint t_complexity[1] = cell_size*CB_tot + cell_size*CF_tot + log_2_minus_053_of_g;
constraint t_complexity[2] = cell_size*KS + log_2_minus_053_of_g;
constraint t_complexity[3] = key_size - g;
constraint memory_complexity = min(cell_size*KS, t_complexity[1]);

% constrain g
constraint if RB + RF >= 1 then 
(
    g > 1
    /\
    g <= cell_size*KS
) endif;

constraint max_term = max(i in 0..3)(t_complexity[i]);
constraint if is_related_tweakey then
(
    t_complexity[0] - 1 <= block_size + tolerance
) else
(
    t_complexity[0] <= block_size + tolerance
) endif;  % data complexity
constraint memory_complexity < key_size; % memory complexity
constraint max_term < key_size + tolerance; % time complexity

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ___   _      _              _    _               _____                     _    _               
%  / _ \ | |__  (_)  ___   ___ | |_ (_)__   __ ___  |  ___|_   _  _ __    ___ | |_ (_)  ___   _ __  
% | | | || '_ \ | | / _ \ / __|| __|| |\ \ / // _ \ | |_  | | | || '_ \  / __|| __|| | / _ \ | '_ \ 
% | |_| || |_) || ||  __/| (__ | |_ | | \ V /|  __/ |  _| | |_| || | | || (__ | |_ | || (_) || | | |
%  \___/ |_.__/_/ | \___| \___| \__||_|  \_/  \___| |_|    \__,_||_| |_| \___| \__||_| \___/ |_| |_|
%             |__/                                                                                  
% Objective function

solve minimize max_term;

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%     _                 _  _  _                       _____                     _    _                    
%    / \   _   _ __  __(_)| |(_)  __ _  _ __  _   _  |  ___|_   _  _ __    ___ | |_ (_)  ___   _ __   ___ 
%   / _ \ | | | |\ \/ /| || || | / _` || '__|| | | | | |_  | | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|
%  / ___ \| |_| | >  < | || || || (_| || |   | |_| | |  _| | |_| || | | || (__ | |_ | || (_) || | | |\__ \
% /_/   \_\\__,_|/_/\_\|_||_||_| \__,_||_|    \__, | |_|    \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/
%                                             |___/       
% auxiliary functions

predicate link_difference(var 0..3: diff_pattern, var -2..15: diff_value) =  
    if (diff_pattern == 0) then diff_value == 0
    elseif (diff_pattern == 1) then diff_value > 0
    elseif (diff_pattern == 2) then diff_value == -1
    else diff_value = -2
    endif
;

predicate sbox(var 0..3: diff_in, var 0..3: diff_out) = 
    diff_out != 1 /\
    (diff_in + diff_out) in {0, 3, 4, 6} /\
    diff_out >= diff_in /\
    (diff_out - diff_in) <= 1
;

predicate xor_operation(var 0..3: diff_a, var -2..15: dvalue_a, 
                        var 0..3: diff_b, var -2..15: dvalue_b, 
                        var 0..3: diff_c, var -2..15: dvalue_c) = 
    if (diff_a + diff_b > 2) then 
        (diff_c = 3) /\ (dvalue_c = -2)
    elseif (diff_a + diff_b = 1) then
        (diff_c = 1) /\ (dvalue_c = dvalue_a + dvalue_b)
    elseif ((diff_a == 0) /\ (diff_b = 0)) then
        (diff_c = 0) /\ (dvalue_c = 0)
    elseif (dvalue_a + dvalue_b < 0) then
        (diff_c = 2) /\ (dvalue_c = -1)
    elseif (dvalue_a == dvalue_b) then
        (diff_c = 0) /\ (dvalue_c = 0)
    else
        (diff_c = 1) /\ 
        dvalue_c = (bool2int((dvalue_a mod 2) != (dvalue_b mod 2)) + 
        bool2int(((dvalue_a div 2) mod 2) != ((dvalue_b div 2) mod 2)) * 2 + 
        bool2int(((dvalue_a div 4) mod 2) != ((dvalue_b div 4) mod 2)) * 4 +
        bool2int(((dvalue_a div 8) mod 2) != ((dvalue_b div 8) mod 2)) * 8)
    endif
;

predicate xor_nibbles(var 0..15: class_a, var 0..15: class_b, var 0..15: class_c) = 
    class_c = (bool2int((class_a mod 2) != (class_b mod 2)) + 
    bool2int(((class_a div 2) mod 2) != ((class_b div 2) mod 2)) * 2 + 
    bool2int(((class_a div 4) mod 2) != ((class_b div 4) mod 2)) * 4 +
    bool2int(((class_a div 8) mod 2) != ((class_b div 8) mod 2)) * 8)
;

predicate mix_column_forward(var 0..3: diff_in1, var -2..15: dvalue_in1,
                             var 0..3: diff_in2, var -2..15: dvalue_in2,
                             var 0..3: diff_in3, var -2..15: dvalue_in3,
                             var 0..3: diff_in4, var -2..15: dvalue_in4,
                             var 0..3: diff_out1, var -2..15: dvalue_out1,
                             var 0..3: diff_out2, var -2..15: dvalue_out2,
                             var 0..3: diff_out3, var -2..15: dvalue_out3,
                             var 0..3: diff_out4, var -2..15: dvalue_out4) =
    % the second row
    diff_out2 = diff_in1 /\
    dvalue_out2 = dvalue_in1
    /\
    % the third row
    xor_operation(diff_in2, dvalue_in2, diff_in3, dvalue_in3, diff_out3, dvalue_out3)
    /\
    % the fourth row
    xor_operation(diff_in1, dvalue_in1, diff_in3, dvalue_in3, diff_out4, dvalue_out4)
    /\
    % the first row
    xor_operation(diff_out4, dvalue_out4, diff_in4, dvalue_in4, diff_out1, dvalue_out1)
;

predicate mix_column_backward(var 0..3: diff_in1, var -2..15: dvalue_in1,
                              var 0..3: diff_in2, var -2..15: dvalue_in2,
                              var 0..3: diff_in3, var -2..15: dvalue_in3,
                              var 0..3: diff_in4, var -2..15: dvalue_in4,
                              var 0..3: diff_out1, var -2..15: dvalue_out1,
                              var 0..3: diff_out2, var -2..15: dvalue_out2,
                              var 0..3: diff_out3, var -2..15: dvalue_out3,
                              var 0..3: diff_out4, var -2..15: dvalue_out4) =
    
    % the first row
    diff_out1 = diff_in2  /\
    dvalue_out1 = dvalue_in2
    /\
    % the thrid row
    xor_operation(diff_in2, dvalue_in2, diff_in4, dvalue_in4, diff_out3, dvalue_out3)
    /\
    % the fourth row
    xor_operation(diff_in1, dvalue_in1, diff_in4, dvalue_in4, diff_out4, dvalue_out4)
    /\
    % the second row
    xor_operation(diff_out3, dvalue_out3, diff_in3, dvalue_in3, diff_out2, dvalue_out2)
;

predicate XORD(var 0..1: AX, var 0..1: AY, var 0..1: AZ) = 
    AZ >= AX
    /\
    AZ >= AY
    /\
    AZ <= AX + AY
;

predicate XORD3(var 0..1: AX, var 0..1: AY, var 0..1: AZ, var 0..1: AW) = 
    AW >= AX
    /\
    AW >= AY
    /\
    AW >= AZ
    /\
    AW <= AX + AY + AZ
;

predicate MdiffD(var 0..1: AX0, var 0..1: AX1, var 0..1: AX2, var 0..1: AX3,
                 var 0..1: AY0, var 0..1: AY1, var 0..1: AY2, var 0..1: AY3) =
    AY1 = AX0
    /\
    XORD(AX1, AX2, AY2)
    /\
    XORD(AX0, AX2, AY3)
    /\
    XORD(AY3, AX3, AY0)
;

predicate MinvdiffD(var 0..1: AX0, var 0..1: AX1, var 0..1: AX2, var 0..1: AX3,
                    var 0..1: AY0, var 0..1: AY1, var 0..1: AY2, var 0..1: AY3) =
    AY0 = AX1
    /\
    XORD(AX1, AX3, AY2)
    /\
    XORD(AX0, AX3, AY3)
    /\
    XORD(AY2, AX2, AY1)
;

predicate Mgd(var 0..1: KX0, var 0..1: KX1, var 0..1: KX2, var 0..1: KX3,
              var 0..1: KY0, var 0..1: KY1, var 0..1: KY2, var 0..1: KY3) = 
    KY0 = KX3
    /\
    KY2 = KX1
    /\
    XORD3(KX0, KX1, KX2, KY1)
    /\
    XORD3(KX1, KX2, KX3, KY3)
;

predicate Minvgd(var 0..1: KX0, var 0..1: KX1, var 0..1: KX2, var 0..1: KX3,
                 var 0..1: KY0, var 0..1: KY1, var 0..1: KY2, var 0..1: KY3) = 
    KY1 = KX2
    /\
    KY3 = KX0
    /\
    XORD3(KX0, KX1, KX3, KY0)
    /\
    XORD3(KX0, KX3, KX2, KY2)
;

predicate Minvfixed(var 0..1: X0, var 0..1: X1, var 0..1: X2, var 0..1: X3,
                    var 0..1: Y0, var 0..1: Y1, var 0..1: Y2, var 0..1: Y3) =
    Y0 = X1
    /\
    Y1 = bool2int(X1 + X2 + X3 == 3)
    /\
    Y2 = bool2int(X1 + X3 == 2)
    /\
    Y3 = bool2int(X0 + X3 == 2)
;

predicate Mfixed(var 0..1: X0, var 0..1: X1, var 0..1: X2, var 0..1: X3,
                 var 0..1: Y0, var 0..1: Y1, var 0..1: Y2, var 0..1: Y3) =
    Y0 = bool2int(X0 + X2 + X3 == 3)
    /\
    Y1 = X0
    /\
    Y2 = bool2int(X1 + X2 == 2)
    /\
    Y3 = bool2int(X0 + X2 == 2)
;

predicate XOR_P(var 0..1: AX, var 0..1: AY, var 0..1: AZ, var 0..1: CB) = 
    if ((AX + AY == 2) /\ AZ == 0) then (CB = 1) else (CB = 0) endif
;