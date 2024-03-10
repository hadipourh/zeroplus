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
include "globals.mzn";

int: variant;
int: NPT; % number of parallel tweakey lines in the tweakey schedule (used for distinguisher part)
int: RD; % the length of distinguisher
int: Rzero; % the number of rounds before fork
int: Rone; % the number of rounds in C0-fork
int: RB; % number of prepended rounds in key-recovery
int: RF; % number of appended rounds in key-recovery
int: RT = RB + RD + RF; % total number of attacked rounds
bool: is_related_tweakey; % related-tweak setting vs. single-tweakey setting
int: block_size; % block size
int: cell_size; % cell size
block_size = 16*cell_size; 

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

% 4-bit LFSRs in tweakey schedule of SKINNY-64
array[0..15, 1..2] of int: lfsr_tk2_64 = array2d(0..15, 1..2, [0, 0, 1, 2, 2, 4, 3, 6, 4, 9, 5, 11, 6, 13, 7, 15, 8, 1, 9, 3, 10, 5, 11, 7, 12, 8, 13, 10, 14, 12, 15, 14]); % 4-bit LFSR for TK2 tweakey schedule
array[0..15, 1..2] of int: lfsr_tk3_64 = array2d(0..15, 1..2, [0, 0, 1, 8, 2, 1, 3, 9, 4, 2, 5, 10, 6, 3, 7, 11, 8, 12, 9, 4, 10, 13, 11, 5, 12, 14, 13, 6, 14, 15, 15, 7]); % 4-bit LFSR for TK3 tweakey schedule
% 8-bit LFSRs in tweakey schedule of SKINNY-128
array[0..255, 1..2] of int: lfsr_tk2_128 = array2d(0..255, 1..2, [0, 0, 1, 2, 2, 4, 3, 6, 4, 8, 5, 10, 6, 12, 7, 14, 8, 16, 9, 18, 10, 20, 11, 22, 12, 24, 13, 26, 14, 28, 15, 30, 16, 32, 17, 34, 18, 36, 19, 38, 20, 40, 21, 42, 22, 44, 23, 46, 24, 48, 25, 50, 26, 52, 27, 54, 28, 56, 29, 58, 30, 60, 31, 62, 32, 65, 33, 67, 34, 69, 35, 71, 36, 73, 37, 75, 38, 77, 39, 79, 40, 81, 41, 83, 42, 85, 43, 87, 44, 89, 45, 91, 46, 93, 47, 95, 48, 97, 49, 99, 50, 101, 51, 103, 52, 105, 53, 107, 54, 109, 55, 111, 56, 113, 57, 115, 58, 117, 59, 119, 60, 121, 61, 123, 62, 125, 63, 127, 64, 128, 65, 130, 66, 132, 67, 134, 68, 136, 69, 138, 70, 140, 71, 142, 72, 144, 73, 146, 74, 148, 75, 150, 76, 152, 77, 154, 78, 156, 79, 158, 80, 160, 81, 162, 82, 164, 83, 166, 84, 168, 85, 170, 86, 172, 87, 174, 88, 176, 89, 178, 90, 180, 91, 182, 92, 184, 93, 186, 94, 188, 95, 190, 96, 193, 97, 195, 98, 197, 99, 199, 100, 201, 101, 203, 102, 205, 103, 207, 104, 209, 105, 211, 106, 213, 107, 215, 108, 217, 109, 219, 110, 221, 111, 223, 112, 225, 113, 227, 114, 229, 115, 231, 116, 233, 117, 235, 118, 237, 119, 239, 120, 241, 121, 243, 122, 245, 123, 247, 124, 249, 125, 251, 126, 253, 127, 255, 128, 1, 129, 3, 130, 5, 131, 7, 132, 9, 133, 11, 134, 13, 135, 15, 136, 17, 137, 19, 138, 21, 139, 23, 140, 25, 141, 27, 142, 29, 143, 31, 144, 33, 145, 35, 146, 37, 147, 39, 148, 41, 149, 43, 150, 45, 151, 47, 152, 49, 153, 51, 154, 53, 155, 55, 156, 57, 157, 59, 158, 61, 159, 63, 160, 64, 161, 66, 162, 68, 163, 70, 164, 72, 165, 74, 166, 76, 167, 78, 168, 80, 169, 82, 170, 84, 171, 86, 172, 88, 173, 90, 174, 92, 175, 94, 176, 96, 177, 98, 178, 100, 179, 102, 180, 104, 181, 106, 182, 108, 183, 110, 184, 112, 185, 114, 186, 116, 187, 118, 188, 120, 189, 122, 190, 124, 191, 126, 192, 129, 193, 131, 194, 133, 195, 135, 196, 137, 197, 139, 198, 141, 199, 143, 200, 145, 201, 147, 202, 149, 203, 151, 204, 153, 205, 155, 206, 157, 207, 159, 208, 161, 209, 163, 210, 165, 211, 167, 212, 169, 213, 171, 214, 173, 215, 175, 216, 177, 217, 179, 218, 181, 219, 183, 220, 185, 221, 187, 222, 189, 223, 191, 224, 192, 225, 194, 226, 196, 227, 198, 228, 200, 229, 202, 230, 204, 231, 206, 232, 208, 233, 210, 234, 212, 235, 214, 236, 216, 237, 218, 238, 220, 239, 222, 240, 224, 241, 226, 242, 228, 243, 230, 244, 232, 245, 234, 246, 236, 247, 238, 248, 240, 249, 242, 250, 244, 251, 246, 252, 248, 253, 250, 254, 252, 255, 254]); % 8-bit LFSR for TK2 tweakey schedule
array[0..255, 1..2] of int: lfsr_tk3_128 = array2d(0..255, 1..2, [0, 0, 1, 128, 2, 1, 3, 129, 4, 2, 5, 130, 6, 3, 7, 131, 8, 4, 9, 132, 10, 5, 11, 133, 12, 6, 13, 134, 14, 7, 15, 135, 16, 8, 17, 136, 18, 9, 19, 137, 20, 10, 21, 138, 22, 11, 23, 139, 24, 12, 25, 140, 26, 13, 27, 141, 28, 14, 29, 142, 30, 15, 31, 143, 32, 16, 33, 144, 34, 17, 35, 145, 36, 18, 37, 146, 38, 19, 39, 147, 40, 20, 41, 148, 42, 21, 43, 149, 44, 22, 45, 150, 46, 23, 47, 151, 48, 24, 49, 152, 50, 25, 51, 153, 52, 26, 53, 154, 54, 27, 55, 155, 56, 28, 57, 156, 58, 29, 59, 157, 60, 30, 61, 158, 62, 31, 63, 159, 64, 160, 65, 32, 66, 161, 67, 33, 68, 162, 69, 34, 70, 163, 71, 35, 72, 164, 73, 36, 74, 165, 75, 37, 76, 166, 77, 38, 78, 167, 79, 39, 80, 168, 81, 40, 82, 169, 83, 41, 84, 170, 85, 42, 86, 171, 87, 43, 88, 172, 89, 44, 90, 173, 91, 45, 92, 174, 93, 46, 94, 175, 95, 47, 96, 176, 97, 48, 98, 177, 99, 49, 100, 178, 101, 50, 102, 179, 103, 51, 104, 180, 105, 52, 106, 181, 107, 53, 108, 182, 109, 54, 110, 183, 111, 55, 112, 184, 113, 56, 114, 185, 115, 57, 116, 186, 117, 58, 118, 187, 119, 59, 120, 188, 121, 60, 122, 189, 123, 61, 124, 190, 125, 62, 126, 191, 127, 63, 128, 64, 129, 192, 130, 65, 131, 193, 132, 66, 133, 194, 134, 67, 135, 195, 136, 68, 137, 196, 138, 69, 139, 197, 140, 70, 141, 198, 142, 71, 143, 199, 144, 72, 145, 200, 146, 73, 147, 201, 148, 74, 149, 202, 150, 75, 151, 203, 152, 76, 153, 204, 154, 77, 155, 205, 156, 78, 157, 206, 158, 79, 159, 207, 160, 80, 161, 208, 162, 81, 163, 209, 164, 82, 165, 210, 166, 83, 167, 211, 168, 84, 169, 212, 170, 85, 171, 213, 172, 86, 173, 214, 174, 87, 175, 215, 176, 88, 177, 216, 178, 89, 179, 217, 180, 90, 181, 218, 182, 91, 183, 219, 184, 92, 185, 220, 186, 93, 187, 221, 188, 94, 189, 222, 190, 95, 191, 223, 192, 224, 193, 96, 194, 225, 195, 97, 196, 226, 197, 98, 198, 227, 199, 99, 200, 228, 201, 100, 202, 229, 203, 101, 204, 230, 205, 102, 206, 231, 207, 103, 208, 232, 209, 104, 210, 233, 211, 105, 212, 234, 213, 106, 214, 235, 215, 107, 216, 236, 217, 108, 218, 237, 219, 109, 220, 238, 221, 110, 222, 239, 223, 111, 224, 240, 225, 112, 226, 241, 227, 113, 228, 242, 229, 114, 230, 243, 231, 115, 232, 244, 233, 116, 234, 245, 235, 117, 236, 246, 237, 118, 238, 247, 239, 119, 240, 248, 241, 120, 242, 249, 243, 121, 244, 250, 245, 122, 246, 251, 247, 123, 248, 252, 249, 124, 250, 253, 251, 125, 252, 254, 253, 126, 254, 255, 255, 127]); % 8-bit LFSR for TK3 tweakey schedule


array[0..15] of int: tweakey_permutation = array1d(0..15,[9, 15, 8, 13, 10, 14, 12, 11, 0, 1, 2, 3, 4, 5, 6, 7]); % skinny's tweakey permutation
array[0..15] of int: inv_tweakey_permutation = array1d(0..15, [8, 9, 10, 11, 12, 13, 14, 15, 2, 0, 4, 7, 6, 3, 5, 1]); % the inverse of skinny's tweakey permutation

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
array[0..15] of var 0..1: ASTK1;
array[0..15] of var 0..<pow(2, cell_size): DSTK1;
constraint forall(i in 0..15) (link_difference(ASTK1[i], DSTK1[i]));

% tweakey line 2
array[0..15] of var 0..1: ASTK2;
array[0..(RT + Rone - 1), 0..15] of var 0..<pow(2, cell_size): DSTK2;
constraint forall(i in 0..15) (link_difference(ASTK2[i], DSTK2[0, i]));

% tweakey line 3
array[0..15] of var 0..1: ASTK3;
array[0..(RT + Rone - 1), 0..15] of var 0..<pow(2, cell_size): DSTK3;
constraint forall(i in 0..15) (link_difference(ASTK3[i], DSTK3[0, i]));

array[0..(RT + Rone - 1), 0..15] of var 0..15: DSTK2xor3;

% subtweakey
array[0..(RT + Rone - 1), 0..15] of var 0..1: ASTK;
array[0..(RT + Rone - 1), 0..15] of var 0..<pow(2, cell_size): DSTK;
constraint forall(i in 0..(RT + Rone - 1), j in 0..15) (link_difference(ASTK[i, j], DSTK[i, j]));

constraint if cell_size == 4 then 
(
    if NPT == 1 then 
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
    ) endif
) else
(
    if NPT == 1 then 
    (
        forall(i in 0..(RT + Rone - 1), j in 0..15) (DSTK[i, j] = DSTK1[tkperm_at_round[i, j]])
    ) elseif NPT == 2 then
    (
        forall(i in 0..(RT + Rone - 2), j in 0..7) (table([DSTK2[i, tweakey_permutation[j]], DSTK2[i + 1, j]], lfsr_tk2_128)) /\
        forall(i in 0..(RT + Rone - 2), j in 8..15) (DSTK2[i + 1, j] = DSTK2[i, tweakey_permutation[j]]) /\
        forall(i in 0..(RT + Rone - 1), j in 0..15) (xor_bytes(DSTK1[tkperm_at_round[i, j]], DSTK2[i, j], DSTK[i, j]))
    ) else
    (
        forall(i in 0..(RT + Rone - 2), j in 0..7) (table([DSTK2[i, tweakey_permutation[j]], DSTK2[i + 1, j]], lfsr_tk2_128)) /\
        forall(i in 0..(RT + Rone - 2), j in 8..15) (DSTK2[i + 1, j] = DSTK2[i, tweakey_permutation[j]]) /\
        forall(i in 0..(RT + Rone - 2), j in 0..7) (table([DSTK3[i, tweakey_permutation[j]], DSTK3[i + 1, j]], lfsr_tk3_128)) /\
        forall(i in 0..(RT + Rone - 2), j in 8..15) (DSTK3[i + 1, j] = DSTK3[i, tweakey_permutation[j]]) /\
        forall(i in 0..(RT + Rone - 1), j in 0..15) (xor_bytes(DSTK1[tkperm_at_round[i, j]], DSTK2[i, j], DSTK2xor3[i, j])) /\
        forall(i in 0..(RT + Rone - 1), j in 0..15) (xor_bytes(DSTK2xor3[i, j], DSTK3[i, j], DSTK[i, j]))
    ) endif  
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

solve satisfy;

predicate link_difference(var 0..3: diff_pattern, var -2..<pow(2, cell_size): diff_value) =  
    if (diff_pattern == 0) then diff_value == 0
    elseif (diff_pattern == 1) then diff_value > 0
    elseif (diff_pattern == 2) then diff_value == -1
    else diff_value = -2
    endif
;

predicate xor_nibbles(var 0..15: class_a, var 0..15: class_b, var 0..15: class_c) = 
    class_c = (bool2int((class_a mod 2) != (class_b mod 2)) + 
    bool2int(((class_a div 2) mod 2) != ((class_b div 2) mod 2)) * 2 + 
    bool2int(((class_a div 4) mod 2) != ((class_b div 4) mod 2)) * 4 +
    bool2int(((class_a div 8) mod 2) != ((class_b div 8) mod 2)) * 8)
;

predicate xor_bytes(var 0..255: byte_a, var 0..255: byte_b, var 0..255: byte_c) =
    byte_c = (bool2int((byte_a mod 2) != (byte_b mod 2)) +
    bool2int(((byte_a div 2) mod 2) != ((byte_b div 2) mod 2)) * 2 +
    bool2int(((byte_a div 4) mod 2) != ((byte_b div 4) mod 2)) * 4 +
    bool2int(((byte_a div 8) mod 2) != ((byte_b div 8) mod 2)) * 8 +
    bool2int(((byte_a div 16) mod 2) != ((byte_b div 16) mod 2)) * 16 +
    bool2int(((byte_a div 32) mod 2) != ((byte_b div 32) mod 2)) * 32 +
    bool2int(((byte_a div 64) mod 2) != ((byte_b div 64) mod 2)) * 64 +
    bool2int(((byte_a div 128) mod 2) != ((byte_b div 128) mod 2)) * 128)
;