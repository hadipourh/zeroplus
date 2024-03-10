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
int: NPT; % the length of distinguisher
int: RD; % the length of distinguisher
int: Ri; % the number of rounds before fork
int: R0; % the number of rounds in C0-fork
bool: is_related_tweakey; % related-tweak setting vs. single-tweakey setting
bool: skip_first_sbox_layer;

constraint assert(RD >= 1, "Invalid value for RD: " ++
                  "RD must be greater than or equal to 1");
constraint assert(NPT in {1, 2, 3, 4}, "NPT must be in {1, 2, 3, 4}");

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

array[0..15] of int: round_permutation = array1d(0..15, [0, 1, 2, 3, 7, 4, 5, 6, 10, 11, 8, 9, 13, 14, 15, 12]); % round permutation
array[0..15] of int: inv_tweakey_permutation = array1d(0..15, [8, 9, 10, 11, 12, 13, 14, 15, 2, 0, 4, 7, 6, 3, 5, 1]); % the inverse of tweakey permutation
% 4-bit LFSR in tweakey schedule of SKINNY-64
array[0..15, 1..2] of int: lfsr_tk2_64 = array2d(0..15, 1..2, [0, 0, 1, 2, 2, 4, 3, 6, 4, 9, 5, 11, 6, 13, 7, 15, 8, 1, 9, 3, 10, 5, 11, 7, 12, 8, 13, 10, 14, 12, 15, 14]); % LFSR for TK2 tweakey schedule
array[0..15, 1..2] of int: lfsr_tk3_64 = array2d(0..15, 1..2, [0, 0, 1, 8, 2, 1, 3, 9, 4, 2, 5, 10, 6, 3, 7, 11, 8, 12, 9, 4, 10, 13, 11, 5, 12, 14, 13, 6, 14, 15, 15, 7]); % LFSR for TK3 tweakey schedule
array[0..15] of int: tweakey_permutation = array1d(0..15,[9,15,8,13,10,14,12,11,0,1,2,3,4,5,6,7]);
array[0..(RD + R0 - 1),0..15] of var int: tkperm_at_round;
constraint forall (i in 0..15) (tkperm_at_round[0, i] = i);
constraint forall (n in 1..(RD + R0 - 1), i in 0..15) (tkperm_at_round[n, i] = tweakey_permutation[tkperm_at_round[n - 1, i]]);

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
array[0..(RD + R0 - 1), 0..15] of var -2..15: DSTK2;
constraint forall(i in 0..15) (link_difference(ASTK2[i], DSTK2[0, i]));

% tweakey line 3
array[0..15] of var 0..3: ASTK3;
array[0..(RD + R0 - 1), 0..15] of var -2..15: DSTK3;
constraint forall(i in 0..15) (link_difference(ASTK3[i], DSTK3[0, i]));

array[0..(RD + R0 - 1), 0..15] of var -2..15: DSTK2xor3;

% subtweakey
array[0..(RD + R0 - 1), 0..15] of var 0..3: ASTK;
array[0..(RD + R0 - 1), 0..15] of var -2..15: DSTK;
constraint forall(i in 0..(RD + R0 - 1), j in 0..15) (link_difference(ASTK[i, j], DSTK[i, j]));

constraint if NPT == 1 then 
(
    forall(i in 0..(RD + R0 - 1), j in 0..15) (DSTK[i, j] = DSTK1[tkperm_at_round[i, j]])
) elseif NPT == 2 then
(
    forall(i in 0..(RD + R0 - 2), j in 0..7) (table([DSTK2[i, tweakey_permutation[j]], DSTK2[i + 1, j]], lfsr_tk2_64)) /\
    forall(i in 0..(RD + R0 - 2), j in 8..15) (DSTK2[i + 1, j] = DSTK2[i, tweakey_permutation[j]]) /\
    forall(i in 0..(RD + R0 - 1), j in 0..15) (xor_nibbles(DSTK1[tkperm_at_round[i, j]], DSTK2[i, j], DSTK[i, j]))
) else
(
    forall(i in 0..(RD + R0 - 2), j in 0..7) (table([DSTK2[i, tweakey_permutation[j]], DSTK2[i + 1, j]], lfsr_tk2_64)) /\
    forall(i in 0..(RD + R0 - 2), j in 8..15) (DSTK2[i + 1, j] = DSTK2[i, tweakey_permutation[j]]) /\
    forall(i in 0..(RD + R0 - 2), j in 0..7) (table([DSTK3[i, tweakey_permutation[j]], DSTK3[i + 1, j]], lfsr_tk3_64)) /\
    forall(i in 0..(RD + R0 - 2), j in 8..15) (DSTK3[i + 1, j] = DSTK3[i, tweakey_permutation[j]]) /\
    forall(i in 0..(RD + R0 - 1), j in 0..15) (xor_nibbles(DSTK1[tkperm_at_round[i, j]], DSTK2[i, j], DSTK2xor3[i, j])) /\
    forall(i in 0..(RD + R0 - 1), j in 0..15) (xor_nibbles(DSTK2xor3[i, j], DSTK3[i, j], DSTK[i, j]))
) endif;

% constraint for the related-tweak vs. single-tweakey settings
constraint if (is_related_tweakey == false) then 
(
    sum(i in 0..(RD + R0 - 1), j in 0..15)(ASTK[i, j]) = 0
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
constraint sum(i in 0..15)(AXU[0, i]) + sum(i in 0..(RD + R0 - 1), j in 0..15)(ASTK[i, j]) != 0;

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
    if r < Ri then 
    (
        xor_operation(AYU[r, i], DYU[r, i], ASTK[r, i], DSTK[r, i], AZU[r, i], DZU[r, i])
        /\
        AZU[r, i + 8] = AYU[r, i + 8]
        /\
        DZU[r, i + 8] = DYU[r, i + 8]        
    ) else
    (
        xor_operation(AYU[r, i], DYU[r, i], ASTK[R0 + r, i], DSTK[R0 + r, i], AZU[r, i], DZU[r, i])
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
    link_difference(AXL[i,j], DXL[i,j])
);

array[0..(RD - 1), 0..15] of var 0..3: AYL;
array[0..(RD - 1), 0..15] of var -2..15: DYL;
constraint forall(i in 0..(RD - 1), j in 0..15) (
    link_difference(AYL[i,j], DYL[i,j])
);

array[0..(RD - 1), 0..15] of var 0..3: AZL;
array[0..(RD - 1), 0..15] of var -2..15: DZL;
constraint forall(i in 0..(RD - 1), j in 0..15) (
    link_difference(AZL[i, j], DZL[i, j])
);

% exclude all-zero output difference
constraint sum(i in 0..15)(AXL[RD, i]) + sum(i in 0..(RD + R0 - 1), j in 0..15)(ASTK[i, j]) != 0;

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
    if r < Ri then 
    (
        xor_operation(AZL[r, i], DZL[r, i], ASTK[r, i], DSTK[r, i], AYL[r, i], DYL[r, i])
        /\
        AYL[r, i + 8] = AZL[r, i + 8]
        /\
        DYL[r, i + 8] = DZL[r, i + 8]
    ) else
    (
        xor_operation(AZL[r, i], DZL[r, i], ASTK[R0 + r, i], DSTK[R0 + r, i], AYL[r, i], DYL[r, i])
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
%   ____                                   _                _    _              ____               _                    _  _        _    _               
%  / ___| _   _   __ _  _ __  __ _  _ __  | |_  ___   ___  | |_ | |__    ___   / ___| ___   _ __  | |_  _ __  __ _   __| |(_)  ___ | |_ (_)  ___   _ __  
% | |  _ | | | | / _` || '__|/ _` || '_ \ | __|/ _ \ / _ \ | __|| '_ \  / _ \ | |    / _ \ | '_ \ | __|| '__|/ _` | / _` || | / __|| __|| | / _ \ | '_ \ 
% | |_| || |_| || (_| || |  | (_| || | | || |_|  __/|  __/ | |_ | | | ||  __/ | |___| (_) || | | || |_ | |  | (_| || (_| || || (__ | |_ | || (_) || | | |
%  \____| \__,_| \__,_||_|   \__,_||_| |_| \__|\___| \___|  \__||_| |_| \___|  \____|\___/ |_| |_| \__||_|   \__,_| \__,_||_| \___| \__||_| \___/ |_| |_|
% Constraints to guranatee the contradiction 
                                                                                                    
array[0..RD] of var 0..16: contradict1;
array[0..RD] of var 0..16: contradict2;
constraint forall(r in 0..RD)
(
    contradict1[r] = sum(i in 0..15)(bool2int((AXU[r, i] + AXL[r, i] > 0) /\ (AXU[r, i] + AXL[r, i] < 3) /\ (AXU[r, i] != AXL[r, i]))) /\
    contradict2[r] = sum(i in 0..15)(bool2int(AXU[r, i] == 1 /\ AXL[r, i] == 1 /\ (DXU[r, i] != DXL[r, i])))
);
% var 0..(16*RD): contradict;
% constraint contradict = sum(r in 0..RD)(contradict1[r] + contradict2[r]);
% constraint contradict > 0;

array[0..(RD - 1)] of var 0..16: contradict3;
array[0..(RD - 1)] of var 0..16: contradict4;
constraint forall(r in 0..(RD - 1))
(
    contradict3[r] = sum(i in 0..15)(bool2int((AYU[r, i] + AYL[r, i] > 0) /\ (AYU[r, i] + AYL[r, i] < 3) /\ (AYU[r, i] != AYL[r, i]))) /\
    contradict4[r] = sum(i in 0..15)(bool2int(AYU[r, i] == 1 /\ AYL[r, i] == 1 /\ (DYU[r, i] != DYL[r, i])))
);
var 0..(4*16*RD): contradict;
constraint contradict = sum(r in 0..(RD - 1))(contradict1[r] + contradict2[r] + contradict3[r] + contradict4[r]);
constraint contradict > 0;

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%  ____          _             
% / ___|   ___  | |__   __ ___ 
% \___ \  / _ \ | |\ \ / // _ \
%  ___) || (_) || | \ V /|  __/
% |____/  \___/ |_|  \_/  \___|

% constraint AYU[0, 0] = 1;
% constraint AXL[RD, 8] = 1;
% constraint ASTK[0, 0] != 1;
% constraint forall(i in 4..15) (ASTK3[i] = 0); % ForkSKINNY-128-288

solve satisfy;

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

predicate xor_with_probability_one(var 0..1: a, var 0..1: b, var 0..1: c) =
    c >= a
    /\ 
    c >= b
    /\ 
    c <= a + b
;

predicate xor3_with_probability_one(var 0..1: a, var 0..1: b, var 0..1: c, var 0..1: d) =
    d >= a
    /\ 
    d >= b
    /\ 
    d >= c
    /\ 
    d <= a + b + c
;

predicate mix_column_forward_with_probability_one_diff(var 0..1: diff_in1,
                                                       var 0..1: diff_in2,
                                                       var 0..1: diff_in3,
                                                       var 0..1: diff_in4,
                                                       var 0..1: diff_out1,
                                                       var 0..1: diff_out2,
                                                       var 0..1: diff_out3,
                                                       var 0..1: diff_out4) =
    % the second row
    diff_out2 = diff_in1
    /\
    % the third row
    xor_with_probability_one(diff_in2, diff_in3, diff_out3)
    /\
    % the fourth row
    xor_with_probability_one(diff_in1, diff_in3, diff_out4)
    /\
    % the first row
    xor_with_probability_one(diff_out4, diff_in4, diff_out1)
;

predicate mix_column_backward_with_probability_one_diff(var 0..1: diff_in1,
                                                        var 0..1: diff_in2,
                                                        var 0..1: diff_in3,
                                                        var 0..1: diff_in4,
                                                        var 0..1: diff_out1,
                                                        var 0..1: diff_out2,
                                                        var 0..1: diff_out3,
                                                        var 0..1: diff_out4) = 
    
    % the first row
    diff_out1 = diff_in2
    /\
    % the thrid row
    xor_with_probability_one(diff_in2, diff_in4, diff_out3)
    /\
    % the fourth row
    xor_with_probability_one(diff_in1, diff_in4, diff_out4)
    /\
    % the second row
    xor_with_probability_one(diff_out3, diff_in3, diff_out2)
;

predicate mix_column_forward_data(var 0..1: data_in1,
                                  var 0..1: data_in2,
                                  var 0..1: data_in3,
                                  var 0..1: data_in4,
                                  var 0..1: data_out1,
                                  var 0..1: data_out2,
                                  var 0..1: data_out3,
                                  var 0..1: data_out4,
                                  var 0..1: auxi_var) =
    % the first row
    data_out1 = data_in4
    /\
    % the third row
    data_out3 = data_in2
    /\
    xor_with_probability_one(data_in2, data_in3, auxi_var)
    /\
    % the second row
    xor_with_probability_one(auxi_var, data_in1, data_out2)
    /\
    % The fourth row
    xor_with_probability_one(auxi_var, data_in4, data_out4)
;

predicate mix_column_forward_diff_values(var 0..1: diff_in1,
                                         var 0..1: diff_in2,
                                         var 0..1: diff_in3,
                                         var 0..1: diff_in4,
                                         var 0..1: diff_out1,
                                         var 0..1: diff_out2,
                                         var 0..1: diff_out3,
                                         var 0..1: diff_out4,
                                         var 0..1: dv_in1,
                                         var 0..1: dv_in2,
                                         var 0..1: dv_in3,
                                         var 0..1: dv_in4,
                                         var 0..1: dv_out1,
                                         var 0..1: dv_out2,
                                         var 0..1: dv_out3,
                                         var 0..1: dv_out4,
                                         var 0..1: auxi_var,
                                         var 0..1: c1,
                                         var 0..1: c2,
                                         var 0..1: c3) = 
    if dv_in1 == 1 then dv_out2 = diff_out2 endif
    /\
    if dv_in2 == 1 then (dv_out2 = diff_out2 /\ dv_out3 = diff_out3 /\ dv_out4 >= diff_out4) endif
    /\
    if dv_in3 == 1 then (dv_out2 = diff_out2 /\ dv_out4 = diff_out4) endif
    /\
    if dv_in4 == 1 then (dv_out1 = diff_out1 /\ dv_out4 = diff_out4) endif
    /\
    if (diff_out1 + diff_out4 == 2 /\ diff_in4 == 0) then (c3 = 1 /\ dv_out1 = 1 /\ dv_out4 = 1) else c3 = 0 endif
    /\
    if (diff_out2 + diff_out4 == 2 /\ diff_in3 == 0) then (c2 = 1 /\ dv_out2 = 1 /\ dv_out4 = 1) else c2 = 0 endif
    /\
    if (diff_in3 + diff_out3 == 2 /\ diff_in2 == 0) then (c1 = 1 /\ dv_out2 = diff_out2 /\ dv_out4 = diff_out4 /\ dv_out3 = 1) else c1 = 0 endif
;

predicate mix_column_backward_data(var 0..1: data_in1,
                                   var 0..1: data_in2,
                                   var 0..1: data_in3,
                                   var 0..1: data_in4,
                                   var 0..1: data_out1,
                                   var 0..1: data_out2,
                                   var 0..1: data_out3,
                                   var 0..1: data_out4,
                                   var 0..1: auxi_var) =
    % the second row
    data_out2 = data_in3
    /\
    % the fourth row
    data_out4 = data_in1
    /\
    xor_with_probability_one(data_in1, data_in4, auxi_var)
    /\
    % the first row
    xor_with_probability_one(auxi_var, data_in2, data_out1)
    /\
    % the thrid row
    xor_with_probability_one(auxi_var, data_in3, data_out3)
;


predicate mix_column_backward_diff_values(var 0..1: diff_in1,
                                          var 0..1: diff_in2,
                                          var 0..1: diff_in3,
                                          var 0..1: diff_in4,
                                          var 0..1: diff_out1,
                                          var 0..1: diff_out2,
                                          var 0..1: diff_out3,
                                          var 0..1: diff_out4,                                            
                                          var 0..1: dv_in1,
                                          var 0..1: dv_in2,
                                          var 0..1: dv_in3,
                                          var 0..1: dv_in4,
                                          var 0..1: dv_out1,
                                          var 0..1: dv_out2,
                                          var 0..1: dv_out3,
                                          var 0..1: dv_out4,
                                          var 0..1: auxi_var,
                                          var 0..1: c1,
                                          var 0..1: c2,
                                          var 0..1: c3) = 
    if dv_in1 == 1 then (dv_out1 = diff_out1 /\ dv_out3 = diff_out3 /\ dv_out4 = diff_out4) endif
    /\
    if dv_in2 == 1 then (dv_out1 = diff_out1) endif
    /\
    if dv_in3 == 1 then (dv_out2 = diff_out2 /\ dv_out3 = diff_out3) endif
    /\
    if dv_in4 == 1 then (dv_out1 = diff_out1 /\ dv_out3 = diff_out3) endif
    /\
    if (diff_out1 + diff_out3 == 2 /\ diff_in4 == 0) then (c2 = 1 /\ dv_out1 = 1 /\ dv_out3 = 1) else c2 = 0 endif
    /\
    if (diff_out2 + diff_out3 == 2 /\ diff_in3 == 0) then (c1 = 1 /\ dv_out2 = 1 /\ dv_out3 = 1) else c1 = 0 endif
    /\
    if (diff_in4 + diff_out4 == 2 /\ diff_in1 == 0) then (c3 =1 /\ dv_out1  = diff_out1 /\ dv_out3 = diff_out3 /\ dv_out4 = 1) else c3 = 0 endif    
;