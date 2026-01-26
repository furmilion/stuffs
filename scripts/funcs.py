"""
A module with various useful functions used in other files.
Imports: random, os if needed, hashlib
"""

import random
from math import *
#from typing import Any

try:
    import argparse
except ModuleNotFoundError:
    pass
from hashlib import sha512, sha256, md5

try:  # numpy is a better option than standard python list stuff
    import numpy as np
    NUMPY = True
    # print("nupi")
except ImportError:
    print("NumPY not found.\n"
          "It is recommended to install NumPY as this offers slightly better performance.")
    NUMPY = False

def clamp(val: int = 0, mn: int = 0, mx: int = 9) -> int:
    """
    Clamps value to a range.
    :param val: the value
    :param mn: the lowest boundary
    :param mx: the highest boundary
    :return: clamped value
    """
    return max(mn, val) if val <= mn else min(val, mx) if val <= mx else mx

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


def ternary(condition, true, false):  # why doesn't python have this 😭
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
    delta = (l + u)/2
    if v < delta:
        return l
    else:
        return u

def check_bytes(in_file, val):
    """
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
def save_riff(#bdep=8, rate=32000, data="sample", loop_start=None, loop_end=None, location="./output.wav",
              **kwargs) -> None or int:  # I have no idea what that "-> tuple" means
    """
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
    """
    # We'll put everything in a nice big fat juicy try block to print out errors if there are any
    try:
        try:
            verbose = kwargs["verbose"]
            try: verbose = bool(verbose)
            except TypeError: verbose = False
        except KeyError: verbose = False

        try: bdep = kwargs["bdep"]
        except KeyError: bdep = 8
        try: rate = floor(kwargs["rate"])
        except KeyError: rate = 32000
        try: data = kwargs["data"]
        except KeyError:
            data = [random.randint(0, 255) for _ in range(256*(bdep//8))]
        try: loop_type = kwargs["loop_type"]
        except KeyError: loop_type = 0
        try: loop_start = kwargs["loop_start"]
        except KeyError: loop_start = (len(data) // (bdep//8))
        try: loop_end = kwargs["loop_end"] - 1
        except KeyError: loop_end = (len(data) // (bdep//8)) - 1
        try: location = kwargs["location"]
        except KeyError: location = "./output.wav"

        if type(loop_start)== int:
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

        rate &= 0xFFFFFF
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
        length_real = len(data) + 0x64
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
            data = np.array(data, np.uint8)
        else:
            raise ValueError(f"data has died. (type: {type(data)})")
        if NUMPY:
            data = np.array(data, np.uint8)
            header = np.array(important, np.uint8)
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

def split_file(file: str, output_folder: str, length=32136, dpcm_rate=15, type=0) -> None:
    """

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
        print(" /!\\ This will likely not fit within 256kb of memory.")
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


def convert_12_to_16(data: bytes = None) -> list[int]:
    if not data:
        return [0, 0]
    final = []
    for dt in range(len(data)//3):
        final.append(
            ((((data[dt * 3]) << 16 | (data[dt * 3 + 1]) | data[dt * 3 + 2]) >> 12) & 0xFFF) >> 8
        )
        final.append(
            ((((data[dt * 3]) << 16 | (data[dt * 3 + 1]) | data[dt * 3 + 2]) >> 12) & 0xFFF) & 0xFF
        )
        final.append(
            (((data[dt * 3]) << 16 | (data[dt * 3 + 1]) | data[dt * 3 + 2]) & 0xFFF) >> 8
        )
        final.append(
            (((data[dt * 3]) << 16 | (data[dt * 3 + 1]) | data[dt * 3 + 2]) & 0xFFF) & 0xFF
        )
    return final


class LFSR:

    """
    A simple class to create, tick and otherwise manage LFSRs.
    LFSR is short for Linear Feedback Shift Register.
    In LFSR world, there are taps.
    A tap (or tap bit) is a bit that will be operated on with a tap method.

    In this example we will use an LFSR of size 6 and initial state of 0b100010,
    taps 0, 2, 4 and 5 and tap method for all taps being XOR.

    XOR table:
    0 ^ 0 = 0
    1 ^ 0 = 1
    0 ^ 1 = 1
    1 ^ 1 = 0

    Note that the rightmost bit is always tapped.

    The LFSR works as follows:
    1. Get defined with size x (6), initial state y (0b100010), taps (0, 2, 4 and 5) and tap method (XOR).
    2. Tick:
    2.1. XOR last bit with first tap bit, aka bit 5 ^ bit 4. b5^b4 = 1, according to XOR table.
    2.2. XOR the result with next tap: 1^0 = 1
    2.3. XOR with the last tap: 1^1 = 0
    2.4. Right shift the state and insert the result bit at the first position.
    3. Repeat.

    """

    class ArgumentError(Exception):
        """
        An exception for use with argument errors.
        """
        def __init__(self, *args, **kwargs):
            """Initialize self."""
            pass

    class СатурнError(Exception):
        def __init__(self, *args, **kwargs):
            pass

    def raiseError(self, exception, message):
        raise exception(message)

    def _(self):
        return None

    def __init__(self):
        """
        Initializes self.
        """
        self.data = {}
        self.all_names = []
        self.last_calculation = 0
        self.temp_taps = [0]
        self.temp_taps2 = []
        self.len_mask = 0b1
        self.temp_state = 0
        self.name = None
        self.index = None
        self.lfsr_exists = False
        self.temp = 0
        self.temp2 = 0
        self.current_tap1, self.current_tap2 = None, None
        self.return_binary = False
        self.lfsr_types = [
                           "and",  "or",  "xor",
                           "nand", "nor", "xnor",
                           # "imply", "nimply"
                           ]

    def create(self, **kwargs):
        """
        Creates and contains a new LFSR with a name, initial state, size and tap bits.
        Raises a ValueError if either of parameters not passed.
        If an LFSR already exists, its parameters get overwritten (default dict behavior).
        Following values are accepted for taps: 'no','0', 'and', 'nand', 'or', 'xor', 'xnor'
        """
        kwargs["name"] if "name" in kwargs else self.raiseError(self.ArgumentError, "LFSR name not provided (provide via 'name' keyword).")
        temp_state = kwargs["state"] if "state" in kwargs else self.raiseError(self.ArgumentError, "LFSR initial state not provided (provide via 'state' keyword).")
        temp = kwargs["size"] if "size" in kwargs else self.raiseError(self.ArgumentError, "LFSR size not provided (provide via 'size' keyword).")
        temp_taps = kwargs["taps"] if "taps" in kwargs else self.raiseError(self.ArgumentError, "LFSR taps not provided (provide via 'taps' keyword).")
        len_mask = 0b1
        for i in range(kwargs["size"]):
            len_mask |= 2**i
        if type(temp_state) is int:
            temp_state &= len_mask
        elif temp_state == "max":
            temp_state = len_mask
        else:
            raise ValueError("'state' keyword only accepts integers or 'max' as a value.")
        if type(kwargs["taps"]) is not list:
            temp_taps = list(kwargs["taps"])
        temp_taps2 = list(range(kwargs["size"] - len(temp_taps)))
        for i in range(len(temp_taps2)):
            temp_taps2[i] = 0
        temp_taps2.append(temp_taps)
        for i in range(len(self.data)):
            if kwargs["name"] in self.data[i]:
                self.lfsr_exists = True
                self.data[len(self.data)] = {"name": kwargs["name"], "state": self.temp_state,
                                                      "taps": self.temp_taps2, "size": kwargs["size"]}
                for j in range(len(self.data)):
                    if self.data[j]["name"] not in self.all_names:
                        self.all_names.append(self.data[j]["name"])
                return (f"Successfully modified an LFSR at position {len(self.data) - 1}:\n"
                        f"{self.data[f'lfsr{len(self.data) - 1}']}")
            else:
                self.lfsr_exists = False
        if not self.lfsr_exists:
            self.data[len(self.data)] = {"name": kwargs["name"], "state": self.temp_state,
                                         "taps": self.temp_taps, "size": kwargs["size"]}
            for j in range(len(self.data)):
                if self.data[j]["name"] not in self.all_names:
                    self.all_names.append(self.data[j]["name"])
            return (f"Successfully created an LFSR at position {len(self.data) - 1}:\n"
                    f"{self.data[len(self.data) - 1]}")

    def list_all(self):
        """
        Lists names of all currently created LFSRs.
        """
        for i in range(len(self.data)):
            try:
                if self.data[i]["name"] not in self.all_names:
                    self.all_names.append(self.data[i]["name"])
            except KeyError:
                pass
        return self.all_names

    def return_state(self, **kwargs):
        """
        Returns the current state of an LFSR.
        Raises a ValueError if name or index not passed or an LFSR with that name or at that index does not exist.
        Returns binary view if 'return_binary' keyword set.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        self.name = kwargs["name"] if "name" in kwargs else None
        self.index = kwargs["index"] if "index" in kwargs else None
        self.return_binary = kwargs["return_binary"] if "return_binary" in kwargs else 0
        if self.name is None and self.index is None:
            raise self.ArgumentError("Name of LFSR not passed as an argument.")
        try:
            if self.return_binary:
                return bin(self.data[self.all_names.index(self.name)]["state"])
            else:
                return self.data[self.all_names.index(self.name)]["state"]
        except ValueError:
            raise ValueError(f"LFSR with name {self.name} does not exist."
                             f"Use list_all() method to get a list of all names.")

    def flush(self):
        """
        Flushes: returns a dict of all LFSRs and their states and clears it.
        """
        print(self.data)
        self.data = {}
        self.all_names = []

    def get_all(self):
        """
        Returns the dict containing all LFSRs.
        """
        return self.data

    def pop(self, **kwargs):
        """
        Remove and return LFSR at index or at name.
        Raises an IndexError if no LFSRs are present.
        Raises a ValueError if neither of arguments is passed.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        index = kwargs["index"] if "index" in kwargs else None
        name = kwargs["name"] if "name" in kwargs else None
        if (index is None) and (name is None):
            raise self.ArgumentError("Name nor index of LFSR not passed as an argument.")
        elif name is not None and index is not None or name is not None:
            try:
                if self.all_names.index(name) == (len(self.all_names) - 1):
                    temp = self.data[self.all_names.index(name)]
                    self.data.pop(self.all_names.index(name))
                    self.all_names.pop(self.all_names.index(name))
                    return temp
                else:
                    temp = self.data[self.all_names.index(name)]
                    for i in range(self.all_names.index(name), len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(self.all_names.index(name))
                    return temp
            except KeyError:
                raise KeyError(f"LFSR with name {name} does not exist."
                               f"Use list_all() method to get a list of all names.")
        elif name is None and index is not None:
            try:
                if index == (len(self.all_names) - 1):
                    temp = self.data[index]
                    self.all_names.pop(self.data[index]["name"])
                    self.data.pop(index)
                    return temp
                else:
                    temp = self.data[index]
                    for i in range(index, len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(index)
                    return temp
            except KeyError:
                raise IndexError(f"LFSR at index {index} does not exist."
                                 f"Use list_all() method to get a list of all names.")

    def remove(self, **kwargs):
        """
        Remove an LFSR at index or at name.
        Raises an IndexError if no LFSRs are present.
        Raises a ValueError if neither of arguments is passed.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        index = kwargs["index"] if "index" in kwargs else None
        name = kwargs["name"]  if "name" in kwargs else None
        if (index is None) and (name is None):
            raise self.ArgumentError("Name nor index of LFSR not passed as an argument.")
        elif name is not None and index is not None or name is not None:
            try:
                if self.all_names.index(name) == (len(self.all_names) - 1):
                    self.data.pop(self.all_names.index(name))
                    self.all_names.pop(self.all_names.index(name))
                    return
                else:
                    for i in range(self.all_names.index(name), len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(self.all_names.index(name))
                    return
            except KeyError:
                raise KeyError(f"LFSR with name {name} does not exist."
                               f"Use list_all() method to get a list of all names.")
        elif name is None and index is not None:
            try:
                if index == (len(self.all_names) - 1):
                    self.all_names.pop(self.data[index]["name"])
                    self.data.pop(index)
                    return
                else:
                    for i in range(index, len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(index)
                    return
            except KeyError:
                raise IndexError(f"LFSR at index {index} does not exist."
                                 f"Use list_all() method to get a list of all names.")

    def tick(self, **kwargs):
        """
        Advances the LFSR at name or index by a single tick and returns the bit that got thrown out when right-shifting.
        Raises a ValueError if neither of arguments is passed.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        index = kwargs["index"] if "index" in kwargs else None
        name = kwargs["name"] if "name" in kwargs else None
        current_tap1, current_tap2, *_, = [None for _ in range(16)]
        if index is None and name is None:
            raise self.ArgumentError("Name nor index of LFSR not passed as an argument.")

        if name is not None and (index is not None) or name is not None:
            if name in self.data:
                temp = self.data[self.all_names.index(name)]["state"]
                temp2 = self.data[self.all_names.index(name)]["size"]
                temp_taps = self.data[self.all_names.index(name)]["taps"]

                for i in range(len(temp_taps), 0):
                    try:
                        calculated = False
                        if temp_taps[i] not in self.lfsr_types:
                            pass
                        else:
                            if current_tap1 is None:
                                current_tap1 = temp_taps[i]
                            elif current_tap2 is None:
                                current_tap2 = temp_taps[i]
                            elif "h":
                                pass


                    except:  # i'll probably finish everything later
                        ""
            else:
                raise KeyError(f"LFSR with name {name} does not exist."
                               f"Use list_all() method to get a list of all names.")

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

if __name__ == "__main__":

    a_n5 = opll_get_freq(0x09, 0x10)
    a_n4 = opll_get_freq(0x12, 0x10)
    a_n3 = opll_get_freq(0x24, 0x10)
    a_n2 = opll_get_freq(0x49, 0x10)
    a_n1 = opll_get_freq(0x91, 0x10)
    a_0  = opll_get_freq(0x22, 0x11)
    a_1  = opll_get_freq(0x22, 0x13)
    a_2  = opll_get_freq(0x22, 0x15)
    a_3  = opll_get_freq(0x22, 0x17)
    a_4  = opll_get_freq(0x22, 0x19)
    a_5  = opll_get_freq(0x22, 0x1b)
    a_6  = opll_get_freq(0x22, 0x1d)
    a_7  = opll_get_freq(0x22, 0x1f)
    a_8  = opll_get_freq(0xff, 0x1f)
    print(f'{a_n5}\n{a_n4}\n'
          f'{a_n3}\n{a_n2}\n'
          f'{a_n1}\n{a_0}\n'
          f'{a_1}\n{a_2}\n'
          f'{a_3}\n{a_4}\n'
          f'{a_5}\n{a_6}\n'
          f'{a_7}\n{a_8}\n')