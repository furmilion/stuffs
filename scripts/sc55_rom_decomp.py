from funcs import text_from_bytes
from funcs import clamp

from sc55_lookups import *

# creds to Kitrinx and NewRisingSun for descrambling code

# ==========================================================
# area of lookup stuff from sc-55 control roms
control_rom = open(f"./{input('Please enter the filename of the control ROM (must be in the same directory as this script):')}", "rb").read()

# could have merged into 3 lists, ond for each type, but cant be botgered to
# todo: check if addresses differ between versions, add hash detection if so
def_smp1 = control_rom[0x1DEC0 : 0x1FFFF]  # sample definitions part
def_smp2 = control_rom[0x1DEC0 : 0x1FFFF]

def_ins1 = control_rom[0x10000 : 0x1BCFF]  # instr definitions part
def_ins2 = control_rom[0x20000 : 0x2BCFF]

def_prt1 = control_rom[0x1BD00 : 0x1DEBF]  # partials definitions part
def_prt2 = control_rom[0x2BD00 : 0x2DEBF]

def_drum = control_rom[0x38000 : 0x3C027] # drums definitions part

class SC55Sample:
    def __init__(this):
        this.volume = 0
        this.address = 0
        this.length = 0
        this.loop_length = 0
        this.loop_mode = 0
        this.root_key = 0
        this.pitch
class SC55Partial:
    # blank for now
    def __init__(this):
        pass
class SC55Instrument:
    def __init__(this):
        this.lfo_shapes = {
            0x0: "Sine",         0x1: "Square",
            0x2: "Sawtooth", # actually i have no idea if its a falling or rizing one
            0x3: "Triangle",
            0x4: "Invalid",      0x5: "Invalid",
            0x6: "Invalid",      0x7: "Invalid",
            0x8: "Random (S&H)", 0x9: "Random (S&G)", 0xa: "Random (S&G)",
            0xb: "Invalid",      0xc: "Invalid",      0xd: "Invalid", 0xe: "Invalid",
            0xf: "Invalid",
        } # weird "grouping"
        this.lfo_rate_lut = LUT_lfo_rate
        this.lfo_time_lut = LUT_lfo_time
        this.lfo_depth_lut = LUT_lfo_depth
        this.name = "            "  # inst name (12 ascii)
        this.common = []            # instrument params, 20 bytes
        this.partials = []          # partials data; list of 2 lists
        this.exists = False

    def deconstruct_instrument(this, data: bytes | list = None):
        if not data:
            print("must data")
        if len(data) != 216:
            print("data must be 216 bytes")
            return
        this.name = text_from_bytes(data[:12])
        this.common = data[12:20 + 12]
        this.partials = [
            data[20 + 12:20 + 12 + 88 + 4],                  # partial 1
            data[20 + 12 + 88 + 4:20 + 12 + 88 + 4 + 88 + 4] # partial 2
        ]
        

    def print_inst(this):
        return (
            # the "0xX" indices are just there to help me not get lost in stuff;
            # maybe they will actually be useful to someone else,
            # but for me I am just making sure I didn't get stuff wrong.
            f'======================= INSTRUMENT PARAMETERS =======================\n'
            f'0x0 Attenuation level:       {this.common[0]}                            \n'
            f'0x1 Common LFO shape:        {this.lfo_shapes[this.common[2] & 0xf]}     \n'
            f'0x2 Common LFO phase offset: {((this.common[2] >> 4) & 0xf) * 22.5}deg   \n' # no idea if lfo actually has non-90deg offsets, this is just in case
            f'0x3 Common LFO rate:         {this.lfo_rate_lut[this.common[3]]}hz       \n'
            f'0x4 Common LFO delay:        {this.lfo_time_lut[this.common[4]]}s        \n'
            f'0x5 Common LFO fade:         {this.lfo_time_lut[this.common[5]]}s        \n'
            f'0x6 Used partials:           {["none", "1", "2", "1, 2"][this.common[6] & 3]}\n'
            f'0x7 Pitch correction:        {["none", "1", "2"][this.common[7] & 3]}    \n'
            f'                                                                         \n'
            f'======================== PARTIAL  PARAMETERS ========================\n'
            f'{this.print_partial(1)}'
            f'{this.print_partial(2)}'
        ) if this.exists else print("Instrument does not exist yet!")
    def print_partial(this, partial: int = 1):
        partial = clamp(partial, 1, 2)
        return (
            f'Partial {partial}:\n'
            f'    0x00 0x01 Mysterious value:              {(this.partials[partial][0] << 8) | this.partials[partial][1]}\n'
            f'    0x02 0x03 Partial #:                     {(this.partials[partial][2] << 8) | this.partials[partial][3]}\n'
            f'         0x04 Part LFO shape:                {this.lfo_shapes[this.partials[partial][4] & 0xf]}            \n'
            f'         0x04 Part LFO phase offset:         {((this.partials[partial][4] >> 4) & 0xf) * 22.5}deg          \n'
            f'         0x05 Part LFO rate:                 {this.lfo_rate_lut[this.partials[partial][5]]}hz              \n'
            f'         0x06 Part LFO delay:                {this.lfo_time_lut[this.partials[partial][6]]}s              \n'
            f'         0x07 Part LFO fade:                 {this.lfo_time_lut[this.partials[partial][7]]}s               \n'
            f'         0x09 Panpot:                        {"random" if this.partials[partial][9] == 0 else (this.partials[partial][9] - 64)}\n'
            f'         0x0A Coarse pitch:                  {this.partials[partial][10] - 64} semitones                   \n'
            f'         0x0B Fine pitch:                    {this.partials[partial][11] - 64} cents                       \n'
            f'         0x0C Random pitch:                  {"none" if this.partials[partial][12] == 0 else this.partials[partial][12]}\n'
            f'         0x0D Pitch key follow:              {"full" if this.partials[partial][13] == 0 else "none" if this.partials[partial][13] == 10 else str(10 - this.partials[partial][13]) + "/10"}\n' # is this how it is?
            f'         0x0E Inst LFO depth:                {this.lfo_depth_lut[14]} cents                      \n'
            f'         0x0F Part LFO depth:                {this.lfo_depth_lut[15]} cents                      \n'
            f'         0x10 Pitch envelope depth:          {this.lfo_depth_lut[15]} units                      \n' # todo: figure out later
            f'         0x12 Initial pitch envelope level:  {64 - this.partials[partial][18]}                             \n'
            f'         0x17 P.env Attack 1 time:           {64 - this.partials[partial][23]} units                       \n'
            f'         0x13 P.env Attack 1 pitch level:    {64 - this.partials[partial][19]}                             \n'
            f'         0x18 P.env Attack 2 time:           {64 - this.partials[partial][24]} units                       \n'
            f'         0x14 P.env Attack 2 pitch level:    {64 - this.partials[partial][20]}                             \n'
            f'         0x19 P.env Decay 1 time:            {64 - this.partials[partial][25]} units                       \n'
            f'         0x15 P.env pitch Sustain level:     {64 - this.partials[partial][21]}                             \n'
            f'         0x1A P.env Decay 2 time:            {64 - this.partials[partial][26]} units                       \n'
            f'         0x1B P.env Release time:            {64 - this.partials[partial][27]} units                       \n'
            f'         0x16 P.env pitch Release level:     {64 - this.partials[partial][22]}                             \n'
            f'         0x22 P.env velocity sensetivity:    {64 - this.partials[partial][34]}×2.4×(127 - v)               \n'
            f'         0x25 TVF Cutoff Frequency:          {64 - this.partials[partial][37]}               \n'
        ) if this.exists else print("Instrument does not exist yet!")


class SC55:
    def __init__(this):
        this.instruments = []
        this.partials = []

def get_ins_data(data: bytes | list = None):
    if not data:
        print("must data")
    if len(data) < 16:
        pass
# ==========================================================

def ternary(condition, true, false):  # TODO: replace all usages with guarded conditions
    if condition:
        return true
    else:
        return false

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
def descramble_wave(files=None) -> bytearray:
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
        open("../midis/MIDI Things/wave_dec.rom", "xb").write(bytearray(dec_buf))
    except FileExistsError:
        open("../midis/MIDI Things/wave_dec.rom", "wb").write(bytearray(dec_buf))
    # return bytearray(dec_buf)

# descramble_wave(["./roms/55_mk1_03wave1.bin","./roms/55_mk1_04wave2.bin","./roms/55_mk1_05wave3.bin"])