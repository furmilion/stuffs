"""
A module with various useful functions used in other files.
Imports: random, os if needed, hashlib
"""

from luts import ASCII_lut_arr
import random
from math import *
#from typing import Any

try:
    import argparse
except ModuleNotFoundError:
    pass
from hashlib import sha512, sha256, md5
from os import mkdir, remove as rm, name as osName
posix = osName == "posix"
nt = osName == "nt"

def pain(*args):  # i typoed print once
    print(*args)

def types(*variables):
    return [type(_()) for _ in variables]
import builtins as bi  # bi <3
# i'll write a better list function here later;
# it will pick either list or np.array depending on availability of numpy

try:  # numpy is a better option than standard python list stuff
    import numpy as np
    NUMPY = True
    #print("nupi")
    from numpy import uint8 as char, uint8 as uchar, int8 as schar, uint8 as uint8_t, int8 as int8_t
    from numpy import byte, ubyte
    from numpy import ushort, short, uint16 as uint16_t, int16 as int16_t
    from numpy import ulong, long, uint32 as uint32_t, int32 as int32_t
    from numpy import ulonglong, longlong, uint64 as uint64_t, int64 as int64_t
    from numpy import float32 as float, single, double
    try: from numpy import float96 as triple
    except ImportError: pass
    try: from numpy import float128 as quadruple
    except ImportError: pass
    from numpy import half, longdouble as veryfloat

    def swap_sign(int_type):
        match int_type:
            case np.uint8:  return byte
            case np.uint16: return short
            case np.uint32: return long
            case np.uint64: return longlong
            case np.int8:  return ubyte
            case np.int16: return ushort
            case np.int32: return ulonglong
            case np.int64: return ulonglong
            case _: return int_type
    def is_signed(int_type):
        match int_type:
            case np.uint8 | np.uint16 | np.uint32 | np.uint64:  return False
            case np.int8 | np.int16 | np.int32 | np.int64:  return True
            case _: return False
    
except Exception as e:
    print("NumPY not found.\n"
          "It is recommended to install NumPY as this offers slightly better performance.\n"
          f"Ecxeption: {e}\n"
          f"Type: {type(e)}")
    NUMPY = False
    char, uchar, schar,\
    uint8_t, int8_t,\
    ushort, uint16_t, short, int16_t,\
    ulong, uint32_t, long, int32_t,\
    ulonglong, uint64_t, longlong, int64_t,\
    double, longdouble =\
    (
        bi.int, bi.int, bi.int,
        bi.int, bi.int,
        bi.int, bi.int, bi.int, bi.int,
        bi.int, bi.int, bi.int, bi.int,
        bi.int, bi.int, bi.int, bi.int,
        bi.float, bi.float
    )
    f16 = bi.float
    def swap_sign(int_type):
        return int_type



def test_file(path: str = ".") -> bool:
    try:
        open(f"{path}/test.test", 'xb')
        print("opening test")
    except (FileExistsError, FileNotFoundError) as e:
        if isinstance(e, FileExistsError):
            rm(f"{path}/test.test")
            print("test success")
            return True
        elif isinstance(e, FileNotFoundError):
            print("test not success")
            return False
    print("test success")
    return True
def _():
    """
    a wrapper for pass.
    """
    pass

def text_from_bytes(data: bytes | list = None, minlen: int = 0) -> str:
    if not data:
        print("must data")
        return ""
    a = ""
    for i in data:
        a += ASCII_lut_arr[i]
    if minlen:
        while len(a) < minlen:
            a += " "
    return a

def clamp(val: float | int = 0, mn: float | int = 0, mx: float | int = 9) -> float | int:
    """
    Clamps value to a range.
    :param val: the value
    :param mn: the lowest boundary
    :param mx: the highest boundary
    :return: clamped value
    """
    #return max(mn, val) if val <= mn else min(val, mx) if val <= mx else mx
    return min(mx, max(mn, val)) # how did i not think of this

def pack_byte(bits=None) -> int:
    """Pack 8 bits into a byte. Excess input will be discarded."""
    output = 0
    if bits is None:
        return 0
    if type(bits) in [int, float]:
        bits = [bits]
    if len(bits) < 8:
        for i in range(8 - len(bits)):
            bits.append(0)
    for i in range(8):
        output += bits[i] << (7 - i)
    return output


def explode_byte(bit: int = 255) -> list[int]:
    """Explode a byte into a list of 8 bits. Excess bits are discarded."""
    bits = [1, 1, 1, 1, 1, 1, 1, 1]
    for i in range(8):
        bits[i] = (bit >> (7 - i)) & 1
    return bits

def log(*args, **kwargs) -> None:
    pass

def round_to_closest(l,u,v) -> int:
    """
    Rounds a value to closest in supplied range.
    Works identical to normal round(): rounds down if the value is less than delta, rounds up otherwise.
    Delta is calculated by adding lower and upper values and dividing the result by 2.
    """
    return l if v < (l + u)/2 else u

# removed: save_riff()
# removed: make_dpcm()
# removed: split_file()
# removed: ternary()

def check_bytes(in_file, val):
    """
    Obsolete.

    This function checks hardcoded amount of bytes (4) in input file to see if they are a specified value.
    If so, it returns len(<input file>).
    """
    # checking every 4 if they are [val]
    # if so, we discard them
    with open(in_file, 'rb') as f:
        data = f.read()
        start_from = len(data) - 1
        condition = True
        while condition:
            # the loop we use
            bt4 = data[start_from]
            bt3 = data[start_from - 1]
            if bt4 == bt3 and bt4 == val and bt3 == val:
                condition = True
            else:
                condition = False
            bt2 = data[start_from - 2]
            if bt3 == bt2 and bt3 == val and bt2 == val:
                condition = True
            else:
                condition = False
            bt1 = data[start_from - 3]
            if bt2 == bt1 and bt2 == val and bt1 == val:
                condition = True
            else:
                condition = False
            start_from -= 4
        f.close()
        return start_from + 5

class PtrManager:
    """
    Why did i make this? nobody knows.
    """
    def __init__(self):
        self.pointers = {}

    def add_pointer(self, pointer_value, pointer_name: str = None):
        self.pointers[f"pointer{len(self.pointers)}" if not pointer_name else pointer_name] = pointer_value if pointer_value else 0

    def get_pointer(self, pointer_name: str = None):
        return self.pointers[pointer_name] if pointer_name else 0

    def remove_pointer(self, pointer_name: str = None):
        self.pointers.pop(pointer_name) if pointer_name else 0

    def update_pointer(self, pointer_value, pointer_name: str = None):
        self.add_pointer(pointer_value, pointer_name) if pointer_name else 0

def combine_odd_even(file1: list = None, file2: list = None) -> np.ndarray | None:
    """
    i have no idea how to describe this but what it does is basically
    combine whatever 2 input files it was given by sliding bytes of the
    files inbetween eachother
    """
    match (not file1, not file2):
        case (True, True):
            raise ValueError("input requred")
        case (True, False):
            return file2
        case (False, True):
            return file1

    final_len = min(len(file1), len(file2))
    arr = np.array([0 for _ in range(final_len * 2)], ubyte)
    for i in range(0, final_len):
        if not i % (1 << 16):
            print(i)
        arr[i * 2] = file1[i]
        arr[i * 2 + 1] = file2[i]
    return arr
    #return b'what'

def ret_hash(data, mode="md5", **kwargs):
    """
    A quick way to get hash in one of these modes:
        - SHA512
        - SHA256
        - MD5
    """
    if mode.lower() == "sha512":
        hash = sha512()
        hash.update(data)
        return hash.hexdigest()
    elif mode.lower() == "sha256":
        hash = sha256()
        hash.update(data)
        return hash.hexdigest()
    elif mode.lower() == "md5":
        hash = md5()
        hash.update(data)
        return hash.hexdigest()
    else:
        return "Unknown mode."


def write_ins(instype=28, samples=None, name="Instrument"):
    if samples is None:
        samples = []
    elif len(samples) == 1:
        samples = samples[0]
    # will be finished, some day
    """
    Writes a proper Furnace Tracker instrument, with samples if provided.
    """
    data = (f"FINS\xE6{chr(instype)}\x1C{chr(len(name) + 1)}\x00{name}\x00"  # main stuff
            f"MA\x0c\x00\x08\x00\x00\x01\xff\xff\x00\x00\x00\x01\x7f")    # macros: volume 127
    data = ["FINS", 0xE6, instype, "NA", len(name) + 1, name, 0x00,
            "MA", ]

def convert_12_to_16(data12: list[int] | bytes = None):
    if not data12: return [0, 0]
    data16 = [0 for _ in range((len(data12) * 2) // 3)]
    #pain(f"data16 array len {len(data16)}")
    #pain(f"data12 in array len {len(data12)}")
    i, j = 0, 0
    while i < len(data16):
        data16[i + 0] = (data12[j + 0] << 8) | (data12[j + 1] & 0xf0)
        if (i + 1) < len(data16):
            data16[i + 1] = (data12[j + 2] << 8) | ( (data12[j + 1] << 4) & 0xf0)
        i += 2
        j += 3
    #print(f"sample {i} byte {i}")
    return data16
        

def get_sample_data(raw, chip_type="m"):
    """
    Returns contents of a 12-byte instrument header
    of MultiPCM-like chips, those being Sega MultiPCM itself (also known as Yamaha YMW258-F) and
    Yamaha OPL4, also known as Yamaha YMF278-F.
    Takes any data as input data and any text as mode.
    If first letter of mode matches 'm', return MultiPCM data, if matches 'o', return OPL4 data, return None otherwise.
    """
    match chip_type[0]:
        case "o" :  # OPL4 (YMF278B)
            return (
                (((raw[0x0000] & 0x3F) << 16 ) |                        #  0. start address
                  (raw[0x0001] << 8) |
                  (raw[0x0002])),

                ( (raw[0x0000] >> 6) & 0b11),                           #  1. data format (0: 8bit, 1: 12bit, 2: 16bit)

                ( (raw[0x0003] << 8) |                                  #  2. loop start
                  (raw[0x0004]) + 1),

                (0xFFFF ^ (
                  (raw[0x0005] << 8) |                                  #  3. sample length in samples, caps at 65535
                  (raw[0x0006]))),

                ( (raw[0x0008] >> 4) & 0x0F),                           #  4. instrument attack rate
                (  raw[0x0008] & 0x0F),                                 #  5. instrument decay 1 rate

                (  raw[0x0009] & 0x0F),                                 #  6. instrument decay 2 rate
                ( (raw[0x0009] >> 4) & 0x0F),                           #  7. instrument decay level

                (  raw[0x000A] & 0x0F),                                 #  8. instrument release rate
                ( (raw[0x000A] >> 4) & 0x0F),                           #  9. instrument rate envelope correction

                (  raw[0x0007] & 0b111),                                # 10. vibrato strength
                (  raw[0x000B] & 0b111),                                # 11. amplitude modulation strength
                ( (raw[0x0007] >> 3) & 0b111),                          # 12. lfo speed
            )
        case "8" | "m":  # MultiPCM (GEW8, YMW258-F, Sega 315-5560)
            # MAME emulator at src/devices/sound/multipcm.cpp says that the chip has
            # FM support, referencing Edward d-tech's article.
            # I myself don't really believe it does, and I think it is exclusively a
            # sample chip. Well, we'll never know until Saturn gets one on his hands,
            # which is pretty unlikely considering it's a quad package and has to be
            # soldered off board first and is unlikely to be on sale by itself from
            # factory.
            # MU5 note: it only uses 21 address bits.
            return (
                (((raw[0x0000] & 0x3F) << 16) |  # 0. start address; there is one free bit as the address space is
                 (raw[0x0001] << 8) |            #                 ; still 22 bits.
                 (raw[0x0002])),                 #
                                                 #
                ((raw[0x0000] >> 6) & 1),        # 1. data format (0: 8bit, 1: 12bit)
                                                 #
                ((raw[0x0003] << 8) |            # 2. loop start
                 (raw[0x0004]) + 1),             #
                                                 #
                (0x10000 - (                     #
                        (raw[0x0005] << 8) |     # 3. sample length in samples, caps at 65535
                        (raw[0x0006]))),         #
                                                 #
                ((raw[0x0008] >> 4) & 0x0F),     # 4. instrument attack rate
                (raw[0x0008] & 0x0F),            # 5. instrument decay 1 rate
                                                 #
                (raw[0x0009] & 0x0F),            # 6. instrument decay 2 rate
                ((raw[0x0009] >> 4) & 0x0F),     # 7. instrument decay level
                                                 #
                (raw[0x000A] & 0x0F),            # 8. instrument release rate
                ((raw[0x000A] >> 4) & 0x0F),     # 9. instrument rate envelope correction
                                                 #
                (raw[0x0007] & 0b111),           # 10. vibrato strength
                (raw[0x000B] & 0b111),           # 11. amplitude modulation strength
                ((raw[0x0007] >> 3) & 0b111),    # 12. lfo speed
            )
        case "7" :  # GEW7 (YMW270-F)
            return (
                (((raw[0x0000] & 0x1F) << 16) | # 0. start address
                  (raw[0x0001] << 8) |          #
                  (raw[0x0002])) & 0x1fffff,    # ;; address space is much smaller. huh
                                                #
                 ((raw[0x0000] >> 6) & 0b11),   # 1. data format (0: 8bit, 1: 12bit)
                                                #
                 ((raw[0x0003] << 8) |          # 2. loop start ;; how does it even work lmao
                  (raw[0x0004]) + 1),           #
                                                #
                (0x4000 - (                     #
                  (raw[0x0005] << 8) |          # 3. sample length in samples, caps at... 16384 for GEW7??? huh.
                  (raw[0x0006]))),              #
                                                # ;; ADSR is laid slightly different compared to GEW8
                 ((raw[0x0009] >> 4) & 0x0F),   # 4. instrument attack rate
                  (raw[0x0009] & 0x0F),         # 5. instrument decay 1 rate
                                                #
                 ((raw[0x000A] >> 4) & 0x0F),   # 6. instrument decay 2 rate
                  (raw[0x000B] & 0x0F),         # 7. instrument decay level
                                                #
                  (raw[0x000A] & 0x0F),         # 8. instrument release rate
                 ((raw[0x000B] >> 4) & 0x0F),   # 9. instrument rate envelope correction
                                                #
                  (raw[0x0007] & 0b111),        # 10. vibrato strength
                  (raw[0x0008] & 0b111),        # 11. amplitude modulation strength
                 ((raw[0x0007] >> 3) & 0b111),  # 12. lfo speed ;; ???????
            )
        case _:
            raise ValueError("Invalid chip type!")


# АХТУНГ ДЕТКА

def fnum_from_freq(freq, block, clock=14000000):
    return freq * (2 ** 19) / (clock / 288) / (2 ** (block - 1))
def fnum_from_freq_opll(freq, block, clock=3579545):
    return freq * (2 ** 19) / (clock / 36) / (2 ** (block - 1))
def opll_get_freq(reg10, reg20):
    return (((reg20 & 1) << 8) + reg10), ((reg20 & 0b1110) >> 1)

def fnum_from_freq_general(freq, block, clock=3579545, divider=36):
    return freq * (2 ** 19) / (clock / divider) / (2 ** (block - 1))

def freq_from_fnum():
    pass

def binarify(string: str = '', split: int = 4):
    a = ''
    for idx, char in enumerate(string):
        if split > 0:
            if not idx % split and idx > 0:
                a += ' '
        b = bin(bytes(char, 'utf8')[0])[2:]
        while len(str(b)) < 8:
            b = '0' + b
        a += b
    return a

def note_from_key(key: int = 0):
    octave = key//12
    notes = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
    notes_neg = ["c_", "c+", "d_", "d+", "e_", "f_", "f+", "g_", "g+", "a_", "a+", "b_"]
    if key >= 0:
        while key > 11:
            key -= 12
        return notes[key] + str(octave)
    elif key < 0:
        while key < 0:
            key += 12
        return notes_neg[key] + str(-octave)
    

if __name__ == "__main__":
    #save_riff(bdep=16, rate=44100, data=pcm12_to_16(open("./tests/amen_12", "rb").read()), location="./tests/amen_12.wav")
    # a_n5 = opll_get_freq(0x09, 0x10)
    # a_n4 = opll_get_freq(0x12, 0x10)
    # a_n3 = opll_get_freq(0x24, 0x10)
    # a_n2 = opll_get_freq(0x49, 0x10)
    # a_n1 = opll_get_freq(0x91, 0x10)
    # a_0  = opll_get_freq(0x22, 0x11)
    # a_1  = opll_get_freq(0x22, 0x13)
    # a_2  = opll_get_freq(0x22, 0x15)
    # a_3  = opll_get_freq(0x22, 0x17)
    # a_4  = opll_get_freq(0x22, 0x19)
    # a_5  = opll_get_freq(0x22, 0x1b)
    # a_6  = opll_get_freq(0x22, 0x1d)
    # a_7  = opll_get_freq(0x22, 0x1f)
    # a_8  = opll_get_freq(0xff, 0x1f)
    # print(f'{a_n5}\n{a_n4}\n'
    #       f'{a_n3}\n{a_n2}\n'
    #       f'{a_n1}\n{a_0}\n'
    #       f'{a_1}\n{a_2}\n'
    #       f'{a_3}\n{a_4}\n'
    #       f'{a_5}\n{a_6}\n'
    #       f'{a_7}\n{a_8}\n')
    # print(
    #     f"{generate_sine_table(256, char(255), 0)}\n"
    #     f"{generate_sine_table(256, schar(127), 1)}\n"
    #     f"{generate_sine_table(256, ushort(65535), 0)}\n"
    #     f"{generate_sine_table(256, short(32767), 1)}\n"
    # )
    
    # example and also debug usage of wave table generator
    # import FurWave
    # import funcs_wavegens
    # with FurWave.WaveWriter(
    #     channels = 1,
    #     samplerate = 16743,
    #     data = funcs_wavegens.generate_fn_table_advanced(128, short(32767), 1, atan, e*e*e)
    # ) as w:
    #     w.write_file("_htest.wav")
    fp = r"E:\D Drive (HDD)\PycharmProjects\BananaBot\mpt2fur\rom stuff\roms\roms\sw1000xg"
    open(
        f"{fp}/wave1_16m.raw",
        "wb"
    ).write(
        combine_odd_even(
            list(open(f"{fp}/xv389a0.ic122", "rb").read()),
            list(open(f"{fp}/xv390a0.ic121", "rb").read())
        )
    )
    open(
        fr"{fp}/wave2_4m.raw",
        "wb"
    ).write(
        combine_odd_even(
            list(open(f"{fp}/xt445a0-828.ic124", "rb").read()),
            list(open(f"{fp}/xt461a0-829.ic123", "rb").read())
        )
    )
    a = np.array([0], ushort)