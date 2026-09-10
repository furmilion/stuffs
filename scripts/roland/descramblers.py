import time

import numba

#import numpy as np

byte_lut = [
      0,   2, 128, 130,   1,   3, 129, 131,
     64,  66, 192, 194,  65,  67, 193, 195,
      4,   6, 132, 134,   5,   7, 133, 135,
     68,  70, 196, 198,  69,  71, 197, 199,
      8,  10, 136, 138,   9,  11, 137, 139,
     72,  74, 200, 202,  73,  75, 201, 203,
     12,  14, 140, 142,  13,  15, 141, 143,
     76,  78, 204, 206,  77,  79, 205, 207,
     32,  34, 160, 162,  33,  35, 161, 163,
     96,  98, 224, 226,  97,  99, 225, 227,
     36,  38, 164, 166,  37,  39, 165, 167,
    100, 102, 228, 230, 101, 103, 229, 231,
     40,  42, 168, 170,  41,  43, 169, 171,
    104, 106, 232, 234, 105, 107, 233, 235,
     44,  46, 172, 174,  45,  47, 173, 175,
    108, 110, 236, 238, 109, 111, 237, 239,
     16,  18, 144, 146,  17,  19, 145, 147,
     80,  82, 208, 210,  81,  83, 209, 211,
     20,  22, 148, 150,  21,  23, 149, 151,
     84,  86, 212, 214,  85,  87, 213, 215,
     24,  26, 152, 154,  25,  27, 153, 155,
     88,  90, 216, 218,  89,  91, 217, 219,
     28,  30, 156, 158,  29,  31, 157, 159,
     92,  94, 220, 222,  93,  95, 221, 223,
     48,  50, 176, 178,  49,  51, 177, 179,
    112, 114, 240, 242, 113, 115, 241, 243,
     52,  54, 180, 182,  53,  55, 181, 183,
    116, 118, 244, 246, 117, 119, 245, 247,
     56,  58, 184, 186,  57,  59, 185, 187,
    120, 122, 248, 250, 121, 123, 249, 251,
     60,  62, 188, 190,  61,  63, 189, 191,
    124, 126, 252, 254, 125, 127, 253, 255
]
address_order_sc = [
    0x02,0x00,0x03,0x04,0x01,0x09,0x0D,0x0A,
    0x12,0x11,0x06,0x0F,0x0B,0x10,0x08,0x05,
    0x0C,0x07,0x0E,0x13,0x14,0x15,0x16,0x17
]
address_order_srx = [
    0x00,0x04,0x02,0x03,0x01,0x0D,0x07,0x0C,
    0x05,0x0A,0x10,0x09,0x06,0x08,0x0E,0x11,
    0x0B,0x0F,0x12,0x13,0x14,0x15,0x16,0x17
]


@numba.jit
def descramble_address_sc(addr: int) -> int:
    address_order = [
        0x02,0x00,0x03,0x04,0x01,0x09,0x0D,0x0A,
        0x12,0x11,0x06,0x0F,0x0B,0x10,0x08,0x05,
        0x0C,0x07,0x0E,0x13,0x14,0x15,0x16,0x17
    ]
    if addr < 0x24:
        return addr
    out: int = 0
    for bit in range(20):
        out |= ((addr >> address_order[bit]) & 1) << bit
    return out

def descramble_address_srx(addr) -> int:
    address_order = [
        0x00,0x04,0x02,0x03,0x01,0x0D,0x07,0x0C,
        0x05,0x0A,0x10,0x09,0x06,0x08,0x0E,0x11,
        0x0B,0x0F,0x12,0x13,0x14,0x15,0x16,0x17
    ]
    if addr < 0x20:
        return addr
    out = 0
    for bit in range(24):
        out |= ((addr >> address_order[bit]) & 1) << bit
    return out


def descramble_file(file: str = '', out_to: str = '', return_buffer=False, srx=False):
    if not file and not return_buffer: print("nothing to descramble"); return
    if not out_to and not return_buffer: print("nowhere to put"); return
    with open(file, "rb") as r:
        rom = r.read()
    if len(rom) % (1 << 20): print("wrong rom size"); return
    passes = len(rom) // (1 << 20)
    buffer: list[int] = [0 for _ in range((1 << 20) * passes)]
    if srx:
        for pass_ in range(passes):
            for addr in range(1048576):
                if addr < 0x20:
                    buffer[addr + (1048576 * pass_)] = rom[addr + (1048576 * pass_)]
                    continue
                buffer[descramble_address_srx(addr) + (1048576 * pass_)] = byte_lut[rom[addr + (1048576 * pass_)]]
            print(f'bank {pass_ + 1} done')
    else:
        for pass_ in range(passes):
            for addr in range(1048576):
                if addr < 0x20:
                    buffer[addr + (1048576 * pass_)] = rom[addr + (1048576 * pass_)]
                    continue
                buffer[descramble_address_sc(addr) + (1048576 * pass_)] = byte_lut[rom[addr + (1048576 * pass_)]]
            print(f'bank {pass_ + 1} done')
    if return_buffer:
        return buffer
    else:
        with open(out_to, "wb") as output:
            output.write(bytes(buffer))

# BEHOLD! The holy testing area
# You might want to change those
# paths on your machine if you
# decide to run this as a module
# instead of just importing the
# functions and using those.
if __name__ == '__main__':
    print("begin")
    start = time.perf_counter()
    descramble_file(
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_3.bin",
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_3_DED.bin")
    descramble_file(
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_1.bin",
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_1_DED.bin")
    descramble_file(
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_2.bin",
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_2_DED.bin")

    print(f"took {time.perf_counter() - start}")
