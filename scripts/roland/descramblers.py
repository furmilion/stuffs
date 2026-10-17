import time

import numba

#import numpy as np

byte_lut_sc = [
    # SC-55 and relatives byte lookup table.
    # since its literally like 256 entries, i just ran the bit order magic and put ready-to-use values here to avoid speed issues.
    # Bit order: [2, 0, 4, 5, 7, 6, 3, 1]
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

byte_lut_r8 = [
    # byte lut for R-8 and D-70
    # bit order: [1, 2, 7, 3, 5, 0, 4, 6]
      0,  32,   1,  33,   2,  34,   3,  35,
      8,  40,   9,  41,  10,  42,  11,  43,
     64,  96,  65,  97,  66,  98,  67,  99,
     72, 104,  73, 105,  74, 106,  75, 107,
     16,  48,  17,  49,  18,  50,  19,  51,
     24,  56,  25,  57,  26,  58,  27,  59,
     80, 112,  81, 113,  82, 114,  83, 115,
     88, 120,  89, 121,  90, 122,  91, 123,
    128, 160, 129, 161, 130, 162, 131, 163,
    136, 168, 137, 169, 138, 170, 139, 171,
    192, 224, 193, 225, 194, 226, 195, 227,
    200, 232, 201, 233, 202, 234, 203, 235,
    144, 176, 145, 177, 146, 178, 147, 179,
    152, 184, 153, 185, 154, 186, 155, 187,
    208, 240, 209, 241, 210, 242, 211, 243,
    216, 248, 217, 249, 218, 250, 219, 251,
      4,  36,   5,  37,   6,  38,   7,  39,
     12,  44,  13,  45,  14,  46,  15,  47,
     68, 100,  69, 101,  70, 102,  71, 103,
     76, 108,  77, 109,  78, 110,  79, 111,
     20,  52,  21,  53,  22,  54,  23,  55,
     28,  60,  29,  61,  30,  62,  31,  63,
     84, 116,  85, 117,  86, 118,  87, 119,
     92, 124,  93, 125,  94, 126,  95, 127,
    132, 164, 133, 165, 134, 166, 135, 167,
    140, 172, 141, 173, 142, 174, 143, 175,
    196, 228, 197, 229, 198, 230, 199, 231,
    204, 236, 205, 237, 206, 238, 207, 239,
    148, 180, 149, 181, 150, 182, 151, 183,
    156, 188, 157, 189, 158, 190, 159, 191,
    212, 244, 213, 245, 214, 246, 215, 247,
    220, 252, 221, 253, 222, 254, 223, 255
]

address_order_sc = [
    # address byte order of SC-55 and relatives
    # it is a byte order instead of a full lut since it will
    # contain like a million entries and that will certainly
    # make this file big and unreadable
    0x02,0x00,0x03,0x04,0x01,0x09,0x0D,0x0A,
    0x12,0x11,0x06,0x0F,0x0B,0x10,0x08,0x05,
    0x0C,0x07,0x0E,0x13,0x14,0x15,0x16,0x17
]
address_order_srx = [
    # ditto, but SRX expansions instead
    0x00,0x04,0x02,0x03,0x01,0x0D,0x07,0x0C,
    0x05,0x0A,0x10,0x09,0x06,0x08,0x0E,0x11,
    0x0B,0x0F,0x12,0x13,0x14,0x15,0x16,0x17
]
address_order_r8 = [
    # ditto, but R-8
    0x12,0x11,0x08,0x09,0x10,0x0B,0x0C,0x07,
    0x0E,0x0A,0x0D,0x0F,0x03,0x02,0x01,0x06,
    0x04,0x05,0x00,0x13,0x14,0x15,0x16,0x17
]
address_order_d70 = [
    0x12,0x11,0x0F,0x0E,0x10,0x0C,0x0B,0x07,
    0x09,0x0D,0x0A,0x08,0x03,0x02,0x01,0x06,
    0x04,0x05,0x00,0x13,0x14,0x15,0x16,0x17
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

@numba.jit
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

@numba.jit
def descramble_address_r8(addr) -> int:
    address_order = [
        0x12,0x11,0x08,0x09,0x10,0x0B,0x0C,0x07,
        0x0E,0x0A,0x0D,0x0F,0x03,0x02,0x01,0x06,
        0x04,0x05,0x00,0x13,0x14,0x15,0x16,0x17
    ]
    #if addr < 0x20:
        #return addr
    out = 0
    for bit in range(24):
        out |= ((addr >> address_order[bit]) & 1) << bit
    return out
    
@numba.jit
def descramble_address_d70(addr) -> int:
    address_order = [
        0x12,0x11,0x0F,0x0E,0x10,0x0C,0x0B,0x07,
        0x09,0x0D,0x0A,0x08,0x03,0x02,0x01,0x06,
        0x04,0x05,0x00,0x13,0x14,0x15,0x16,0x17
    ]
    if addr < 0x80:
        return addr
    out = 0
    for bit in range(24):
        out |= ((addr >> address_order[bit]) & 1) << bit
    return out

def descramble_file(file: str = '', out_to: str = '', return_buffer=False, _type=0):
    """
    descramble a file according to to 3 of the following algorithms:
        0: SC-55/88 series, JV boards
        1: SRX Expansion cards
        2: R-8 (TODO)
        3: D-70 
    """
    if not file and not return_buffer: print("nothing to descramble"); return [0]
    if not out_to and not return_buffer: print("nowhere to put"); return [0]
    with open(file, "rb") as r:
        rom = r.read()
    if len(rom) % (1 << 20) and _type in [0, 1]: print("wrong rom size"); return [0]
    elif _type in [2, 3] and len(rom) % (1 << 19): print("wrong rom size"); return [0]
    if _type in [0, 1]:
        passes = len(rom) // (1 << 20)
        buffer: list[int] = [0 for _ in range((1 << 20) * passes)]
    elif _type in [2, 3]:
        passes = len(rom) // (1 << 19)
        buffer: list[int] = [0 for _ in range((1 << 19) * passes)]
    match _type:
        case 0:
            for pass_ in range(passes):
                for addr in range(1048576):
                    if addr < 0x20:
                        buffer[addr + (1048576 * pass_)] = rom[addr + (1048576 * pass_)]
                        continue
                    buffer[descramble_address_sc(addr) + (1048576 * pass_)] = byte_lut_sc[rom[addr + (1048576 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 1:
            for pass_ in range(passes):
                for addr in range(1048576):
                    if addr < 0x20:
                        buffer[addr + (1048576 * pass_)] = rom[addr + (1048576 * pass_)]
                        continue
                    buffer[descramble_address_srx(addr) + (1048576 * pass_)] = byte_lut_sc[rom[addr + (1048576 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 2:
            for pass_ in range(passes):
                for addr in range(524288):
                    if addr < 0x20:
                        buffer[addr + (524288 * pass_)] = rom[addr + (524288 * pass_)]
                        continue
                    buffer[descramble_address_r8(addr) + (524288 * pass_)] = byte_lut_r8[rom[addr + (524288 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 2:
            for pass_ in range(passes):
                for addr in range(524288):
                    if addr < 0x20:
                        buffer[addr + (524288 * pass_)] = rom[addr + (524288 * pass_)]
                        continue
                    buffer[descramble_address_r8(addr) + (524288 * pass_)] = byte_lut_r8[rom[addr + (524288 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 3:
            for pass_ in range(passes):
                for addr in range(524288):
                    if addr < 0x80:
                        buffer[addr + (524288 * pass_)] = rom[addr + (524288 * pass_)]
                        continue
                    buffer[descramble_address_d70(addr) + (524288 * pass_)] = byte_lut_r8[rom[addr + (524288 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case _:
            return [0]
    if return_buffer:
        return buffer
    else:
        with open(out_to, "wb") as output:
            output.write(bytes(buffer))

def descramble_file_VERY_FUCKING_FAST(file: str = '', out_to: str = '', return_buffer=False, _type=0):
    """
    ughh luts in function
    """
    local_byte_lut_sc = [
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
        124, 126, 252, 254, 125, 127, 253, 255]
    local_byte_lut_r8 = [
          0,  32,   1,  33,   2,  34,   3,  35,
          8,  40,   9,  41,  10,  42,  11,  43,
         64,  96,  65,  97,  66,  98,  67,  99,
         72, 104,  73, 105,  74, 106,  75, 107,
         16,  48,  17,  49,  18,  50,  19,  51,
         24,  56,  25,  57,  26,  58,  27,  59,
         80, 112,  81, 113,  82, 114,  83, 115,
         88, 120,  89, 121,  90, 122,  91, 123,
        128, 160, 129, 161, 130, 162, 131, 163,
        136, 168, 137, 169, 138, 170, 139, 171,
        192, 224, 193, 225, 194, 226, 195, 227,
        200, 232, 201, 233, 202, 234, 203, 235,
        144, 176, 145, 177, 146, 178, 147, 179,
        152, 184, 153, 185, 154, 186, 155, 187,
        208, 240, 209, 241, 210, 242, 211, 243,
        216, 248, 217, 249, 218, 250, 219, 251,
          4,  36,   5,  37,   6,  38,   7,  39,
         12,  44,  13,  45,  14,  46,  15,  47,
         68, 100,  69, 101,  70, 102,  71, 103,
         76, 108,  77, 109,  78, 110,  79, 111,
         20,  52,  21,  53,  22,  54,  23,  55,
         28,  60,  29,  61,  30,  62,  31,  63,
         84, 116,  85, 117,  86, 118,  87, 119,
         92, 124,  93, 125,  94, 126,  95, 127,
        132, 164, 133, 165, 134, 166, 135, 167,
        140, 172, 141, 173, 142, 174, 143, 175,
        196, 228, 197, 229, 198, 230, 199, 231,
        204, 236, 205, 237, 206, 238, 207, 239,
        148, 180, 149, 181, 150, 182, 151, 183,
        156, 188, 157, 189, 158, 190, 159, 191,
        212, 244, 213, 245, 214, 246, 215, 247,
        220, 252, 221, 253, 222, 254, 223, 255]
    if not file and not return_buffer: print("nothing to descramble"); return [0]
    if not out_to and not return_buffer: print("nowhere to put"); return [0]
    with open(file, "rb") as r:
        rom = r.read()
    if len(rom) % (1 << 20) and _type in [0, 1]: print("wrong rom size"); return [0]
    elif _type in [2, 3] and len(rom) % (1 << 19): print("wrong rom size"); return [0]
    if _type in [0, 1]:
        passes = len(rom) // (1 << 20)
        buffer: list[int] = [0 for _ in range((1 << 20) * passes)]
    elif _type in [2, 3]:
        passes = len(rom) // (1 << 19)
        buffer: list[int] = [0 for _ in range((1 << 19) * passes)]
    match _type:
        case 0:
            for pass_ in range(passes):
                for addr in range(1048576):
                    if addr < 0x20:
                        buffer[addr + (1048576 * pass_)] = rom[addr + (1048576 * pass_)]
                        continue
                    buffer[descramble_address_sc(addr) + (1048576 * pass_)] = local_byte_lut_sc[rom[addr + (1048576 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 1:
            for pass_ in range(passes):
                for addr in range(1048576):
                    if addr < 0x20:
                        buffer[addr + (1048576 * pass_)] = rom[addr + (1048576 * pass_)]
                        continue
                    buffer[descramble_address_srx(addr) + (1048576 * pass_)] = local_byte_lut_sc[rom[addr + (1048576 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 2:
            for pass_ in range(passes):
                for addr in range(524288):
                    if addr < 0x20:
                        buffer[addr + (524288 * pass_)] = rom[addr + (524288 * pass_)]
                        continue
                    buffer[descramble_address_r8(addr) + (524288 * pass_)] = local_byte_lut_r8[rom[addr + (524288 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case 3:
            for pass_ in range(passes):
                for addr in range(524288):
                    if addr < 0x80:
                        buffer[addr + (524288 * pass_)] = rom[addr + (524288 * pass_)]
                        continue
                    buffer[descramble_address_d70(addr) + (524288 * pass_)] = byte_lut_r8[rom[addr + (524288 * pass_)]]
                print(f'bank {pass_ + 1} done')
        case _:
            return [0]
    if return_buffer:
        return buffer
    else:
        with open(out_to, "wb") as output:
            print("shart")
            output.write(bytes(buffer))

# BEHOLD! The holy testing area
# You might want to change those
# paths on your machine if you
# decide to run this as a module
# instead of just importing the
# functions and using those.
if __name__ == '__main__':
    # print("begin")
    start = time.perf_counter()
    # descramble_file(
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom1.bin",
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom1_DED.bin")
    # descramble_file(
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom2.bin",
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom2_DED.bin")
    # print(f"took {time.perf_counter() - start}")
    # print("begin")
    # start = time.perf_counter()
    # descramble_file_VERY_FUCKING_FAST(
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom1.bin",
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom1_DED.bin")
    # descramble_file_VERY_FUCKING_FAST(
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom2.bin",
    # r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom2_DED.bin")
    # start = time.perf_counter()
    descramble_file_VERY_FUCKING_FAST(
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\very h\Wave ROMs\Roland\Roland D-70\roland_d70_waverom-a.bin",
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\very h\Wave ROMs\Roland\Roland D-70\roland_d70_waverom-a_DED.bin", _type=3)
    print(f"took {time.perf_counter() - start}")
