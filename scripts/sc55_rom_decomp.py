from funcs import text_from_bytes, clamp, note_from_key, _
from os import name as osName
from sc55_lookups import *
from FurWave import WaveWriter
# creds to Kitrinx and NewRisingSun for descrambling code

try:
    import numpy as np
except ImportError:
    print("Please install numpy for this module to work, or it's gonna fail right there.")

# local auto open stuff
model = "mk1"
firmware = "_120"
wave = "_wave/"  # wave roms
try:
    WAVE = open(f"{model}{firmware}_wave_descrambled.rom", "rb").read()
    print("Successfully loaded descrambled unified wave ROM")
except FileNotFoundError:
    print("Descrambled unified wave ROM not found, loading separate files")
    WAVE = []
    try:
        WAVE.extend(list(open(f"{model}{firmware}_wave1_descrambled.rom", "rb").read()))
        WAVE.extend(list(open(f"{model}{firmware}_wave2_descrambled.rom", "rb").read()))
        WAVE.extend(list(open(f"{model}{firmware}_wave3_descrambled.rom", "rb").read()))
        print("Successfully loaded descrambled seoarate wave ROMs")
    except FileNotFoundError: print("None or not all WAVE roms succeeded to load, sample decoding and dumping may fail.")

from pathlib import Path
mkdir = Path.mkdir
main = __name__ == "__main__"

mainpath = "../../roms/" if osName == "posix" else \
    r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-SC55 ROMSET/"
control_rom = open(f"{mainpath}{model}{firmware}/sc55_rom2.bin", "rb").read()

# ======== Constants and important ========
address_order = [2, 0, 3, 4, 1, 9, 13, 10, 18, 17, 6, 15, 11, 16, 8, 5, 12, 7, 14, 19] # address bit order..?
byte_order =    [2, 0, 4, 5, 7, 6, 3, 1] # byte bit order
def unscramble_address(address):
    # print(f"processing address {address}")
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

# inst_count = 224  # instruments per bank
bank_offset = 0x10000  # constant distance between 2 banks of definitions
wave_size = 0x100000   # size of a single wave ROM
partial_size = 60      # size of a single partial defenition
inst_size = 216        # size of a single instrument definituon
sample_size = 16       # size of a single sample definition
try:
    byte_lut = np.array(list(open("LUT_unscrambled_byte.lut", "rb").read()), np.uint8)
    print("Loaded descrambled byte LUT.")
except FileNotFoundError:
    print("Generating byte LUT...")
    byte_lut = np.array([unscramble_byte(_) for _ in range(256)], np.uint8)
    print("Done.")
    open("LUT_unscrambled_byte.lut", "wb").write(bytearray(byte_lut))
try:
    address_lut = np.array(list(open("LUT_unscrambled_address.lut", "rb").read()), np.uint8)
    address_lut = np.array(address_lut.view(np.uint32), np.uint32)
    print("Loaded descrambled address LUT.")
except:
    print("Generating address LUT...")
    address_lut = np.array([unscramble_address(_) for _ in range(wave_size)], np.uint32)
    print("Done.")
    open("LUT_unscrambled_address.lut", "wb").write(bytearray(address_lut))
#address_lut_gen = np.array([unscramble_address(_) for _ in range(wave_size)], np.uint32)
#print(f"LUT validation:loaded address lut == generated address lut: {address_lut == address_lut_gen}")
# ==========================================================
# area of lookup stuff from sc-55 control roms
# control_rom = open(f"./{input('Please enter the filename of the control ROM (must be in the same directory as this script):')}", "rb").read()

# could have merged into 3 lists, ond for each type, but cant be botgered to
# todo: add hash detection

# todo: note to self, finding instrument and partial banks may be as simple as searching the name or
# seeing at how definition sections the order "instrument 》partial 》sample".

def_ins = [
    control_rom[0x10000 : 0x1BD00],  # instr definitions part
    control_rom[0x10000 + bank_offset : 0x1BD00 + bank_offset]
]
def_prt = [
    control_rom[0x1BD00 : 0x1DEC0],  # partials definitions part
    control_rom[0x1BD00 + bank_offset : 0x1DEC0 + bank_offset]
]
def_smp = [
    control_rom[0x1DEC0 : 0x20000],  # sample definitions part
    control_rom[0x1DEC0 + bank_offset : 0x20000 + bank_offset]
]
def_drum = control_rom[0x38000 : 0x3C027] # drums definitions part
# ==========================================================
class SC55Sample:
    def __init__(this):
        this.volume = 0
        this.address = 0
        this.start_offset = 0
        this.length = 0
        this.loop_length = 0
        this.loop_mode = 0  # 0: fw, 1: bi, 2: oneshot
        this.root_key = 0
        this.pitch_offs_preloop = 0
        this.pitch_offs_loop = 0
        this.bank = 0
        this.exists = False
    
    def deconstruct_sample(this, data: bytes | list = None):
        if not data:
            print("must data")
            return
        if len(data) != 16:
            print("data must be 16 bytes")
            return
        this.volume = data[0]
        this.address = (data[1] << 16) | (data[2] << 8) | data[3]
        this.start_offset = (data[4] << 8) | data[5]
        this.length = (data[6] << 8) | data[7]
        this.loop_length = (data[8] << 8) | data[9]
        this.loop_mode = data[10]
        this.root_key = data[11]
        this.pitch_offs_preloop = ((data[12] << 8) | data[13]) - 1024
        this.pitch_offs_loop = ((data[14] << 8) | data[15]) - 1024
        this.bank = (this.address & 0x700000) >> 20
        this.exists = True
    
    def print_sample(this):
        return (
            f'Volume:               {this.volume}\n'
            f'Start address in ROM: {this.address}\n'
            f'Start offset:         {this.start_offset}\n'
            f'Length:               {this.length}\n'
            f'Loop length:          {this.loop_length}\n'
            f'Loop mode:            {["forward", "ping-pong", "oneshot"][this.loop_mode]}\n'
            f'Root key:             {note_from_key(this.root_key)} ({this.root_key})\n'
            f'Initial pitch offset: {this.pitch_offs_preloop}\n'
            f'Loop pitch offset:    {this.pitch_offs_loop}\n\n'
        ) if this.exists else "This sample does not exist yet!"
        

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
        # print(data)
        if not data:
            print("must data")
            return
        if len(data) != 216:
            print("data must be 216 bytes")
            return
        this.name = text_from_bytes(data[:12], 12)
        print(f"[{this.name}]")
        this.common = data[12:20 + 12]
        this.partials = [
            data[20 + 12:20 + 12 + 88 + 4],                  # partial 1
            data[20 + 12 + 88 + 4:20 + 12 + 88 + 4 + 88 + 4] # partial 2
        ]
        this.exists = True

    def print_inst(this):
        return (
            # the "0xX" indices are just there to help me not get lost in stuff;
            # maybe they will actually be useful to someone else,
            # but for me I am just making sure I didn't get stuff wrong.
            f'[{this.name}]\n'
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
        partial = clamp(partial, 1, 2) - 1
        return (
            f'Partial {partial}:\n'
            f'    0x00 0x01 Mysterious value:              {(this.partials[partial][0] << 8) | this.partials[partial][1]}\n'
            f'    0x02 0x03 Partial #:                     {(this.partials[partial][2] << 8) | this.partials[partial][3]}\n'
            f'         0x04 Part LFO shape:                {this.lfo_shapes[this.partials[partial][4] & 0xf]}            \n'
            f'         0x04 Part LFO phase offset:         {((this.partials[partial][4] >> 4) & 0xf) * 22.5}deg          \n'
            f'         0x05 Part LFO rate:                 {this.lfo_rate_lut[this.partials[partial][5]]}hz              \n'
            f'         0x06 Part LFO delay:                {this.lfo_time_lut[this.partials[partial][6]]}s               \n'
            f'         0x07 Part LFO fade:                 {this.lfo_time_lut[this.partials[partial][7]]}s               \n'
            f'         0x09 Panpot:                        {"random" if this.partials[partial][9] == 0 else (this.partials[partial][9] - 64)}\n'
            f'         0x0A Coarse pitch:                  {this.partials[partial][10] - 64} semitones                   \n'
            f'         0x0B Fine pitch:                    {this.partials[partial][11] - 64} cents                       \n'
            f'         0x0C Random pitch:                  {"none" if this.partials[partial][12] == 0 else this.partials[partial][12]}\n'
            f'         0x0D Pitch key follow:              {"full" if this.partials[partial][13] == 0 else "none" if this.partials[partial][13] == 10 else str(10 - this.partials[partial][13]) + "/10"}\n' # is this how it is?
            f'         0x0E Inst LFO depth:                {this.lfo_depth_lut[14]} cents                                \n'
            f'         0x0F Part LFO depth:                {this.lfo_depth_lut[15]} cents                                \n'
            f'         0x10 Pitch envelope depth:          {this.lfo_depth_lut[15]} units                                \n' # todo: figure out later
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
            f'         0x25 TVF Cutoff Frequency:          {64 - this.partials[partial][37]}                             \n'
            ) if this.exists else print("Instrument does not exist yet!")

class SC55:
    def __init__(this):
        this.instruments = []
        this.partials = []

def decode_roland_dpcm(data: list = None, smp: SC55Sample = SC55Sample()) -> None | list:
    if not data:
        bank_idx = smp.bank + 1
        length = smp.length
        match bank_idx:
            case 0:
                bank_idx = 0 * wave_size
            case 1:
                bank_idx = 1 * wave_size
            case 2:
                if model.lower() == "mk2":
                    bank_idx = 2 * wave_size
                else:
                    bank_idx = 1 * wave_size
            case 4:
                bank_idx = 2 * wave_size
            case _:
                print(f"bank index is {bank_idx} what")
    else:
        length = len(data)
    out = []
    val = 0
    if not data:
        actual_address = (smp.address & 0xFFFFF) + bank_idx
        if not WAVE:
            raise ValueError("A decrypted ROM must be provided.")
        rom = WAVE[bank_idx:bank_idx + wave_size]
        rom_addr = smp.address & 0xFFFFF
        for sample in range(length):
            counter = actual_address + sample
            c_byte = WAVE[counter]
            c_byte -= 256 if c_byte >= 128 else c_byte
            
            shift_addr = ((counter & 0xFFFFF) >> 5) | (counter & 0xF00000)
            #print(f"shift address is {shift_addr}")
            sbyte      = WAVE[shift_addr]
            snibble    = (sbyte >> 4) if (counter & 0x10) else (sbyte & 0x0F)
    
            final  = (c_byte << snibble) << 14
            final  = max(-2147483648, min(2147483647, final))
            val += final / (1 << 31)
            print(f"final_accum: {final}\nval: {val}")
            out.append(val)
        return out
        
            
def dump_insts(
        folder=True  # whether to make a folder 
                     # and dump instruments as
                     # separate txt files into it
                     # instead of a single big one
    ):
    if not folder:
        try: log = open(f"{model}{firmware}_instruments.txt", "xt")
        except FileExistsError: log = open(f"{model}{firmware}_instruments.txt", "wt") #i wish there was an easiee way to do this
    if folder:
        try: mkdir(f"{model}{firmware}_instruments")
        except: pass
    for bank in def_ins:
        #print(bank)
        for ins in range(len(bank)//inst_size):
            #print(bank[216 * ins:216 * ins + 216])
            inst = SC55Instrument()
            inst.deconstruct_instrument(bank[inst_size * ins:inst_size * ins + inst_size])
            print(f'Inst {ins}: [{inst.name}]')
            if inst.name:
                if not folder:
                    log.write(
                        f"BANK {def_ins.index(bank)} | INSTRUMENT {ins}\n" +
                        inst.print_inst() +
                        "\n"
                )
                if folder:
                    try: open(f"{model}{firmware}_instruments/{inst.name}_{ins}.txt",'xt').write(
                        f"BANK {def_ins.index(bank)} | INSTRUMENT {ins}\n" +
                        inst.print_inst()
                    )
                    except FileExistsError: open(f"{model}{firmware}_instruments/{inst.name}_{ins}.txt",'wt').write(
                        f"BANK {def_ins.index(bank)} | INSTRUMENT {ins}\n" +
                        inst.print_inst()
                )
        print('done')

            
def dump_samples(decode_dpcm: bool = False):
    try: log = open(f"{model}{firmware}_samples.txt", "xt")
    except FileExistsError: log = open(f"{model}{firmware}_samples.txt", "wt") #i wish there was an easiee way to do this
    if decode_dpcm:
        try: mkdir(f"{model}{firmware}_samples")
        except: pass
    for bank in def_smp:
        #print(bank)
        for smp in range(len(bank)//sample_size):
            #print(bank[216 * ins:216 * ins + 216])
            sample = SC55Sample()
            sample.deconstruct_sample(bank[sample_size * smp:sample_size * smp + sample_size])
            print(f'Sample {smp}')
            log.write(
                f"BANK {def_smp.index(bank)} | SAMPLE {smp}\n" +
                sample.print_sample()
            )
            if decode_dpcm:
                with WaveWriter() as w:
                    w.set_channels(1)
                    w.set_samplerate(32000)
                    w.set_data(decode_roland_dpcm(smp=sample))
                    w.set_depth(32)
                    w.set_smpl_chunk(
                        loop_starts = [sample.length - sample.loop_length],
                        loop_ends = [sample.length],
                        loop_types = [sample.loop_mode],
                        midi_unity_note = sample.root_key,
                    ) if sample.loop_mode > 1 else _()
                    w.write_file(f"{model}{firmware}_samples/sample_{smp}_{note_from_key(sample.root_key)}.wav")
        print('done')

# ==========================================================

def ternary(condition, true, false):  # TODO: replace all usages with guarded conditions
    if condition:
        return true
    else:
        return false
def descramble_wave(
        files: list = None,
        ignore: bool | int = False,  # whether to not do anything so that i dont comment out the entire function
        id: int = -1,
        one_file: bool | int = False  # whether to dump descrambled roms into a single file
) -> bytearray | None:
    if ignore:
        return
    if files is None:
        files = []
    if files == []:
        raise ValueError("this needs at least some input")
    if one_file:
        try: buffer = open(f"{model}{firmware}_wave_descrambled.rom", "xb")
        except FileExistsError: buffer = open(f"{model}{firmware}_wave_descrambled.rom", "wb")
    for x in range(len(files)):
        try: encoded_rom = open(files[x], "rb").read()
        except FileNotFoundError:
            print(f"uhhhhhhhh where is {files[x]} its like not found\n"
                  f"or something, results will probably break")
            continue
        
        dec_buf = [0 for _ in range(0x100000)]
        if not one_file:
            try: buffer = open(f"{model}{firmware}_wave{x if len(files) > 1 else id}_descrambled.rom", "xb")
            except FileExistsError: buffer = open(f"{model}{firmware}_wave{x if len(files) > 1 else id}_descrambled.rom", "wb")
        
        for y in range(0x100000):
            dec_buf[address_lut[y]] = byte_lut[encoded_rom[y]]
            print(y)
        buffer.write(bytearray(dec_buf))
        if not one_file:
            buffer.close()
        # return bytearray(dec_buf)
    if one_file:
        buffer.close()
# descramble_wave(["./roms/55_mk1_03wave1.bin","./roms/55_mk1_04wave2.bin","./roms/55_mk1_05wave3.bin"])
if main:
    descramble_wave(
        [
            f"{mainpath}{model}{wave}sc55_waverom1.bin",
            f"{mainpath}{model}{wave}sc55_waverom2.bin",
            f"{mainpath}{model}{wave}sc55_waverom3.bin",
        ],
        ignore=1,
        id=-1,
        one_file=True
    )
    #dump_insts(folder=False)
    dump_samples(decode_dpcm=True)