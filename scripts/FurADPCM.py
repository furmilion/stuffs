from math import log, ceil
import funcs
import time

try:
    import numpy
except ImportError:
    print("shart")


def lim(mv, inlist: list[int] = None) -> list[int]:
    if type(inlist) in [int, float]:
        inlist = [inlist]
    elif type(inlist) in [list, tuple]:
        inlist = list(inlist)
    else:
        raise TypeError("Input data must be of types [int, float, list, tuple].")
    for i in range(len(inlist)):
        if inlist[i] > mv:
            inlist[i] = mv
    return inlist


def pack_byte(bits=None) -> int:
    """Pack 8 bits into a byte. Excess input will be discarded."""
    output = 0
    if bits is None or 0:
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


def pack_int16(ints=None, endianness: str = "big") -> int:
    """Pack 2 int8's into a 16-bit int."""
    if ints is None or ints == []:
        raise ValueError("A list of 2 ints is not supplied.")
    if type(ints) in [int, float]:
        ints = [int(ints)]
    if len(ints) == 1:
        ints.append(int())
    if endianness.lower() in ["backwards", "back", "b", "lsb", "little"]:
        return ((ints[1] & 255) << 8) + (ints[0] & 255)  # return backwards imploded word
    else:
        return ((ints[0] & 255) << 8) + (ints[1] & 255)  # return normal imploded word


def explode_int16(_int: int = 65535, endianness: str = "big") -> list[int]:
    """Explodes an int16 into a list of 2 int8's"""
    if endianness.lower() in ["backwards", "back", "b", "lsb", "little"]:
        return [_int & 255, (_int >> 8) & 255]  # return backwards exploded bytes
    else:
        return [(_int >> 8) & 255, _int & 255]  # return normal exploded bytes


class FurADPCM:
    """
    File format: .fa
    File magic: "FurADPCM"
    File structure:
         size | block
        ------+----------------------
            8 | FurADPCM File Magic
            2 | Sample rate / 2
            1 | Metadata
            1 | Fx Block Info Start
           ---+----------------------
            2 | Block Info Data
            4 | Flags
           ---+----------------------
            1 | F1 Block Info End
            ? | data

    METADATA:
        bit 0: is 16-bit
        bit 1: channels (bit0)
        bit 2: channels (bit1)
        bit 3: channels (bit2)
        bit 4: channels (bit3)
        bit 5: reserved
        bit 6: reserved
        bit 7: reserved


    Block format 1:
        byte 1:
            F0 (block info start)
        byte 2:
            block size MSByte
        byte 3:
            block size LSByte
        byte 4:
            initial value MSByte
        byte 5:
            initial value LSByte
        byte 6:
            reserved
        byte 7:
            reserved
        byte 8:
            F1 (block info end)

    8-bit step table:  [  0x80,   0x40,   0x20,  0x10,  0x08,  0x04,  0x02, 0x01]
    16-bit step table: [0x4000, 0x2000, 0x1000, 0x800, 0x400, 0x200, 0x100, 0x80]

    A single byte of data in Block Format 1 contains 2 samples.
    Each sample has 1 bit of sign (direction of where it goes since the last value, up or down),
    and 3 bits for selecting how much to step from last value. The samples are stored in big-endian order,
    as in sample 1 comes first and sample 2 comes second.
    If there is not enough samples to form a full byte, then lower nibble is 0.

    Initial value is sample value at which decoding starts


    Block format 2:
        byte 1:
            F2 (block info start)
        byte 2:
            bit 1: 3-bit power value, bit 1
            bit 2: 3-bit power value, bit 2
            bit 3: 3-bit power value, bit 3
            bit 4: block size, bit 1.
            bit 5: block size, bit 2.
            bit 6: block size, bit 3.
            bit 7: block size, bit 4.
            bit 8: block size, bit 5.
        byte 3:
            bit 1: block size, bit 6.
            bit 2: block size, bit 7.
            bit 3: block size, bit 8.
            bit 4: block size, bit 9.
            bit 5: block size, bit 10.
            bit 6: block size, bit 11.
            bit 7: block size, bit 12.
            bit 8: block size, bit 13.
        byte 4:
            initial value MSByte
        byte 5:
            initial value LSByte
        byte 6:
            reserved, any value
        byte 7:
            reserved, any value
        byte 8:
            F1 (block info end)

        Each byte in Block Format 2 contains 8 samples.
        Base step is 2. This is then raised to the power of Power value.
        If the metadata in file tells that this file is 16-bit, then the
        step value is additionally right-shifted 9 times. After this,
        1 is subtracted from the final step value.
        Each sample in a byte has 2 states: go up by step size from previous sample, or go down.
        If there are not enough samples to fully fill a byte, then other bits are padded in a checkerboard manner.

        Initial value is sample value at which decoding starts


    Block format 3:
        byte 1:
            F3 (block info start)
        byte 2:
            bit 1: step change function
            bit 2: step change function
            bit 3: step change function [lin4, lin16, pow2, pow3]
            bit 4:  block size, bit 1
            bit 5:  block size, bit 2
            bit 6:  block size, bit 3
            bit 7:  block size, bit 4
            bit 8:  block size, bit 5
        byte 3:
            bit 1:  block size, bit 6
            bit 2:  block size, bit 7
            bit 3:  block size, bit 8
            bit 4:  block size, bit 9
            bit 5:  block size, bit 10
            bit 6:  block size, bit 11
            bit 7:  block size, bit 12
            bit 8:  block size, bit 13
        byte 4:
            initial value MSByte
        byte 5:
            initial value LSByte
        byte 6:
            reserved
        byte 7:
            reserved
        byte 8:
            F1 (block info end)

        Step functions:
            function | initial step size | step increase per iteration
            LIN4     | 0                 | 4
            LIN16    | 0                 | 16
            LIN256   | 0                 | 256
            LIN2048  | 0                 | 2048
            POW2     | 2                 | iteration**2
            POW3     | 2                 | iteration**3
        NOTE: when 16-bit, LIN4 is swapped for LIN256 and LIN16 is swapped out for LIN2048

        Each byte in Block Format 3 contains 8 samples.
        Each sample only has 2 states: go up from current value and increase step, or go down and increase step.
        If there are not enough samples to fully fill a byte, then other bits are padded in a checkerboard manner.

        Initial value is sample value at which decoding starts
    """

    def __init__(self):
        self.magic = b"FurADPCM"  # bytestring of the file magic
        self.extension = ".fa"  # file extension

        # TODO: remove this if i actually find this useless
        self.blocks = 0  # amount of blocks in file; will remain unused?

        self.step_table_f1_8b =  [  0x80,   0x40,   0x20,  0x10,  0x08,  0x04,  0x02, 0x01]  # step table for use with F0 block, 8-bit variant
        self.step_table_f1_16b = [0x4000, 0x2000, 0x1000, 0x800, 0x400, 0x200, 0x100, 0x80]  # step table for use with F0 block, 16-bit variant
        self.step_table_f2 = [0x0F, 0x07, 0x03, 0x01]  # step table for use with F2 block
        self.step_types = ["lin4", "lin16", "pow2", "pow3"]  # step increase functions for use with F3 block
        self.max_step_size = 1024

        self.little_endian = ["l", "lsb", "little"]
        self.big_endian = ["b", "msb", "big"]
        self.endianness = ["b", "msb", "big", "l", "lsb", "little"]

        # decoder
        self.data_begin = 8  # offset of data beginning in a data block
        ...

    # TODO: implement block format 1
    def encode_block_f1(self, encdata=None, block_size=0) -> list[int]:
        return [0]

    # TODO: implement block format 2
    def encode_block_f2(self, encdata: list[int] = None, blocksize=16) -> list[int]:
        return [0]

    def encode_block_f3(self,
                        encdata: list[int] = None,
                        block_size: int = 16,
                        step_type: str = None,
                        correction: int = None,
                        is_int16: bool = False,
                        **encoder_options) -> list[int]:
        """
        Encodes a format 3 block.
        :param encdata: Data to encode.
        :param block_size: Block size to encode with.
        :param step_type: Which step increase function to use.
        :param correction: Offset
        :param is_int16: Pass True if 16-bit space. Leave blank otherwise.
        :param encoder_options: Extra encoder options.
        Available options:
        - extra_info: print out extra info during encoding process
        :return: Returns a list[int] containing the block and encoded data
        """

        if step_type is None:
            step_type = "lin4"
        extra_info = encoder_options["extra_info"] if "extra_info" in encoder_options else False

        if encdata is None:
            raise ValueError("Do not leave data empty.")
        if type(encdata) not in [int, float, list, tuple]:
            raise TypeError("Data must be of following types: [int, float, list, tuple].")

        encdata = lim(255, list(encdata))  # Convert data to list if it's a tuple or other format

        # 16-bit space shenanigans
        max_val = 255
        if is_int16:  # if we *are* 16-bit...
            new_encdata = []  # define a new temp array
            for i in range(ceil(len(encdata) / 2)):  # for half of the encdata length...
                new_encdata.append(pack_int16(encdata[i * 2:i * 2 + 2]))  # pack and append a 16-bit int from encdata
            encdata = new_encdata  # to new_encdata and then set encdata to
            del new_encdata  # new_encdata and wipe new_encdata
            max_val = 65535  # from existence. and also update max_val

        if step_type.lower() not in self.step_types:
            raise ValueError(f"Bad step type: {step_type}. Available step types: {self.step_types}.")

        if block_size > 4096:
            raise ValueError(f"Illegal block size: {block_size}. The value must be less than or equal to 4096.")

        if ceil(
                len(encdata) // 16 if is_int16 else 8
        ) > block_size:
            raise ValueError(f"Length of data to be encoded is larger than the block size.")

        if len(encdata) < block_size * 8:
            print(f"Warning, supplied only {len(encdata)} samples of data with block size "
                  f"{block_size}. Shrinking block to {ceil(len(encdata) / 8)}.")
            block_size = ceil(len(encdata) / 8)
            for i in range(block_size * 8 - len(encdata)):
                encdata.append(encdata[-1])

        if correction is not None:
            current_value = correction
        else:
            correction = encdata[0]
            current_value = encdata[0]

        # TODO: refine the block format
        data_block_full: list[int] = \
            [
                0xF3,                                               # Block begin
                ((self.step_types.index(step_type) & 0b11) << 6) +  # Step type + 6 lower bits of block len
                (((block_size - 1) >> 8) & 0b111111),               # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                (block_size - 1) & 0b11111111,                      # Lower 8 bits of block size
                is_int16 << 7,                                      # block in 16-bit space?
                0,                                                  # reserved
                (correction >> 8) & 255, correction & 255,          # Correction
                0xF0  # Block end
            ]

        current_step = 0 if step_type.lower().__contains__("lin") else 2
        is_negative_step = False
        pow_step = 1
        ed = []
        if extra_info:
            print(f"Block:\n"
                  f"{data_block_full}")
        for step in range(len(encdata)):
            # Limit the step so that it does not explode my (or your) memory
            # Python ints don't have width which is both in- and very convenient
            # Inconvenient because if you decide to indefinitely raise to the power of a number,
            # you end up expanding your int more and more, so it ends up eating your gigabytes
            # Convenient for the same reason LMAO
            # TODO: increase max step size for int16 use case?
            if current_step > self.max_step_size or pow_step > self.max_step_size:
                current_step = lim(self.max_step_size, [current_step])[0]
                pow_step = lim(self.max_step_size, [pow_step])[0]

            # this is how I found out that current_step was stealing my memory
            # thank the debugging gods debugging is a thing
            if extra_info:
                print(f"Length:        {len(encdata)}\n"
                      f"Step:          {step + 1}/{len(encdata)}\n"
                      f"Raw value:     {encdata[step]}\n"
                      f"Current value: {current_value}\n"
                      f"Current step:  {current_step}")
            # Very epic checks for value of raw data vs current value
            if encdata[step] <= current_value:
                if (not is_negative_step) and step_type.lower().__contains__("lin"):
                    current_step = 0
                elif (not is_negative_step) and step_type.lower().__contains__("pow"):
                    current_step = 2
                    pow_step = 1
                is_negative_step = True
                current_value -= current_step
                ed.append(0)
            elif encdata[step] > current_value:
                if is_negative_step and step_type.lower().__contains__("lin"):
                    current_step = 0
                elif is_negative_step and step_type.lower().__contains__("pow"):
                    current_step = 2
                    pow_step = 1
                is_negative_step = False
                current_value += current_step
                ed.append(1)

            # Attempt at cleaning up the code
            current_step = current_step + 4 if step_type == "lin4" else \
                current_step + 16 if step_type == "lin16" else \
                    2 ** pow_step if step_type == "pow2" else \
                        3 ** pow_step if step_type == "pow3" else \
                            "buggy code broke down"
            if current_step == "buggy code broke down":
                raise ValueError("buggy code broke down")

            # Limit values to 8-bit space
            # Might expand to 16-bit later. <- discard that, arbitrary bit depth now.

            # TODO: what the actual fuck
            current_value = 0 if current_value < 0 else max_val if current_value > max_val else current_value
            # if current_value == "buggy code broke down":
            #     raise ValueError("buggy code broke down")

            # Increase pow_step
            pow_step += 1

        # print(len(encoded_data))
        # print(len(encoded_data)//8)

        # pack bytes into the final data block
        for i in range(ceil(len(ed) // 8)):
            data_block_full.append(pack_byte(ed[i * 8:(i * 8) + 8]))
        return data_block_full

    def decode_block(self, block=None, **decoder_options) -> list[int]:
        """
        Decodes an input data block.

        Available decoder options:
            - byte_order: byte order of exploded int16. default "msb"
        :param block: The input data block.
        :param decoder_options: Block decoder options
        :return:
        """
        if block is None or len(block) < self.data_begin:
            raise ValueError("Nothing to decode")
        if block[self.data_begin - 1] != 0xF0:
            raise ValueError("Not a proper block")
        decoded_data = []
        to_decode = block[self.data_begin:]

        try:
            extra_info = decoder_options["extra_info"]
        except KeyError:
            extra_info = False
        try:
            byte_order = decoder_options["byte_order"]
        except KeyError:
            byte_order = "msb"

        # TODO: implement block format 1
        if block[0] == 0xF1:
            ...
            return [0]
        # TODO: implement block format 2
        elif block[0] == 0xF2:
            ...
            return [0]

        elif block[0] == 0xF3:
            step_type = self.step_types[block[1] >> 6]
            block_length = (((block[1] & 0b00111111) << 8) + block[2]) + 1
            is_int16 = bool((block[3] >> 7) & 1)
            correction = (block[5] << 8) + block[6]
            # print(is_int16)
            current_value = correction

            # prepare int16 workspace
            max_val = 255
            if is_int16:
                max_val = 65535

            if step_type.lower().__contains__("lin"):
                current_step = 0
            else:
                current_step = 2
            is_negative_step = False
            pow_step = 1
            for i in range(block_length):
                bytes_ = explode_byte(to_decode[i])
                for step in range(8):
                    if current_step > self.max_step_size or pow_step > self.max_step_size:
                        current_step = lim(self.max_step_size, [current_step])[0]
                        pow_step = lim(self.max_step_size, [pow_step])[0]
                    if extra_info:
                        print(
                            f"Block correction: {correction};\n"
                            f"Step: {step};\n"
                            f"Step size: {current_step};\n"
                            f"Current value: {current_value};\n")
                    if bytes_[step] == 0:
                        if (not is_negative_step) and step_type in self.step_types[:2]:
                            current_step = 0
                        elif (not is_negative_step) and step_type in self.step_types[2:]:
                            current_step = 2
                            pow_step = 1
                        is_negative_step = True
                        current_value -= current_step
                    elif bytes_[step] == 1:
                        if is_negative_step and step_type in self.step_types[:2]:
                            current_step = 0
                        elif is_negative_step and step_type in self.step_types[2:]:
                            current_step = 2
                            pow_step = 1
                        is_negative_step = False
                        current_value += current_step

                    # I DID POST-LIMITING NOT PRE-LIMITING man im stupid 😭
                    # Limit values to space
                    if current_value < 0:
                        current_value = 0
                    elif current_value > max_val:
                        current_value = max_val
                    decoded_data.append(current_value)

                    # if step_type == "lin4":
                    current_step = current_step + 4 if step_type == "lin4" else \
                        current_step + 16 if step_type == "lin16" else \
                            2 ** pow_step if step_type == "pow2" else \
                                3 ** pow_step if step_type == "pow3" else \
                                    "buggy code broke down"
                    if current_step == "buggy code broke down":
                        raise ValueError("buggy code broke down")
                    # Increase pow_step
                    pow_step += 1

            if is_int16:
                new_decoded_data = []
                for i in range(len(decoded_data)):
                    new_decoded_data.extend(explode_int16(decoded_data[i], byte_order))
                decoded_data = new_decoded_data
                del new_decoded_data
                # print(is_int16)
            return decoded_data

    def encode_file(self, file, block_format, **encoder_options) -> int | list[int]:
        """
        Encodes a file with one of the block formats.

        Available encoder options:
            - step_type: for use with format 3 block
            - sample_rate: sample rate to encode with. Integer/Floor divided by 2.
            - location: the file location (without the extension) to save the file at.
            - is_stereo: self-explanatory. Joint stereo.
            - is_int16: whether to work in 16-bit space.
            - byte_order: byte order for decoder. "msb" default.
            - convert_sign: whether to exchange data signage.
            - return_data: whether to return a list of values instead of saving to a file.
            - output_progress: output progress on how many blocks have been encoded so far.
            - output_progress_extra: encoder outputs all the information (slows down the process).
        :param file: The file to encode
        :param block_format: The block format to use
        :param encoder_options: Misc options like sample rate and step type for F3 block.
        :return:
        Returns 1 upon success, returns 0 upon any failure.
        """
        final = []
        step_type = encoder_options["step_type"] if "step_type" in encoder_options else None
        sample_rate = encoder_options["sample_rate"] // 2 if "sample_rate" in encoder_options else 22050
        location = encoder_options["location"] + self.extension \
            if "location" in encoder_options else "./file" + self.extension
        is_stereo = encoder_options["is_stereo"] if "is_stereo" in encoder_options else False
        is_int16 = encoder_options["is_int16"] if "is_int16" in encoder_options else False
        byte_order = encoder_options["byte_order"] if "byte_order" in encoder_options else "msb"
        convert_sign = encoder_options["convert_sign"] if "convert_sign" in encoder_options else False
        return_data = encoder_options["return_data"] if "return_data" in encoder_options else False
        if return_data not in [True, False, 1, 0, 1.0, 0.0]:
            raise ValueError("So do you want to get the list of data or a file?")
        if return_data:
            location = None

        output_progress = encoder_options["output_progress"] if "output_progress" in encoder_options else False
        output_progress_extra = encoder_options["output_progress_extra"] if \
            "output_progress_extra" in encoder_options else False

        if byte_order not in self.endianness:
            raise ValueError("none endian")

        final.extend(list(self.magic))
        final.extend([(sample_rate >> 8) & 255, sample_rate & 255])
        # print([(sample_rate >> 8) & 255, sample_rate & 255])
        if type(file) is str:
            data = list(open(file, "rb").read())
        elif type(file) in [list, tuple]:
            data = list(file)
        else:
            raise TypeError("WHAT ARE YOU DOING")

        if convert_sign:
            if is_int16:
                # slightly less simple.
                if byte_order in self.big_endian:  # small byte first
                    for i in range(ceil(len(data) / 2)):
                        data[i] = (data[i * 2] + 128) & 255
                elif byte_order in self.little_endian:  # big byte first
                    for i in range(ceil(len(data) / 2)):
                        data[i] = (data[(i * 2) - 1] + 128) & 255
                else:
                    raise ValueError("none endian")
            else:
                ...
        else:
            # as simple as it gets.
            for i in range(len(data)):
                data[i] = (data[i] + 128) & 255
        final.append(((int(is_int16) << 7) + (int(is_stereo) << 6) + (
                    (1 if byte_order.lower() in self.little_endian else 0) << 5)))
        if output_progress:
            print(f'Encoding with endianness: {"Little" if byte_order.lower() in self.little_endian else "Big"}')
            print(f"Options:\n"
                  f"Output progress: {output_progress}\n"
                  f"Output extra: {output_progress_extra}\n"
                  f"Convert sign: {convert_sign}\n"
                  f"Working with 16 bits: {is_int16}\n"
                  f"Working with stereo: {is_stereo}\n"
                  f"Step type (block format 3): {step_type}\n"
                  f"Sample rate: {sample_rate * 2}\n"
                  f"Output file location: {location}")
        if is_int16:
            samples = 65536
            data_length = ceil(len(data) / 2)
        else:
            samples = 32768
            data_length = len(data)

        if block_format == 1:
            ...
        elif block_format == 2:
            ...
        elif block_format == 3:
            # print(len(data))
            if data_length <= 4096 * 8:
                final.extend(
                    self.encode_block_f3(
                        data,
                        ceil(data_length / 8),
                        step_type,
                        None,
                        is_int16,
                        extra_info=output_progress_extra
                    )
                )
            else:
                for call in range(ceil(data_length / (4096 * 8))):
                    final.extend(
                        self.encode_block_f3(
                            data[samples * call:(samples * call) + samples],
                            4096,
                            step_type,
                            None,
                            is_int16,
                            extra_info=output_progress_extra
                        )
                    )
                    if output_progress:
                        print(f"{call + 1}/"
                              f"{ceil(data_length / (4096 * 8))} "
                              f"blocks done")
                # print("unhandled yet")
                # return 0
        # here we get to write the file
        # print(self.final)
        if not return_data:
            try:
                # if file does not exist, we create a new one.
                open(location, "xb").write(bytearray(final))
            except FileExistsError:
                open(location, "wb").write(bytearray(final))
            return 1
        elif return_data:
            return list(final)

    def get_block_size(self, block) -> int:
        """
        Gets the size of both block and the block data.
        :param block:
        :return:
        """
        return ((block[1] & 0b111111) << 8) + block[2] + 8 + 1
        # the +1 here is from block always being at least 1 byte wide

    def decode_file(self, file=None, **decoder_options) -> tuple[list[int], int] | None:
        """
        Decodes a FurADPCM file or a list of raw values.
                Currently available options:
            - byte_order: force byte order when exploding an int16 to [int8, int8]. either "MSB" or "LSB". None default.
            - output_progress: output progress on how many blocks have been decoded so far
            - extra_info: output detailed info when decoding. slows down the process.
            - convert_sign: whether to convert sign.
            - return_data: whether to return a list of values instead of saving to a file.
            - location: where to save the resulting file.
        :param file: Input file
        :param decoder_options: Decoder options.
        :return:
        Returns a tuple containing a list of decompressed samples and a sample rate.
        """

        output_progress = decoder_options["output_progress"] if "output_progress" in decoder_options else False
        extra_info = decoder_options["extra_info"] if "extra_info" in decoder_options else False
        extra_extra_info = decoder_options["extra_extra_info"] if "extra_extra_info" in decoder_options else False
        byte_order = decoder_options["byte_order"] if "byte_order" in decoder_options else "msb"
        convert_sign = decoder_options["convert_sign"] if "convert_sign" in decoder_options else False
        return_data = decoder_options["return_data"] if "return_data" in decoder_options else False
        location = decoder_options["location"] if "location" in decoder_options else './decoded.wav'

        if byte_order not in self.endianness:
            raise ValueError("none endian")

        if not file or file == "":
            raise ValueError("No file to decode.")
        if type(file) is str:
            try:
                data = list(open(file, "rb").read())
            except FileNotFoundError as e:  # lmao re-raising an exception after catching it
                raise FileNotFoundError(e)  # TODO: not do this
        elif type(file) in [list, tuple]:
            data = list(file)
        else:
            raise TypeError("You must provide either a path to a file or a list of raw values.")

        if bytes(data[:8]) != self.magic:
            raise ValueError("Not a FurADPCM file.")

        sample_rate = ((data[8] << 8) + data[9]) * 2
        metadata = {
            "is_int16": (data[10] >> 7) & 1,
            "is_stereo": (data[10] >> 6) & 1,
            "endianness": (data[10] >> 5) & 1,
        }

        if extra_info:
            print(f"File endianness: {funcs.ternary(metadata['endianness'], 'Little', 'Big')}")

        to_decode = data[11:]
        # print(sample_rate)
        # print(to_decode)
        pointer = 0
        final = []
        # is_first_block = True
        # print(bytes(data))
        # print(bytes(to_decode))
        blocks_decoded = 0
        while pointer < len(to_decode) - 1:
            # print(pointer, len(to_decode), len(to_decode[pointer:]))
            final.extend(
                self.decode_block(to_decode[pointer:],
                                  extra_info=extra_extra_info,
                                  byte_order=(
                                      ("lsb" if metadata["endianness"] else "msb")
                                      if byte_order is None else byte_order
                                  )
                                  )
            )
            pointer += self.get_block_size(to_decode[pointer:])
            blocks_decoded += 1
            if output_progress:
                print(f"Blocks decoded: {blocks_decoded}")
        if not convert_sign and metadata["is_int16"]:
            # slightly less simple.
            if byte_order in self.little_endian:  # small byte first
                for i in range(ceil(len(final) / 2)):
                    final[i] = (final[i * 2] + 128) & 255
            elif byte_order in self.big_endian:  # big byte first
                for i in range(ceil(len(final) / 2)):
                    final[i] = (final[(i * 2) - 1] + 128) & 255
            else:
                raise ValueError("none endian")
        elif convert_sign and metadata["is_int16"]:
            ...
        if return_data:
            return final, sample_rate
        else:
            try:
                funcs.save_riff(
                    data=final,
                    sample_rate=sample_rate,
                    location=location,
                    bdep=(8 if not metadata['is_int16'] else 16),
                )
            except funcs.SaveError:
                return final, sample_rate


encoder = FurADPCM()

# encoded_data = encoder.encode_block_f3(list(range(256)), 32, "pow3", 0)
# decoded_data = encoder.decode_block(encoded_data, 0)
# funcs.save_riff(data=(decoded_data),
#                 location="./test_curve_pow3.wav", rate=32000, verbose=False)

#==============================================================================
# TODO: 16-bit tests
# test_list = []
# test_list.extend(list(range(0, 65536, 16)))
# temp_rev = []
# temp_rev.extend(test_list)
# temp_rev.reverse()
# test_list.extend(temp_rev)
# del temp_rev
# print(len(test_list))
# test_list2 = []
# for i in range(len(test_list)):
#     test_list2.extend(explode_int16(test_list[i]))
# test_list = test_list2
# del test_list2
# test_block16 = encoder.encode_file(test_list,
#                                    3,
#                                    is_int16=True,
#                                    step_type="pow2",
#                                    convert_sign=True,
#                                    byte_order="lsb",
#                                    output_progress=True,
#                                    sample_rate=33488,
#                                    return_data=True,
#                                    )
# test_block16_decoded = encoder.decode_file(test_block16,
#                                            extra_info=False,
#                                            convert_sign=False)
# # print(test_block16_decoded)
# test_block16_decoded_packed = []
# for i in range(ceil(len(test_block16_decoded[0]) / 2)):
#     test_block16_decoded_packed.append(pack_int16(test_block16_decoded[0][i * 2:i * 2 + 2]))
# # print(test_block16_decoded_packed)
# funcs.save_riff(data=test_block16_decoded[0],
#                 location="./furadpcm tests/16bit_test.wav",
#                 rate=test_block16_decoded[1],
#                 bdep=16)
#==============================================================================
#

# encoder.encode_file("./furadpcm tests/011_Mice_on_Venus_LEFT.raw",
#                     3,
#                     step_type="pow2",
#                     location="./furadpcm tests/011_Mice_on_Venus_LEFT",
#                     is_int16=True,
#                     output_progress=True,
#                     byte_order="lsb",
#                     convert_sign=False
#                     )
# test = \
#     encoder.decode_file(
#         "./furadpcm tests/011_Mice_on_Venus_LEFT.fa",
#         output_progress=True,
#         extra_info=True,
#         extra_extra_info=False,
#         # byteorder="backwards"
#     )
# funcs.save_riff(
#     data=test[0],
#     location="./furadpcm tests/011_Mice_on_Venus_LEFT_decoded.wav",
#     rate=test[1],
#     bdep=16,
#     stereo=False
# )
# import time
# start_ = time.time_ns()
# encoder.encode_file("./furadpcm tests/cop_4min.raw",
#                     location="./furadpcm tests/cop_4min",
#                     sample_rate=48000,
#                     block_format=3,
#                     step_type="lin4")
# decoded = encoder.decode_file("./furadpcm tests/cop_4min.fa")
# funcs.save_riff(data=decoded[0],
#                 location="./furadpcm tests/cop_4min.wav",
#                 rate=decoded[1],
#                 bdep=8)
# print(f"Finished in {(time.time_ns() - start_)/1e+9}s")