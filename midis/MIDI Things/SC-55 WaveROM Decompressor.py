# Initial commit


# creds to Kitrinx and NewRisingSun for like 101% of the code

def ternary(condition, true, false):  # why doesnt python have this :sob:
    if condition:
        return true
    else:
        return false
# globals
banks_55 = [0x10000, 0x1BD00, 0x1DEC0, 0x20000, 0x2BD00, 0x2DEC0, 0x30000, 0x38080]
ins_partial = {
    "unk1": 0,
    "unk2": 64,
    "idx": None,
    "par": [None for _ in range(88)],
}
instrument = {
    "name": [None for _ in range(12)],
    "head": [None for _ in range(20)],
    "part": [ins_partial, ins_partial]
}
part = {
    "name":        [None for _ in range(12)],
    "breakpoints": [None for _ in range(16)],
    "samples":     [None for _ in range(16)],
}
sample = {
    "volume":      None,               # attenuation from 12 to 0
    "offset":     [None, None, None],  #
    "attack_end":  None,               #
    "sample_len":  None,               #
    "loop_len":    None,               # loop start; sample_len - loop_len - 1
    "loop_mode":   None,               # 2 = no loop, 1 = pingpong, 0 = forward
    "root_key":    None,               # key against which the sample is transposed
    "pitch":       None,               # fine pitch; within semitone?; range from -2048 to 2047?
    "fine_volume": None,               # 1000th of a db; from -32.768 to 32.767?
}
drum = {
    "preset":      [None for _ in range(128)],
    "volume":      [None for _ in range(128)],
    "key":         [None for _ in range(128)],
    "assignGroup": [None for _ in range(128)],
    "panpot":      [None for _ in range(128)],
    "reverb":      [None for _ in range(128)],
    "chorus":      [None for _ in range(128)],
    "flags":       [None for _ in range(128)], # 0x10 = responds to kon, 0x01 = responds to koff
    "name":        [None for _ in range(12)],
}
variation = {
    "variation": [None for _ in range(128)]
}
synth = {
    "drums":       [drum for _ in range(14)],
    "variations":  [variation for _ in range(128)],
    "instruments": [instrument for _ in range(448)],
    "parts":       [part for _ in range(288)],
    "samples":     [sample for _ in range(1064)],
    "wave_data":   None,
    "ctrl_data":   None,
}

def do_sample_shenanigans(decoded_rom, address):
    data_byte = decoded_rom[address]
    shift_byte = decoded_rom[((address & 0xFFFFF) >> 5) | (address & 0xF00000)]
    shift_nibble = ternary((address & 0x10), (shift_byte >> 4 ), (shift_byte & 0x0F))
    final = ((data_byte << shift_nibble) << 14)
    final = final >> 8
    return final

address_order = [2, 0, 3, 4, 1, 9, 13, 10, 18, 17, 6, 15, 11, 16, 8, 5, 12, 7, 14, 19] # address bit order..?
byte_order =    [2, 0, 4, 5, 7, 6, 3, 1] # byte bit order
def unscramble_address(address):
    print(f"processing address {address}")
    new_addr = 0
    if address >= 0x20:  # The first 32 bytes are not encrypted
        for bit in range(20):
            new_addr |= ((address >> address_order[bit]) & 1) << bit
        return new_addr
    else:
        return address
def unscramble_byte(byte):
    new_byte = 0
    for bit in range(8):  # loop through the bits and construct new byte
        new_byte |= ((byte >> byte_order[bit]) & 1) << bit
    return new_byte
def decode_wave(files=None) -> bytearray:
    if files is None:
        files = []
    if files == []:
        raise ValueError("this needs at least some input")
    dec_buf = [0 for i in range(0x100000 * len(files))]
    for x in range(len(files)):
        try:
            enc_buf = open(files[x], "rb").read()
        except FileNotFoundError:
            print(f"uhhhhhhhh where is {files[x]} its like not found\n"
                  f"or something, results will probably break")
            continue
        for y in range(0x100000):
            dec_buf[unscramble_address(y) + (0x100000 * x)] = unscramble_byte(enc_buf[y])
    try:
        open("wave_dec.rom", "xb").write(bytearray(dec_buf))
    except FileExistsError:
        open("wave_dec.rom", "wb").write(bytearray(dec_buf))
    return bytearray(dec_buf)

# decode_wave(["./roms/55_mk1_03wave1.bin","./roms/55_mk1_04wave2.bin","./roms/55_mk1_05wave3.bin"])

test = []
buffer = open("./wave_dec.rom", "rb").read()
for i in range(0x300000):
    print(f"shenanigans at {i}")
    test.append((do_sample_shenanigans(buffer, i) >> 16) & 0b11111111)
    test.append((do_sample_shenanigans(buffer, i) >> 8 ) & 0b11111111)
    test.append((do_sample_shenanigans(buffer, i) >> 0 ) & 0b11111111)
open("./wave_dec_dec.rom", "wb").write(bytearray(test))
