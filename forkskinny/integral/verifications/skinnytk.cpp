/*
 * Check the integral distinguisher for Fork-SKINNY
 * Date: Sep 7, 2023
 * Author: Hosein Hadipour
*/

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <stdlib.h>  // rand(), srand()
#include <time.h>    // time()
#include <sys/random.h>
#include <string>

using namespace std;

// 4-bit Sbox
const uint8_t S[16] = {0xc, 0x6, 0x9, 0x0, 0x1, 0xa, 0x2, 0xb, 0x3, 0x8, 0x5, 0xd, 0x4, 0xe, 0x7, 0xf};
// 4-bit Sbox Inverse
const uint8_t Sinv[16] = {0x3, 0x4, 0x6, 0x8, 0xc, 0xa, 0x1, 0xe, 0x9, 0x2, 0x5, 0x7, 0x0, 0xb, 0xd, 0xf};
// Permutation
const uint8_t P[16] = {0x0, 0x1, 0x2, 0x3, 0x7, 0x4, 0x5, 0x6, 0xa, 0xb, 0x8, 0x9, 0xd, 0xe, 0xf, 0xc};
const uint8_t Pinv[16] = {0x0, 0x1, 0x2, 0x3, 0x5, 0x6, 0x7, 0x4, 0xa, 0xb, 0x8, 0x9, 0xf, 0xc, 0xd, 0xe};
// Tweakey Permutation
const uint8_t Q[16] = {0x9, 0xf, 0x8, 0xd, 0xa, 0xe, 0xc, 0xb, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7};
// const uint8_t Qinv[16] = {0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x2, 0x0, 0x4, 0x7, 0x6, 0x3, 0x5, 0x1};
// Round Constants
const unsigned char RC[62] = {0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3E, 0x3D, 0x3B, 0x37, 0x2F,
                              0x1E, 0x3C, 0x39, 0x33, 0x27, 0x0E, 0x1D, 0x3A, 0x35, 0x2B,
                              0x16, 0x2C, 0x18, 0x30, 0x21, 0x02, 0x05, 0x0B, 0x17, 0x2E,
                              0x1C, 0x38, 0x31, 0x23, 0x06, 0x0D, 0x1B, 0x36, 0x2D, 0x1A,
                              0x34, 0x29, 0x12, 0x24, 0x08, 0x11, 0x22, 0x04, 0x09, 0x13,
                              0x26, 0x0c, 0x19, 0x32, 0x25, 0x0a, 0x15, 0x2a, 0x14, 0x28,
                              0x10, 0x20};

void init_prng();
void print_state(uint8_t state[16]);
void convert_hexstr_to_statearray(string hex_str, uint8_t int_array[16], bool reversed);
uint8_t tweak_tk2_lfsr(uint8_t x);
uint8_t tweak_tk3_lfsr(uint8_t x);
void mix_columns(uint8_t state[16]);
void inv_mix_columns(uint8_t state[16]);
void tweakey_schedule(int rounds, uint8_t tk1[][16], uint8_t tk2[][16], uint8_t tk3[][16], uint8_t round_tweakey[][8]);
void enc(int R, uint8_t plaintext[16], uint8_t ciphertext[16], uint8_t tk[][8], uint8_t fork_pint, uint8_t length_c0_br);
void dec(int R, uint8_t plaintext[16], uint8_t ciphertext[16], uint8_t tk[][8], uint8_t Ri, uint8_t length_c0_br);
int test_enc_dec_inverse(uint8_t R, uint8_t R0, uint8_t Ri);

void init_prng() {
    unsigned int initial_seed = -1;
    ssize_t temp;
    temp = getrandom(&initial_seed, sizeof(initial_seed), 0);
    srand(initial_seed);   // Initialization, should only be called once. int r = rand();
	printf("[x] PRNG initialized by %lu random bytes: 0x%08X\n", temp, initial_seed);
}

void print_state(uint8_t state[16])
{
    for (int i = 0; i < 16; i++)
        printf("%01x", state[i]);
    printf("\n");
}

void convert_hexstr_to_statearray(string hex_str, uint8_t int_array[16], bool reversed = false)
{
    if (reversed == true)
        for (int i = 15; i > -1; i--)
            int_array[15 - i] = static_cast<uint8_t> (stoi(hex_str.substr(i, 1), 0, 16) & 0xf);
    else
        for (int i = 0; i < 16; i++)
            int_array[i] = static_cast<uint8_t> (stoi(hex_str.substr(i, 1), 0, 16) & 0xf);
}

uint8_t tweak_tk2_lfsr(uint8_t x)
{
    x = (x << 1) ^ ((x >> 3) & 0x1) ^ ((x >> 2) & 0x1);
    x = x & 0xf;
    return x;
}

uint8_t tweak_tk3_lfsr(uint8_t x)
{
    x = (x >> 1) ^ (((x & 0x1) ^ ((x >> 3) & 0x1)) << 3);
    x = x & 0xf;
    return x;
}

void mix_columns(uint8_t state[16])
{
    uint8_t tmp;
    for (uint8_t j = 0; j < 4; j++)
    {
        state[j + 4 * 1] ^= state[j + 4 * 2];
        state[j + 4 * 2] ^= state[j + 4 * 0];
        state[j + 4 * 3] ^= state[j + 4 * 2];
        tmp = state[j + 4 * 3];
        state[j + 4 * 3] = state[j + 4 * 2];
        state[j + 4 * 2] = state[j + 4 * 1];
        state[j + 4 * 1] = state[j + 4 * 0];
        state[j + 4 * 0] = tmp;
    }
}

void inv_mix_columns(uint8_t state[16])
{
    uint8_t tmp;
    for (uint8_t j = 0; j < 4; j++)
    {
        tmp = state[j + 4 * 3];
        state[j + 4 * 3] = state[j + 4 * 0];
        state[j + 4 * 0] = state[j + 4 * 1];
        state[j + 4 * 1] = state[j + 4 * 2];
        state[j + 4 * 2] = tmp;
        state[j + 4 * 3] ^= state[j + 4 * 2];
        state[j + 4 * 2] ^= state[j + 4 * 0];
        state[j + 4 * 1] ^= state[j + 4 * 2];
    }
}

void tweakey_schedule(int rounds, uint8_t tk1[][16], uint8_t tk2[][16], uint8_t tk3[][16], uint8_t round_tweakey[][8])
{
    // Declare tweakey after permutation
    uint8_t tkp1[rounds - 1][16];
    uint8_t tkp2[rounds - 1][16];
    uint8_t tkp3[rounds - 1][16];
    for (uint8_t i = 0; i < 16; i++)
        tk1[0][i] = (tk1[0][i] & 0xf);
    for (uint8_t i = 0; i < 16; i++)
        tk2[0][i] = (tk2[0][i] & 0xf);
    for (uint8_t i = 0; i < 16; i++)
        tk3[0][i] = (tk3[0][i] & 0xf);
    for (uint8_t i = 0; i < 8; i++)
        round_tweakey[0][i] = (tk1[0][i] ^ tk2[0][i] ^ tk3[0][i]);
    for (int r = 1; r < rounds; r++)
    {
        // Apply tweakey permutation on TK1, TK2, and TK3
        for (int i = 0; i < 16; i++)
        {
            tkp1[r - 1][i] = tk1[r - 1][Q[i]];
            tkp2[r - 1][i] = tk2[r - 1][Q[i]];
            tkp3[r - 1][i] = tk3[r - 1][Q[i]];
        }
        // Apply LFSR on two upper rows of TK2, and TK3
        for (int i = 0; i < 16; i++)
        {
            // LFSRs are not performed on TK1 at all
            tk1[r][i] = tkp1[r - 1][i];
            if (i < 8)
            {
                tk2[r][i] = tweak_tk2_lfsr(tkp2[r - 1][i]);
                tk3[r][i] = tweak_tk3_lfsr(tkp3[r - 1][i]);
            }
            else
            {
                tk2[r][i] = tkp2[r - 1][i];
                tk3[r][i] = tkp3[r - 1][i];
            }
        }
        // Update round-tweakey
        for (int i = 0; i < 8; i++)
            round_tweakey[r][i] = (tk1[r][i] ^ tk2[r][i] ^ tk3[r][i]);
        // printf("\ntweakeys: ");
        // print_state(round_tweakey[r]);
    }
}

void enc(int R, uint8_t plaintext[16], uint8_t ciphertext[16], uint8_t tk[][8], uint8_t fork_pint, uint8_t length_c0_br)
{
    for (uint8_t i = 0; i < 16; i++)
    {
        ciphertext[i] = plaintext[i] & 0xf;
    }
    for (uint8_t r = 0; r < R; r++)
    {
        // SBox
        for (uint8_t i = 0; i < 16; i++)
            ciphertext[i] = S[ciphertext[i]];
        // Add constants (constants only affects on three upper cells of the first column)
        ciphertext[0] ^= (RC[r] & 0xf);
        ciphertext[4] ^= ((RC[r] >> 4) & 0x3);
        ciphertext[8] ^= 0x2;
        // Add round tweakey (tweakey only exclusive-ored with two upper rows of the state)
        for (uint8_t i = 0; i < 8; i++)
        {
            if (r < fork_pint) 
                ciphertext[i] ^= tk[r][i];
            else
                ciphertext[i] ^= tk[r + length_c0_br][i];
        }
        // Permute nibbles
        uint8_t temp[16];
        for (uint8_t i = 0; i < 16; i++)
            temp[i] = ciphertext[i];
        for (uint8_t i = 0; i < 16; i++)
            ciphertext[i] = temp[P[i]];
        // MixColumn
        mix_columns(ciphertext);
        // Print state
        // printf("\nR%02d : ", r + 1);
        // print_state(ciphertext);
    }
}

void dec(int R, uint8_t plaintext[16], uint8_t ciphertext[16], uint8_t tk[][8], uint8_t Ri, uint8_t length_c0_br)
{
    for (uint8_t i = 0; i < 16; i++)
    {
        plaintext[i] = ciphertext[i] & 0xf;
    }
    int ind;
    uint8_t temp[16];
    for (int r = 0; r < R; r++)
    {
        // MixColumn inverse
        inv_mix_columns(plaintext);
        // Permute nibble inverse
        for (uint8_t i = 0; i < 16; i++)
            temp[i] = plaintext[i];
        for (uint8_t i = 0; i < 16; i++)
            plaintext[i] = temp[Pinv[i]];
        //temp[P[i]] = plaintext[i];
        // Add tweakey
        ind = R - r - 1;
        for (uint8_t i = 0; i < 8; i++)
        {
            if (ind >= Ri)
                plaintext[i] ^= tk[ind + length_c0_br][i];
            else
                plaintext[i] ^= tk[ind][i];
        }
        // Add constants
        plaintext[0] ^= (RC[ind] & 0xf);
        plaintext[4] ^= ((RC[ind] >> 4) & 0x3);
        plaintext[8] ^= 0x2;
        // SBox inverse
        for (uint8_t i = 0; i < 16; i++)
            plaintext[i] = Sinv[plaintext[i]];
        // Print state
        // printf("\nR%02d : ", r + 1);
        // print_state(plaintext);
    }
}

int test_enc_dec_inverse(uint8_t R, uint8_t R0, uint8_t Ri) {
    uint8_t tk1[R + R0][16];
    uint8_t tk2[R + R0][16];
    uint8_t tk3[R + R0][16];
    uint8_t rtk[R + R0][8];
    // randomly choose a tweakey
    for (int i = 0; i < 16; i++)
    {
        tk1[0][i] = rand() & 0xf;
        tk2[0][i] = rand() & 0xf;
        tk3[0][i] = rand() & 0xf;
    }
    tweakey_schedule(R + R0, tk1, tk2, tk3, rtk);
    // randomly choose a plaintext
    uint8_t plaintext[16];
    for (int i = 0; i < 16; i++)
        plaintext[i] = rand() & 0xf;
    uint8_t ciphertext[16];
    uint8_t decrypted_plaintext[16];
    
    // Encrypt the plaintext using enc function
    enc(R, plaintext, ciphertext, rtk, Ri, R0);
    // Decrypt the ciphertext using dec function
    dec(R, decrypted_plaintext, ciphertext, rtk, Ri, R0);
    print_state(plaintext);
    print_state(ciphertext);
    print_state(decrypted_plaintext);
    // Compare the original plaintext and the decrypted plaintext
    if (memcmp(plaintext, decrypted_plaintext, sizeof(plaintext)) == 0) {
        printf("Encryption and decryption are consistent. Test passed.\n");
        return 1; // Test passed
    } else {
        printf("Encryption and decryption do not match. Test failed.\n");
        return 0; // Test failed
    }
}


int main()
{
    init_prng();
    int test;
    // #######################################################################################################     
    // Number of rounds
    int R = 14;
    // Fork point (Rinit)
    uint8_t Ri = 7;
    // The length of C0 branch (R0)
    uint8_t R0 = 27;    
    // Number of active cells in the plaintext
    int nap = 1;
    // Position of active cells in the plaintext
    int ap[1] = {14};
    // Number of active cells in tweakey
    int ntk = 3;
    // Position of active cells in the tweakey
    int atk = 0xf;
    // Number of involved cells in ciphertext
    int nb = 2;
    // Position of involved cells in ciphertext
    int balanced_positions[2] = {3, 15};    
    // #######################################################################################################
    test = test_enc_dec_inverse(R, Ri, R0);
    if (test == 0) {
        printf("Test failed. Exiting...\n");
        return 0;
    }    
    uint8_t plaintext[16];
    uint8_t ciphertext[16];
    uint8_t sum1 = 0;
    uint8_t sum2 = 0;
    uint8_t tk1[R + R0][16];
    uint8_t tk2[R + R0][16];
    uint8_t tk3[R + R0][16];
    uint8_t rtk[R + R0][8];
    // randomly choose a tweakey
    for (int i = 0; i < 16; i++)
    {
        tk1[0][i] = rand() & 0xf;
        tk2[0][i] = rand() & 0xf;
        tk3[0][i] = rand() & 0xf;
    }
    tweakey_schedule(R + R0, tk1, tk2, tk3, rtk);
    // randomly choose a plaintext
    for (int i = 0; i < 16; i++)
        plaintext[i] = rand() & 0xf;

    uint64_t utk = (1ULL)<<(4*ntk);
    uint64_t up  = (1ULL)<<(4*nap);
    uint8_t random_fixed_position = rand() & 0xf;
    printf("Number of plaintexts: %lu\n", up);
    for (uint64_t tc = 0; tc < utk; tc++)
    {
        tk1[0][atk] = (tc >> 0) & 0xf;
        tk2[0][atk] = (tc >> 4) & 0xf;
        tk3[0][atk] = (tc >> 8) & 0xf;
        tweakey_schedule(R + R0, tk1, tk2, tk3, rtk);
        // print_state(plaintext, ver);      
        for (uint64_t pc = 0; pc < up; pc++)
        {
            for (int nibble = 0; nibble < nap; nibble++)
            {
                plaintext[ap[nibble]] = (pc >> 4*nibble) & 0xf;
            }
            enc(R, plaintext, ciphertext, rtk, Ri, R0);
            for (int i = 0; i < nb; i++)
            {
                sum1 ^= ciphertext[balanced_positions[i]];                
            }
            sum2 ^= ciphertext[random_fixed_position];
        }
    }
    printf("Target sum: %d\n", sum1);
    printf("Random sum: %d\n", sum2);
    return 0;
}
