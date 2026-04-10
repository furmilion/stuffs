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
from os import mkdir, remove as rm

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
    from numpy import float32 as float, single, double, float96 as triple, float128 as quadruple
    from numpy import half, longdouble as veryfloat
    def swap_sign(int_type):
        match int_type:
            case byte: return char
            case schar(): return uchar
            case ushort(): return short
            case short(): return ushort
            case ulong(): return long
            case long(): return ulong
            case ulonglong(): return longlong
            case longlong(): return ulonglong
            case _: return int_type
                
    
except ImportError:
    print("NumPY not found.\n"
          "It is recommended to install NumPY as this offers slightly better performance.")
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


def generate_sine_table(length: int = 1, max: int = 1, signed: bool = True):
    """
    Generates a numpy.ndarray of values of
    sin(math.tau/length*x) across "length" values.
    """
    if not NUMPY:
        return "nah"
    match (type(max)):
        case np.uint8:  # numpy types override signs
            #print("shart")
            #print(type(max) == schar)
            return np.array(
                [
                    round(
                        (sin(tau / length * x) + 1)
                        * max / 2
                    ) for x in range(length)
                ], char
            )
        case np.int8:
            return np.array(
                [
                    round(
                        (sin(tau / length * x))
                        * (f16(max&127) + .5) - .5
                    ) for x in range(length)
                ], schar
            )
        case np.uint16:  # numpy types override signs
            #print("shart")
            #print(type(max) == schar)
            return np.array(
                [
                    round(
                        (sin(tau / length * x) + 1)
                        * max / 2
                    ) for x in range(length)
                ], ushort
            )
        case np.int16:
            return np.array(
                [
                    round(
                        (sin(tau / length * x))
                        * (float(max&32767) + .5) - .5
                    ) for x in range(length)
                ], short
            )
        
        case bi.int:  # placeholder
            return 1
        case _:
            return "unimplemented"
        

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


def ternary(condition, true, false):
    """
    Obsolete since guarded conditions
    :param condition:
    :param true:
    :param false:
    :return:
    """
    if condition:
        return true
    else:
        return false

def log(*args, **kwargs) -> None:
    pass

def round_to_closest(l,u,v) -> int:
    """
    Rounds a value to closest in supplied range.
    Works identical to normal round(): rounds down if the value is less than delta, rounds up otherwise.
    Delta is calculated by adding lower and upper values and dividing the result by 2.
    """
    return l if v < (l + u)/2 else u

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


class SaveError(Exception):
    pass
# legacy, try FurWave first before falling back to this
def save_riff(#bdep=8, rate=32000, data="sample", loop_start=None, loop_end=None, location="./output.wav",
              **kwargs) -> None or int:  # I have no idea what that "-> tuple" means
    """
    This really is a legacy function, you should use FurWAVE instead as it supports floating point and generally has more features.
    
    
    Saves an audio file of desired bit depth at desired sample rate with provided data,
    and loop points if specified, at specified location.
    Only supports fixed-point Linear PCM, not floating point.
    According to Microsoft WAVE format, only following bit depths are allowed:
    [8, 16, 24, 32].

    The thing stopping you from having an arbitrary bit depth is so-called 'Bytes per Block' value.
    As you might've guessed, it is a hexadecimal representation of an integer.
    Despite there being proper channel + bit depth configurations, it is likely that your
    audio player would not play the file properly, or at all.

    This function was made specifically for use with Furnace Tracker (github.com/tildearrow/furnace)

    As of committing this comment, I am planning to replace this backbone with a proper writer function/class,
    which most likely will be based on Cockos' WDL Library Wave Writer.
    """
    # We'll put everything in a nice big fat juicy try block to print out errors if there are any
    try:
        verbose = kwargs["verbose"] if "verbose" in kwargs else False
        try: verbose = bool(verbose)
        except TypeError: verbose = False

        bdep = kwargs["bdep"] if "bdep" in kwargs else 8
        rate = floor(kwargs["rate"]) if "rate" in kwargs else 32000
        data = kwargs["data"] if "data" in kwargs else [random.randint(0, 255) for _ in range(256*(bdep//8))]
        loop_type = kwargs["loop_type"] if "loop_type" in kwargs else 0
        loop_start = kwargs["loop_start"] if "loop_start" in kwargs else (len(data) // (bdep//8))
        loop_end = kwargs["loop_end"] - 1 if "loop_end" in kwargs else (len(data) // (bdep//8)) - 1
        location = kwargs["location"] if "location" in kwargs else "./output.wav"

        if type(loop_start) == int:
            if loop_start < 0:
                loop_start = 0
        if type(loop_end) == int:
            if loop_end < 0:
                loop_end = (len(data) // (bdep//8)) - 1
        else:
            loop_end = len(data) - 1
        if str(loop_type).lower() in ["forwards", "forward", "fw", "f", "0"]:
            loop_type = 0
        elif str(loop_type).lower() in ["backwards", "backward", "bw", "f", "2"]:
            loop_type = 2
        elif str(loop_type).lower() in ["pingpong", "ping-pong", "ping", "pong", "1", "p"]:
            loop_type = 1
        else:
            loop_type = 0

        if verbose: print(f"args: {kwargs}\n"
                          "vals: "
                          "{'verbose': %s, 'bdep': %s, 'rate': %s,"
                          "'data': %s, 'loop_start': %s, 'loop_end': %s, 'location': %s}"
                          % (verbose, bdep, rate, data, loop_start, loop_end, location))

        rate &= 0xFFFFFF # technically 4-bit, but furnace refuses to recognize those
        if bdep % 8:
            print("Bad bit depth (not divisible by 8)")
            bdep -= bdep % 8
        blka = (1 * bdep)//8
        rate2 = (rate * blka) & 0xFFFFFFFF
        # Sample bit depth seems to be simple, a single byte to indicate bytes per samples:
        # 1 for 8-bit, 2 for 16-bit and so on.
        # Floating point samples seem to be using another method to store data, but we're not interested in that.
        important = [0x52, 0x49, 0x46, 0x46,    # RIFF header
                     0x00, 0x00, 0x00, 0x00,    # The size of the data after this block
                     0x57, 0x41, 0x56, 0x45,    # 'WAVE' block
                     0x66, 0x6D, 0x74, 0x20,    # 'fmt ' block
                     0x10, 0x00, 0x00, 0x00,    # Chunk size or something. 16.
                     0x01, 0x00, 0x01, 0x00,    # Linear PCM, 1 channel
                     rate & 0xFF,  (rate >> 8) & 0xFF,  (rate >> 16) & 0xFF,  (rate >> 24) & 0xFF,  # Sample rate
                     rate2 & 0xFF, (rate2 >> 8) & 0xFF, (rate2 >> 16) & 0xFF, (rate2 >> 24) & 0xFF,  # Byte rate
                     blka, 0x00, bdep, 0x00,    # Block align and bit depth
                     0x73, 0x6D, 0x70, 0x6C,    # 'smpl' block
                     0x3C, 0x00, 0x00, 0x00,    # Block size.
                     0x00, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00,
                        0,    0, 0x00, 0x00,    # No idea what those 2 bytes are
                        0,    0,    0,    0,    # help
                        0,    0,    0,    0,    # loop pont marker? the text is ")\ÅB"
                        0,    0,    0,    0,
                        0,    0,    0,    0,
                     0x01, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00,    # some more data
                     0x00, 0x00, 0x00, 0x00,
                     loop_type, 0x00, 0x00, 0x00,    # even more
                     # loop points
                     loop_start & 0xFF, (loop_start >> 8) & 0xFF, (loop_start >> 16) & 0xFF, (loop_start >> 24) & 0xFF,
                     loop_end & 0xFF,   (loop_end >> 8) & 0xFF,   (loop_end >> 16) & 0xFF,   (loop_end >> 24) & 0xFF,
                     0x00, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00,    # some more unknown data
                     0x64, 0x61, 0x74, 0x61,    # 'data' block
                     0x00, 0x00, 0x00, 0x00     # size of that shit
                     ]
        # TODO: actually make a proper wav writing class
        length_real = len(data) + 0x64
        new_data = []
        if max(data) > 255:
            for i in range(len(data)):
                new_data.append(data[i] >> 8)
                new_data.append(data[i] & 255)
        data = new_data
        del new_data
        data_length = len(data)
        important[4] = length_real & 0xFF
        important[5] = (length_real >> 8) & 0xFF
        important[6] = (length_real >> 16) & 0xFF
        important[7] = (length_real >> 24) & 0xFF
        important[-4] = data_length & 0xFF
        important[-3] = (data_length >> 8) & 0xFF
        important[-2] = (data_length >> 16) & 0xFF
        important[-1] = (data_length >> 24) & 0xFF

        if type(data) is str:
            data = bytes(data, "utf8")
        elif type(data) in [list, bytes, bytearray]:
            data = bytes(data)
        elif NUMPY and type(data) is np.ndarray:
            data = np.array(list(data), np.uint8)
        else:
            raise ValueError(f"data has died. (type: {type(data)})")
        if NUMPY:
            data = np.array(list(data), np.uint8)
            header = np.array(list(important), np.uint8)
        else:
            header = important
        # header    = b'RIFF' # RIFF header
        # length    = b'' # Length of the rest of the file, will be calculated later
        # important = b'WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00' # important data or something
        # rate_real = bytes([(rate >> 8) & 0xff,   # sample rate, seems to be 3 bytes long
        #                    (rate >> 16) & 0xff,
        #                    (rate >> 24) & 0xff]) # FIFO: first in, first out
        try:
            h = open(location, "xb")
            h.write(bytes(header) + bytes(data))
            h.close()
        except FileExistsError:
            #print("File already present, overwriting...")
            h = open(location, "wb")
            h.write(bytes(header) + bytes(data))
            h.close()
        if verbose: return bytes(header) + bytes(data)
        else: return 1
    except Exception as e:
        print("Error saving file: %s" % e)
        raise SaveError(e)


def pcm12_to_16(data: bytes = None):
    if not data:
        return [0, 0] # TODO: check how furnace does this

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




def split_file(file: str, output_folder: str, length=32136, dpcm_rate=15, type=0) -> None:
    """
    This is really useless to normal user, to me even. I made this to goof around with Furnace's 256k NES sample ROM limitation.
    
    This function takes any raw data as an input and splits it into chunks, each of
    length specified by the parameter, or less.

    :param file: The input file to split.
    :param length: The length of each chunk.
    :param output_folder: The output folder for resulting split files.
    :param dpcm_rate: Specifies the NES DPCM rate, if applicable. 15 if not set.
    :param type: Specifies the type of NES machine, if applicable. 0: NTSC, 1: PAL. This affects playback frequency slightly.
    :return:
    """
    dpcm_rates_table_ntsc = {
         0: 4182,   1: 4710,   2: 5264,   3: 5593,
         4: 6258,   5: 7046,   6: 7919,   7: 8363,
         8: 9420,   9: 11186, 10: 12604, 11: 13983,
        12: 16885, 13: 21307, 14: 24858, 15: 33144,
    }
    dpcm_rates_table_pal = {
         0: 4177,   1: 4697,   2: 5261,   3: 5579,
         4: 6024,   5: 7045,   6: 7917,   7: 8397,
         8: 9447,   9: 11234, 10: 12596, 11: 14090,
        12: 16965, 13: 21316, 14: 25191, 15: 33252,
    }
    if dpcm_rate not in range(0, 16):
        final_rate = dpcm_rate
        print("Selected rate not compatible with NES DPCM")
    elif type == 0:
        final_rate = dpcm_rates_table_ntsc[dpcm_rate]
        print(f"Selected machine type: NTSC, DPCM Pitch: {dpcm_rate}, {dpcm_rates_table_ntsc[dpcm_rate]}hz")
    elif type == 1:
        final_rate = dpcm_rates_table_pal[dpcm_rate]
        print(f"Selected machine type: NTSC, DPCM Pitch: {dpcm_rate}, {dpcm_rates_table_pal[dpcm_rate]}hz")
    try:
        data = open(file, "rb").read()
    except FileNotFoundError:
        raise FileNotFoundError("not file 😔")
    if length in [None, False]:
        raise ValueError("Length must be non-zero")
    ptr = 0
    total_files = 0
    if len(data)/8 > 262144:
        print(r" /!\ This will likely not fit within 256kb of memory.")
        if dpcm_rate in range(0,16):
            size = len(data)
            temp_rate = dpcm_rate
            recommended_rate = dpcm_rate
            while size/8 > 262144:
                size = ceil(size * (dpcm_rates_table_ntsc[temp_rate - 1]/dpcm_rates_table_ntsc[temp_rate]))
                recommended_rate -= 1
                temp_rate -= 1
                print(f"deb: size {size} | "
                      f"rate {dpcm_rates_table_ntsc[temp_rate]} | "
                      f"rate-1 {dpcm_rates_table_ntsc[temp_rate-1] if (temp_rate-1) in dpcm_rates_table_ntsc else 0} | "
                      f"coefficient {(dpcm_rates_table_ntsc[temp_rate - 1]/dpcm_rates_table_ntsc[temp_rate]) if (temp_rate-1) in dpcm_rates_table_ntsc else 0} | "
                      f"< 262144 {size < 262144}")
                if temp_rate < 1:
                    print("No suitable rate has been found to fit this in under 256kb.")
                    break


            print(f"Recommended DPCM rate (assuming NTSC): {recommended_rate}, {dpcm_rates_table_ntsc[recommended_rate]}hz")
    for i in range(0, (len(data)//length) + 1):
        temp_data = data[ptr:ptr + length]
        save_riff(rate=final_rate, bdep=8,data=temp_data,location=f"{output_folder}/split_{i}.wav")
        ptr += length
        total_files += 1
    print(f"Total files: {total_files}")
    print(f"Recommended tick rate at Speed 60: {round((final_rate*0.0018555394641564084)*(32136/length), 2)}hz")

    # final_rate*0.0018555394641564084*1.9695872556118754

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
    """
    Writes a proper Furnace Tracker instrument, with samples if provided.
    """
    data = (f"FINS\xE6{chr(instype)}\x1C{chr(len(name) + 1)}\x00{name}\x00"  # main stuff
            f"MA\x0c\x00\x08\x00\x00\x01\xff\xff\x00\x00\x00\x01\x7f")    # macros: volume 127
    data = ["FINS", 0xE6, instype, "NA", len(name) + 1, name, 0x00,
            "MA", ]


def get_sample_data(raw, smtype="m"):
    """
    Returns contents of a 12-byte instrument header
    of MultiPCM-like chips, those being Sega MultiPCM itself (also known as Yamaha YMW258-F) and
    Yamaha OPL4, also known as Yamaha YMF278-F.
    Takes any data as input data and any text as mode.
    If first letter of mode matches 'm', return MultiPCM data, if matches 'o', return OPL4 data, return None otherwise.
    """
    return (
        (((raw[0x0000] & 0x3F) << 16 ) |                        #  0. start address
          (raw[0x0001] << 8) |
          (raw[0x0002])),

        ( (raw[0x0000] >> 6) & 0b11),                           #  1. data format (0: 8bit, 1: 12bit, 2: 16bit)

        ( (raw[0x0003] << 8) |                                  #  2. loop start
          (raw[0x0004]) + 1),

        (0x10000 - (
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


# for gods sake PLEASE DO NOT FUCKING USE IT
# IF YOU USE IT WI WILL MAKE SURE TO HAVE
# YOUR ARMS BROKEN. I WILL FIND YOU, I WILL
# COME TO YOUR HOUSE, I WILL PERSONALLY BREAK
# YOUR FUCKING ARMS.
def make_dpcm(data: bytes = b"") -> None:
    data = list(data)
    for i in range(len(data)):
        data[i] //= 2
    if len(data) % 8:
        for i in range(len(data) % 8):
            data.append((i % 2 is True))
    final = [ data[0] for _ in range(len(data)) ]
    final_dmc = [0 for _ in range(len(data)) ]
    current = data[0]
    for l in range(len(data)):
        if current < data[l]:
            current += 1
            final_dmc[l] = 1
        elif current > data[l]:
            current -= 1
            final_dmc[l] = 0
        else:
            if final[l - 1] == 0:
                current += 1
                final_dmc[l] = 1
            elif final[l - 1] == 127:
                current -= 1
                final_dmc[l] = 0
            if current < 0:
                current = 0
                final_dmc[l] = 0
            elif current > 127:
                current = 127
                final_dmc[l] = 0
        final[l] = current
    for i in range(len(final)):
        final[i] *= 2
    final_dmc_truly = [0 for _ in range(len(final_dmc)//8)]
    for i in range(len(final_dmc_truly)):
        bit = 0b11111111
        if final_dmc[(8*i)]:
            bit &= 0b11111111
        else:
            bit &= 0b01111111
        if final_dmc[(8*i) + 1]:
            bit &= 0b11111111
        else:
            bit &= 0b10111111
        if final_dmc[(8*i) + 2]:
            bit &= 0b11111111
        else:
            bit &= 0b11011111
        if final_dmc[(8*i) + 3]:
            bit &= 0b11111111
        else:
            bit &= 0b11101111
        if final_dmc[(8*i) + 4]:
            bit &= 0b11111111
        else:
            bit &= 0b11110111
        if final_dmc[(8*i) + 5]:
            bit &= 0b11111111
        else:
            bit &= 0b11111011
        if final_dmc[(8*i) + 6]:
            bit &= 0b11111111
        else:
            bit &= 0b11111101
        if final_dmc[(8*i) + 7]:
            bit &= 0b11111111
        else:
            bit &= 0b11111110

        final_dmc_truly[i] = bit
    save_riff(rate=33144, bdep=8, data=final, location="./output.wav")
    try:
        print("yay")
        open("./output.dmc", "wb").write(bytearray(final_dmc_truly))
    except FileNotFoundError:
        print("shit")
        open("./output.dmc", "xb").write(bytearray(final_dmc_truly))
    return None

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
    print(
        f"{generate_sine_table(256, char(127), 0)}\n"
        f"{generate_sine_table(256, schar(-1), 0)}\n"
        f"{generate_sine_table(256, ushort(65535), 0)}\n"
        f"{generate_sine_table(256, short(32767), 0)}\n"
    )