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

int: NPT; % Number of paths in the tweakey schedule (1, 2, 3, 4)
int: RD; % The length of distinguisher
int: Ndt; % The number of rounds that the tweakey schedule should perform
int: Ri; % Ri is the number of rounds before the fork
int: R0; % R0 is the number of rounds for the C0-branch
bool: skip_first_sbox_layer;
Ndt = RD + R0;

constraint assert(RD >= 0,"Invalid value for RD: " ++
                "RD must be greater than or equal to 0");
constraint assert(Ri >= 0,"Invalid value for Ri: " ++
                "Ri must be greater than or equal to 0");
constraint assert(R0 >= 0,"Invalid value for R0: " ++
                "R0 must be greater than or equal to 0");

% skinny round permutation
array[0..15] of int: round_permutation = array1d(0..15, [0, 1, 2, 3, 7, 4, 5, 6, 10, 11, 8, 9, 13, 14, 15, 12]);

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____                        _                       ____         _                _         _       
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  |_   _|__      __ ___   __ _ | | __ ___  _   _       / ___|   ___ | |__    ___   __| | _   _ | |  ___ 
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__|   | |  \ \ /\ / // _ \ / _` || |/ // _ \| | | | _____\___ \  / __|| '_ \  / _ \ / _` || | | || | / _ \
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |      | |   \ V  V /|  __/| (_| ||   <|  __/| |_| ||_____|___) || (__ | | | ||  __/| (_| || |_| || ||  __/
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|      |_|    \_/\_/  \___| \__,_||_|\_\\___| \__, |      |____/  \___||_| |_| \___| \__,_| \__,_||_| \___|
%                                                                                                                            |___/                                                        
% Constraints for tweakey-schedule

array[0..(RD - 1), 0..15] of var 0..1: any_or_nonzero_subtweakey;
array[0..(RD - 1), 0..15] of var 0..1: nonzero_subtweakeys;
array[0..15] of var 0..RD: no_of_any_or_nonzero;
array[0..15] of var 0..RD: no_of_only_nonzero;
array[0..15] of int: tweakey_permutation = array1d(0..15, [9, 15, 8, 13, 10, 14, 12, 11, 0, 1, 2, 3, 4, 5, 6, 7]);
array[0..(Ndt - 1), 0..15] of var int: tkpermutation_at_round;
constraint forall (i in 0..15) (tkpermutation_at_round[0, i] = i);
constraint forall (n in 1..(Ndt - 1), i in 0..15) (tkpermutation_at_round[n, i] = tweakey_permutation[tkpermutation_at_round[n - 1, i]]);


% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%   ____                    _                _         _           __                _____  _   _ 
%  / ___| ___   _ __   ___ | |_  _ __  __ _ (_) _ __  | |_  ___   / _|  ___   _ __  | ____|| | | |
% | |    / _ \ | '_ \ / __|| __|| '__|/ _` || || '_ \ | __|/ __| | |_  / _ \ | '__| |  _|  | | | |
% | |___| (_) || | | |\__ \| |_ | |  | (_| || || | | || |_ \__ \ |  _|| (_) || |    | |___ | |_| |
%  \____|\___/ |_| |_||___/ \__||_|   \__,_||_||_| |_| \__||___/ |_|   \___/ |_|    |_____| \___/ 
% constraints for EU

% AXU: Activeness of the state cell before the sbox in the Upper trail
% LXU: Mask value of the state cell before the sbox in the Upper trail
% AYU: Active state cell after the sbox in the Upper trail
% LYU: Mask value of the state cell after the sbox in the Upper trail
% DummyAU: Dummy variable to handle the MixColumn
% DummyLU: Dummy variable to handle the MixColumn

array[0..RD, 0..15] of var 0..3: AXU;
array[0..RD, 0..15] of var -2..15: LXU;
constraint forall(r in 0..RD, i in 0..15) (
    link_mask(AXU[r, i], LXU[r, i])
);

array[0..(RD - 1), 0..15] of var 0..3: AYU;
array[0..(RD - 1), 0..15] of var -2..15: LYU;
constraint forall(r in 0..(RD - 1), i in 0..15) (
    link_mask(AYU[r, i], LYU[r, i])
);

array[0..(RD - 1), 0..3] of var 0..3: DummyAU;
array[0..(RD - 1), 0..3] of var -2..15: DummyLU;
constraint forall(r in 0..(RD - 1), i in 0..3) (
    link_mask(DummyAU[r, i], DummyLU[r, i])
);

% exclude all-zero input mask
var 0..48: input_mask_distinguisher;
constraint input_mask_distinguisher = sum(i in 0..15)(AXU[0, i]);
constraint input_mask_distinguisher != 0;

% S-box
constraint if (skip_first_sbox_layer) then
(
    forall(i in 0..15)
    (
        AYU[0, i] = AXU[0, i] /\
        LYU[0, i] = LXU[0, i]
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

% mix-column
constraint forall(r in 0..(RD - 1), i in 0..3)
(
    mix_column_forward(AYU[r, round_permutation[i]], LYU[r, round_permutation[i]],
                       AYU[r, round_permutation[i + 4]], LYU[r, round_permutation[i + 4]],
                       AYU[r, round_permutation[i + 8]], LYU[r, round_permutation[i + 8]],
                       AYU[r, round_permutation[i + 12]], LYU[r, round_permutation[i + 12]],
                       AXU[r + 1, i], LXU[r + 1, i],
                       AXU[r + 1, i + 4], LXU[r + 1, i + 4],
                       AXU[r + 1, i + 8], LXU[r + 1, i + 8],
                       AXU[r + 1, i + 12], LXU[r + 1, i + 12],
                       DummyAU[r, i], DummyLU[r, i])
);

% Link the subtweakey and the internal state

constraint forall(r in 0..(RD - 1), i in 0..7)
(
    if r < Ri then 
    (
        if min(AYU[r, i], AYL[r, i]) == 3 then
        (
            any_or_nonzero_subtweakey[r, tkpermutation_at_round[r, i]] = 1
            /\
            nonzero_subtweakeys[r, tkpermutation_at_round[r, i]] = 0
        ) elseif min(AYU[r, i], AYL[r, i]) >= 1 then
        (
            any_or_nonzero_subtweakey[r, tkpermutation_at_round[r, i]] = 1 
            /\ 
            nonzero_subtweakeys[r, tkpermutation_at_round[r, i]] = 1
        ) else
        (
            any_or_nonzero_subtweakey[r, tkpermutation_at_round[r, i]] = 0
            /\
            nonzero_subtweakeys[r, tkpermutation_at_round[r, i]] = 0
        ) endif 
        /\
        any_or_nonzero_subtweakey[r, tkpermutation_at_round[r, i + 8]] = 0
        /\
        nonzero_subtweakeys[r, tkpermutation_at_round[r, i + 8]] = 0
    ) else
    (
        if min(AYU[r, i], AYL[r, i]) == 3 then
        (
            any_or_nonzero_subtweakey[r, tkpermutation_at_round[R0 + r, i]] = 1
            /\
            nonzero_subtweakeys[r, tkpermutation_at_round[R0 + r, i]] = 0
        )        
        elseif min(AYU[r, i], AYL[r, i]) >= 1 then
        (
            any_or_nonzero_subtweakey[r, tkpermutation_at_round[R0 + r, i]] = 1 
            /\ 
            nonzero_subtweakeys[r, tkpermutation_at_round[R0 + r, i]] = 1
        ) else
        (
            any_or_nonzero_subtweakey[r, tkpermutation_at_round[R0 + r, i]] = 0
            /\
            nonzero_subtweakeys[r, tkpermutation_at_round[R0 + r, i]] = 0
        )
        endif 
        /\
        any_or_nonzero_subtweakey[r, tkpermutation_at_round[R0 + r, i + 8]] = 0
        /\
        nonzero_subtweakeys[r, tkpermutation_at_round[R0 + r, i + 8]] = 0
    ) endif    
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

% AXL: Activeness of the state cell before the sbox in the Lower trail
% LXL: Mask value of the state cell before the sbox in the Lower trail
% AYL: Active state cell after the sbox in the Lower trail
% LYL: Mask value of the state cell after the sbox in the Lower trail
% DummyAL: Dummy variable to handle the MixColumn
% DummyLL: Dummy variable to handle the MixColumn

array[0..RD, 0..15] of var 0..3: AXL;
array[0..RD, 0..15] of var -2..15: LXL;
constraint forall(r in 0..RD, i in 0..15) (
    link_mask(AXL[r, i], LXL[r, i])
);

array[0..(RD - 1), 0..15] of var 0..3: AYL;
array[0..(RD - 1), 0..15] of var -2..15: LYL;
constraint forall(r in 0..(RD - 1), i in 0..15) (
    link_mask(AYL[r, i], LYL[r, i])
);

array[0..(RD - 1), 0..3] of var 0..3: DummyAL;
array[0..(RD - 1), 0..3] of var -2..15: DummyLL;
constraint forall(r in 0..(RD - 1), i in 0..3) (
    link_mask(DummyAL[r, i], DummyLL[r, i])
);

% exclude all-zero output mask
var 0..48: output_mask_distinguisher;
constraint output_mask_distinguisher = sum(i in 0..15)(AXL[RD, i]);
constraint output_mask_distinguisher != 0;

% mix-column
constraint forall(r in 0..(RD - 1), i in 0..3)
(
    mix_column_backward(AXL[r + 1, i], LXL[r + 1, i],
                        AXL[r + 1, i + 4], LXL[r + 1, i + 4],
                        AXL[r + 1, i + 8], LXL[r + 1, i + 8],
                        AXL[r + 1, i + 12], LXL[r + 1, i + 12],
                        AYL[r, round_permutation[i]], LYL[r, round_permutation[i]],
                        AYL[r, round_permutation[i + 4]], LYL[r, round_permutation[i + 4]],
                        AYL[r, round_permutation[i + 8]], LYL[r, round_permutation[i + 8]],
                        AYL[r, round_permutation[i + 12]], LYL[r, round_permutation[i + 12]],
                        DummyAL[r, i], DummyLL[r, i])
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
% Gurantee the contradiction in the distinguisher

constraint forall(i in 0..15)
(
    no_of_any_or_nonzero[i] = sum(r in 0..(RD - 1))(any_or_nonzero_subtweakey[r, i])
    /\
    no_of_only_nonzero[i] = sum(r in 0..(RD - 1))(nonzero_subtweakeys[r, i])
);

array[0..15] of var 0..1: contradict;
constraint forall(i in 0..15)
(
    contradict[i] = bool2int(no_of_any_or_nonzero[i] <= NPT /\ no_of_only_nonzero[i] >= 1) + bool2int(no_of_any_or_nonzero[i] == 0)
);
constraint sum(i in 0..15)(contradict[i]) >= 1;

% #############################################################################################################################################
% #############################################################################################################################################
% #############################################################################################################################################
%  ____          _             
% / ___|   ___  | |__   __ ___ 
% \___ \  / _ \ | |\ \ / // _ \
%  ___) || (_) || | \ V /|  __/
% |____/  \___/ |_|  \_/  \___|
% define objective function and solve
% constraint forall(i in 0..15)
% (
%     AXU[0, i] = 3 \/ AXU[0, i] = 0
% );

solve maximize input_mask_distinguisher;

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

predicate link_mask(var 0..3: mask, var -2..15: value) = 
    if (mask == 0) then value == 0
    elseif (mask == 1) then value > 0
    elseif (mask == 2) then value == -1
    else value == -2 endif
;

predicate sbox(var 0..3: in_mask, var 0..3: out_mask) = 
    out_mask != 1 /\
    (in_mask + out_mask) in {0, 3, 4, 6} /\
    out_mask >= in_mask /\
    (out_mask - in_mask) <= 1
;

predicate xor_operation(var 0..3: mask_a, var -2..15: value_a, 
                        var 0..3: mask_b, var -2..15: value_b, 
                        var 0..3: mask_c, var -2..15: value_c) = 
    if (mask_a + mask_b > 2) then
        (mask_c = 3) /\ (value_c = -2)
    elseif (mask_a + mask_b = 1) then
        (mask_c = 1) /\ (value_c = value_a + value_b)
    elseif ((mask_a == 0) /\ (mask_b == 0)) then
        (mask_c = 0) /\ (value_c = 0)
    elseif (value_a + value_b < 0) then
        (mask_c = 2) /\ (value_c = -1)
    elseif (value_a == value_b) then
        (mask_c = 0) /\ (value_c = 0)
    else
        (mask_c = 1) /\
        value_c = (bool2int((value_a mod 2) != (value_b mod 2)) + 
        bool2int(((value_a div 2) mod 2) != ((value_b div 2) mod 2)) * 2 + 
        bool2int(((value_a div 4) mod 2) != ((value_b div 4) mod 2)) * 4 +
        bool2int(((value_a div 8) mod 2) != ((value_b div 8) mod 2)) * 8)
    endif
;

predicate branch_operation(var 0..3: mask_c, var -2..15: class_c, 
                           var 0..3: mask_a, var -2..15: class_a, 
                           var 0..3: mask_b, var -2..15: class_b) = 
    % c is coppied to a and b
    if (mask_a + mask_b > 2) then
        (mask_c = 3) /\ (class_c = -2)
    elseif (mask_a + mask_b = 1) then
        (mask_c = 1) /\ (class_c = class_a + class_b)
    elseif ((mask_a == 0) /\ (mask_b == 0)) then
        (mask_c = 0) /\ (class_c = 0)
    elseif (class_a + class_b < 0) then
        (mask_c = 2) /\ (class_c = -1)
    elseif (class_a == class_b) then
        (mask_c = 0) /\ (class_c = 0)
    else
        (mask_c = 1) /\
        class_c = (bool2int((class_a mod 2) != (class_b mod 2)) + 
        bool2int(((class_a div 2) mod 2) != ((class_b div 2) mod 2)) * 2 + 
        bool2int(((class_a div 4) mod 2) != ((class_b div 4) mod 2)) * 4 +
        bool2int(((class_a div 8) mod 2) != ((class_b div 8) mod 2)) * 8)
    endif
;

predicate mix_column_forward(var 0..3: in_mask1, var -2..15: in_value1, 
                             var 0..3: in_mask2, var -2..15: in_value2, 
                             var 0..3: in_mask3, var -2..15: in_value3, 
                             var 0..3: in_mask4, var -2..15: in_value4, 
                             var 0..3: out_mask1, var -2..15: out_value1, 
                             var 0..3: out_mask2, var -2..15: out_value2, 
                             var 0..3: out_mask3, var -2..15: out_value3, 
                             var 0..3: out_mask4, var -2..15: out_value4, 
                             var 0..3: auxi_mask, var -2..15: auxi_val) =
    % the first row
    out_mask1 = in_mask4 /\
    out_value1 = in_value4
    /\
    % the third row
    out_mask3 = in_mask2 /\
    out_value3 = in_value2
    /\
    % compute auxiliary variable
    % a: in_mask2, in_value2
    % b: in_mask3, in_value3
    % c: auxi_mask, auxi_val
    xor_operation(in_mask2, in_value2, in_mask3, in_value3, auxi_mask, auxi_val)
    /\
    % the second row
    % a: auxi_mask, auxi_val
    % b: in_mask1, in_value1
    % c: out_mask2, out_value2
    xor_operation(auxi_mask, auxi_val, in_mask1, in_value1, out_mask2, out_value2)
    /\
    % the fourth row
    % a: auxi_mask, auxi_val
    % b: in_mask4, in_value4
    % c: out_mask4, out_value4
    xor_operation(auxi_mask, auxi_val, in_mask4, in_value4, out_mask4, out_value4)    
;

predicate mix_column_backward(var 0..3: in_mask1, var -2..15: in_value1, 
                              var 0..3: in_mask2, var -2..15: in_value2, 
                              var 0..3: in_mask3, var -2..15: in_value3, 
                              var 0..3: in_mask4, var -2..15: in_value4, 
                              var 0..3: out_mask1, var -2..15: out_value1, 
                              var 0..3: out_mask2, var -2..15: out_value2, 
                              var 0..3: out_mask3, var -2..15: out_value3, 
                              var 0..3: out_mask4, var -2..15: out_value4, 
                              var 0..3: auxi_mask, var -2..15: auxi_val) =
    % the second row
    out_mask2 = in_mask3 /\
    out_value2 = in_value3
    /\
    % the fourth row
    out_mask4 = in_mask1 /\
    out_value4 = in_value1
    /\
    % compute auxiliary variable
    % a: in_mask1 in_value1
    % b: in_mask4 in_value4
    % c: auxi_mask auxi_val
    xor_operation(in_mask1, in_value1, in_mask4, in_value4, auxi_mask, auxi_val)
    /\
    % the first row
    % a: auxi_mask auxi_val
    % b: in_mask2 in_value2
    % c: out_mask1 out_value1
    xor_operation(auxi_mask, auxi_val, in_mask2, in_value2, out_mask1, out_value1)
    /\
    % the third row
    % a: auxi_mask auxi_val
    % b: in_mask3 in_value3
    % c: out_mask3 out_value3
    xor_operation(auxi_mask, auxi_val, in_mask3, in_value3, out_mask3, out_value3)
;
