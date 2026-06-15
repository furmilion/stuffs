"""
This is meant to use in out proprietary STMVGM VGM player, which requires a real chip rather than emulating one.

The player basically consists of following stuff:
    THE SETUP:
        the basic setup of all stuff for STM
    THE MAIN LOOP:
        the main player loop.
        the player basically iterats over the array of values and runs corresponding commands via "switch/case" statements

This file basically just composes the headerless vgm array        
"""

from pathlib import Path

import struct
import random
import gzip

GZ = gzip

VERSION = 1.36

random_messages = [  # random messages to insert at the end of file, every update there is a little bit more added
    "what the fuck", "this sucks", "please help me",
    "please kill me", "it was a pain in the ass", "shit",
    "DUDE", "MANE TAFDJ", "this is all clownery",
    "crazy stuff", "doom 32x", "эмоция школы, as Saturn would've said",
    "MAGIC BOOBY", "🥀", "💀", "😭😭😭", "YEAAHHA BABY THATS WHAT WEVE BEEN WAITING FOR THATS WHAT ITS ALL ABOUT",
    "this bro really thinks hes gonna play it on real hardware 😭😭🙏🥀", "#include <fuck.h>",
    "#include <kill_em_all.h>", "if it exists, it can run doom. except if it's our OPL3.",
    "well, i've tried. that's all i can do.", "my work here is done", "but it didnt do anything!",
    "... but it was not effective.", "STM32, I CHOOSE YOU!", "⚡⚡⚡ OPL3 - В С Ё ⚡⚡⚡",
    "и на это я просрал свою жизнь.", "hey you, you're finally awake.", "breaking bad, breaking rad", "чайзенберг",
    "назови моё имя", "это не клоунада, это целый, мать его, цирк", "натурал или нет -- вот в чём вопрос.", "... но это неточно",
    "сатурн как-то спросил меня, записался ли я в фурри фембои. да.", "https://www.youtube.com/watch?v=-oySbmMeIfI",
    "я пытался.", "без ГМО", "deez nutsы", "с б", "без б", "c4 бомбоклад", "ратной заебал в кс2 играть", "боже мой, да всем насрать",
    "заткнись мэг", "присаживайтесь детки. сейчас я вам историю одну расскажу, о том каак мы с сатурном OPLL работать заставляли...",
    "что?", "@everyone help", "@saturn announcements    the genesis has risen!!", "todo: fix samples vgms"
]

stream_chip = [  # an array of stream chips
    "SN76489", "Yamaha YM2413 'OPLL'", "Yamaha YM2612 'OPN-2'", "Yamaha YM2151 'OPM'",
    "SegaPCM", "Ricoh RF5C68", "Yamaha YM2203 'OPN'", "Yamaha YM2608 'OPN-A'", "Yamaha YM2610/B 'OPN-B/B2'",
    "Yamaha YM3812 'OPL-2'", "Yamaha YM3526 'OPL'", "Yamaha YMF262 'OPL-3'", "Yamaha YMF278-B 'OPL-4'",
    "Yamaha YMF271 'OPX'", "Yamaha YMZ280B 'PCMD8'", "Ricoh RF5C164", "PWM", "General Instrument AY-3-8910",
    "GB DMG", "Ricoh RP2A03/7", "Yamaha YMW258-F 'Sega MultiPCM'", "NEC muPD7759", "OKIM6258", "OKIM6295",
    "Konami K051649", "Konami K054539", "Hudson C6280", "Namco C140", "Konami K053260",
    "Atari PoKEY", "Capcom QSound", "Yamaha YMF292 'Saturn Custom Sound Processor'", "WonderSwan",
    "Nintendo Virtual Boy VSU-VUE", "Philips SA1099", "Ensoniq ES5503", "Ensoniq ES5505/5506", "X1-010",
    "Namco C352", "Irem GA20", "Atari MIKEY",
]

# data block types ============
stream_block = [
    "YM2612 PCM",     # 0
    "RF5C68 PCM",     # 1
    "RF5C164 PCM",    # 2
    "PWM PCM",        # 3
    "OKIM6258 ADPCM", # 4
    "HuC6280 PCM",    # 5
    "SCSP PCM",       # 6
    "2A03 DPCM",      # 7
    "MIKEY PCM",      # 8
]
for i in range(56):
    stream_block.append(None)
stream_block.extend(
[
    "YM2612 PCM (compressed)",     # 0
    "RF5C68 PCM (compressed)",     # 1
    "RF5C164 PCM (compressed)",    # 2
    "PWM PCM (compressed)",        # 3
    "OKIM6258 ADPCM (compressed)", # 4
    "HuC6280 PCM (compressed)",    # 5
    "SCSP PCM (compressed)",       # 6
    "2A03 DPCM (compressed)",      # 7
    "MIKEY PCM (compressed)",      # 8
]
)
for i in range(56):
    stream_block.append(None)

stream_block.extend(
[
    "SPCM ROM",                    # 0
    "YM2608 Delta-T/ADPCM-B",      # 1
    "YM2610 ADPCM-A",              # 2
    "YM2610 Delta-T/ADPCM-B",      # 3
    "OPL4 ROM",                    # 4
    "OPX ROM",                     # 5
    "YMZ280B ROM",                 # 6
    "OPL4 RAM",                    # 7
    "Y8950 ADPCM",                 # 8
    "MultiPCM ROM",                # 9
    "muPD7759 ROM",                # A
    "MSM6295 ROM",                 # B
    "K054539 ROM",                 # C
    "C140 ROM",                    # D
    "K053260 ROM",                 # E
    "QSound ROM",                  # F
    "ES5505/ES5506 ROM",           # 10
    "X1-010 ROM",                  # 11
    "C352 ROM",                    # 12
    "GA20 ROM",                    # 13
    "RF5C68 RAM",                  # 14
    "RF5C164 RAM",                 # 15
    "2A03 RAM write",              # 16
    "SCSP RAM write",              # 17
    "ES5503 RAM write",            # 18
]
)

# ==================================

DELAYS = [
        16667, 20000,  # 0x62, 0x63
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

        23, 45, 68, 91, 113, 136, 159, 181,     # 0x70...0x7F
        204, 227, 249, 272, 295, 317, 340, 363, #

        0, 23, 45, 68, 91, 113, 136, 159,       # 0x80...0x8F
        181, 204, 227, 249, 272, 295, 317, 340  #
]


def list_files(extensions: list[str] = None) -> list[str]:
    """
    List files in the current folder using pathlib.

    Args:
        extensions (list[str], optional): Only show files with these extensions (e.g., 'txt', 'py')
    """
    if extensions is None:
        extensions = []
    # Get current directory
    current_dir = Path('.')
    files = []
    # Get all files
    if extensions:
        # Handle extension with or without dot
        for index, extension in enumerate(extensions):
            if not extensions[index].startswith('.'):
                extensions[index] = '.' + extensions[index]
        for f in range(len(extensions)):
            files += list(current_dir.glob(f'*{extensions[f]}'))
    else:
        files = [f for f in current_dir.iterdir() if f.is_file()]

    if files:
        print(f"Files in current directory{' with extensions ' + str(extensions) if extensions else ''}:")
        for _file in files:
            print(f"  {files.index(_file) + 1}. {_file.name}")
    else:
        print(f"No files found{' with extensions ' + str(extensions) if extensions else ''}")
    return [__.name for _, __ in enumerate(files)]


def pack_vgm(vgm: bytes = None, output_file: str = "array", cap: int = None):
    """
    the actual processor and packer
    """
    arr = []           # VGM data
    datablock_arr = [] # sample and misc data
    if vgm is None:
        raise ValueError("You must provide at least some data to parse.")
    if cap is None:
        cap = len(vgm)
    class VGMError(BufferError):
        def __init__(self, e):
            pass
    if vgm[:4] != b'Vgm ':
        print("Not a VGM, trying gzip...")
        try:
            vgm = GZ.open(VGM_FILES[file - 1], 'rb').read()
            if vgm[:4] != b'Vgm ':
                raise VGMError("Unfortunately, not a valid VGM.")
            print("Successfully decompressed the VGM")
        except GZ.BadGzipFile:
            raise VGMError("Unfortunately, not a valid VGM.")
    metadata = {
        "EOF":       struct.unpack('<I', vgm[4:8])[0] + 4,
        "VER":       struct.unpack('<I', vgm[8:0xC])[0],
        "TISNclock": struct.unpack('<I', vgm[0xC:0x10])[0],
        "2413clock": struct.unpack('<I', vgm[0x10:0x14])[0],
        "GD3Offset": struct.unpack('<I', vgm[0x14:0x18])[0],
        "2612clock": struct.unpack('<I', vgm[0x2C:0x30])[0],
        "TISNflags": struct.unpack('<I', vgm[0x18:0x1C])[0],
        "VGMDatOFS": struct.unpack('<I', vgm[0x34:0x38])[0] + 0x34,
        "2151clock": struct.unpack('<I', vgm[0x30:0x34])[0],
    }
    if (metadata["VER"]) > 0x150:
        metadata["2203clock"] = struct.unpack('<I', vgm[0x44:0x48])[0]
        metadata["2608clock"] = struct.unpack('<I', vgm[0x48:0x4C])[0]
        metadata["2610clock"] = struct.unpack('<I', vgm[0x4C:0x50])[0]
        metadata["3812clock"] = struct.unpack('<I', vgm[0x50:0x54])[0]  # opl2
        metadata["3526clock"] = struct.unpack('<I', vgm[0x54:0x58])[0]  # opl1
        metadata["8950clock"] = struct.unpack('<I', vgm[0x58:0x5C])[0]  # y8950
        metadata["F262clock"] = struct.unpack('<I', vgm[0x5C:0x60])[0]  # opl3
        metadata["F278clock"] = struct.unpack('<I', vgm[0x60:0x64])[0]  # opl4
        metadata["8910clock"] = struct.unpack('<I', vgm[0x74:0x78])[0]
        
        # misc
        metadata["SPCMclock"] = struct.unpack('<I', vgm[0x38:0x3C])[0]  # segapcm
        metadata["RF_1clock"] = struct.unpack('<I', vgm[0x40:0x44])[0]  # rf5c68
        metadata["F271clock"] = struct.unpack('<I', vgm[0x64:0x68])[0]  # opx
        metadata["Z280clock"] = struct.unpack('<I', vgm[0x68:0x6C])[0]  # ymz280
        metadata["RF_2clock"] = struct.unpack('<I', vgm[0x6C:0x70])[0]  # rf5c164
        metadata["PWM_clock"] = struct.unpack('<I', vgm[0x70:0x74])[0]  # generic pwm dac
        metadata["DMG_clock"] = struct.unpack('<I', vgm[0x80:0x84])[0]  # gb dmg
        metadata["2A03clock"] = struct.unpack('<I', vgm[0x84:0x88])[0]  # nes apu
        metadata["W258clock"] = struct.unpack('<I', vgm[0x88:0x8C])[0]  # yamaha ymw258f 'MultiPCM' GEW8
        metadata["muPDclock"] = struct.unpack('<I', vgm[0x8C:0x90])[0]  # NEC muPD7759
        metadata["6258clock"] = struct.unpack('<I', vgm[0x90:0x94])[0]  # oki msm
        metadata["6258clock"] = struct.unpack('<I', vgm[0x90:0x94])[0]  # oki msm
        metadata["0549clock"] = struct.unpack('<I', vgm[0x9C:0xA0])[0]  # konami k051649
        metadata["0539clock"] = struct.unpack('<I', vgm[0xA0:0xA4])[0]  # konami k054539
        metadata["TG16clock"] = struct.unpack('<I', vgm[0xA4:0xA8])[0]  # hudson c6280
        metadata["C140clock"] = struct.unpack('<I', vgm[0xA8:0xAC])[0]  # namco c140
        metadata["0560clock"] = struct.unpack('<I', vgm[0xAC:0xB0])[0]  # konami k053260 
        metadata["POK_clock"] = struct.unpack('<I', vgm[0xB0:0xB4])[0]  # atari pokey
        metadata["QSNDclock"] = struct.unpack('<I', vgm[0xB4:0xB8])[0]  # capcom qsound
        metadata["F292clock"] = struct.unpack('<I', vgm[0xB8:0xBC])[0]  # scsp
        metadata["WSWNclock"] = struct.unpack('<I', vgm[0xC0:0xC4])[0]  # wonderswan
        metadata["VSU_clock"] = struct.unpack('<I', vgm[0xC0:0xC4])[0]  # vsu-vue clock
        metadata["SAA_clock"] = struct.unpack('<I', vgm[0xC4:0xC8])[0]  # philips saa1099
        print("yeaa baeeby we got extra chips")
    else:
        metadata["VGMDatOFS"] = 0x40
        metadata["2203clock"] = 0
        metadata["2608clock"] = 0
        metadata["2610clock"] = 0
        metadata["3812clock"] = 0  # opl2
        metadata["3526clock"] = 0  # opl1
        metadata["8950clock"] = 0  # y8950
        metadata["F262clock"] = 0  # opl3
        metadata["F278clock"] = 0  # opl4
        metadata["8910clock"] = 0
    gd3 = {}
    gd3["VER"] = struct.unpack('<I', vgm[metadata["GD3Offset"] + 4:metadata["GD3Offset"] + 8])[0]
    gd3["DAT"] = vgm[metadata["GD3Offset"] + 8:]
    #print(gd3['DAT'])
    print(f"VGM Data Offset: {metadata['VGMDatOFS'], hex(metadata['VGMDatOFS'])}")
    print(f"GD3 Data Offset: {metadata['GD3Offset'], hex(metadata['GD3Offset'])}")
    print(
        f"Essential data:\n"
        f"TI SN76489  present: {bool(metadata['TISNclock'])} | {metadata['TISNclock']}hz                                                         \n"
        f"YM2413 OPLL present: {bool(metadata['2413clock'])} | {metadata['2413clock']}hz                                                         \n"
        f"YM2612 OPN2 present: {bool(metadata['2612clock'])} | {metadata['2612clock'] & 0x7fffffff}hz | Is YM3438  OPN2C: {metadata['2612clock'] >> 31}\n"
        f"YM2151 OPM  present: {bool(metadata['2151clock'])} | {metadata['2151clock'] & 0x7fffffff}hz | Is YM2164  OPP:   {metadata['2151clock'] >> 31}\n"
        f"YM2203 OPN  present: {bool(metadata['2203clock'])} | {metadata['2203clock']}hz                                                         \n"
        f"YM2608 OPNA present: {bool(metadata['2608clock'])} | {metadata['2608clock']}hz                                                         \n"
        f"YM2610 OPNB present: {bool(metadata['2610clock'])} | {metadata['2610clock'] & 0x7fffffff}hz | Is YM2610B OPNB2: {metadata['2610clock'] >> 31}\n"
        f"YM3812 OPL2 present: {bool(metadata['3812clock'])} | {metadata['3812clock']}hz                                                         \n"
        f"YM3526 OPL1 present: {bool(metadata['3526clock'])} | {metadata['3526clock']}hz                                                         \n"
        f"Y8950       present: {bool(metadata['8950clock'])} | {metadata['8950clock']}hz                                                         \n"
        f"YMF262 OPL3 present: {bool(metadata['F262clock'])} | {metadata['F262clock']}hz                                                         \n"
        f"YMF278 OPL4 present: {bool(metadata['F278clock'])} | {metadata['F278clock']}hz                                                         \n"
        f"AY-3-8910   present: {bool(metadata['8910clock'])} | {metadata['8910clock']}hz                                                         \n"
        )
    print(f"File length: {len(vgm)}")
    print(f"Without GD3: {len(vgm[:metadata['GD3Offset']])}")
    print(f"Only data:   {len(vgm[metadata['VGMDatOFS']:metadata['GD3Offset']])}")
    die = False
    block_id = 0  # to keep track of current data block id
    dump_mode = str(input("Block dump mode:\nd: always dump\ni: always ignore\nanything else: ask\n")).lower()  # either ignore all streams or dump all streams since the moment flag is set
    dump_mode = dump_mode[0] if len(dump_mode) >= 1 else "i"
    print(f"dump mode: {dump_mode}")
    input("Press enter to begin...")
    cursor = metadata["VGMDatOFS"]
    while cursor < metadata["EOF"] and not die and cursor < cap:
        # cursor < (len(vgm) - metadata["VGMDatOFS"]) 
        current = vgm[cursor]
        print(f'current byte: {hex(current)} @ {hex(cursor)}')
        match current:
            
            # chip commands
            case 0x4F:  # game gear stereo
                if metadata["TISNclock"]:
                    # print(f"writing Game Gear: {hex(vgm[cursor + 1])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    cursor += 2
                else:
                    cursor += 2
            case 0x50:  # sn7
                if metadata["TISNclock"]:
                    # print(f"writing SN7: {hex(vgm[cursor + 1])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    cursor += 2
                else:
                    cursor += 2
            case 0x51:
                if metadata["2413clock"]:
                    print(f"writing OPLL: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x52:
                if metadata["2612clock"]:
                    # print(f"writing OPN2 port 1: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x53:
                if metadata["2612clock"]:
                    # print(f"writing OPN2 port 2: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x54:
                if metadata["2151clock"]:
                    # print(f"writing OPM: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x55:
                if metadata["2203clock"]:
                    # print(f"writing OPN1: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x56:
                if metadata["2608clock"]:
                    # print(f"writing OPNA port 1: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x57:
                if metadata["2608clock"]:
                    # print(f"writing OPNA port 2: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x58:
                if metadata["2610clock"]:
                    # print(f"writing OPNB port 2: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x59:
                if metadata["2610clock"]:
                    # print(f"writing OPNB port 2: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x5A:
                if metadata["3812clock"]:
                    # print(f"writing OPL2: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x5B:
                if metadata["3526clock"]:
                    # print(f"writing OPL1: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x5C:
                if metadata["8950clock"]:
                    # print(f"writing Y8950: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x5E:
                if metadata["F262clock"]:
                    # print(f"writing OPL3 port 1: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0x5F:
                if metadata["F262clock"]:
                    # print(f"writing OPL3 port 2: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else: cursor += 3
            case 0xA0:
                if metadata["8910clock"]:
                    # print(f"writing AY-like: {hex(vgm[cursor + 1])}/{hex(vgm[cursor + 2])}")
                    arr.append(vgm[cursor])
                    arr.append(vgm[cursor + 1])
                    arr.append(vgm[cursor + 2])
                    cursor += 3
                else:
                    cursor += 3
            
            # non-chip commands
            case 0x61:
                # print(f"delay: {((1000 / 44100) * ((vgm[cursor + 2] << 8) + vgm[cursor + 1])) * 1000} nanoseconds")
                arr.append(vgm[cursor])
                arr.append(vgm[cursor + 1])
                arr.append(vgm[cursor + 2])
                cursor += 3
            case               0x62 | 0x63 |\
                 0x70 | 0x71 | 0x72 | 0x73 | 0x74 | 0x75 | 0x76 | 0x77 |\
                 0x78 | 0x79 | 0x7A | 0x7B | 0x7C | 0x7D | 0x7E | 0x7F |\
                 0x80 | 0x81 | 0x82 | 0x83 | 0x84 | 0x85 | 0x86 | 0x87 |\
                 0x88 | 0x89 | 0x8A | 0x8B | 0x8C | 0x8D | 0x8E | 0x8F :
                # print(f"accessing delay {hex(vgm[cursor])}/{hex(vgm[cursor] - 0x62)}:", end='')
                # print(f"{DELAYS[vgm[cursor] - 0x62]} nanosecs")
                arr.append(vgm[cursor])
                cursor += 1
            case 0x66: print("done"); die = True
            
            # streams
            case 0x90:
                if not dump_mode in ["i", "d"]:
                    print(f"stream setup:                              \n"
                          f"ID:        {hex(vgm[cursor + 1])}          \n"
                          f"Chip Type: {stream_chip[vgm[cursor + 2]]}  \n"
                          f"register {hex(vgm[cursor + 3])}\n at port {hex(vgm[cursor + 4])}\n")
                    input("Press enter to continue...")
                    
                arr.extend(vgm[cursor:cursor+5])
                cursor += 5
                
            case 0x91:
                if not dump_mode in ["i", "d"]:
                    print(f"stream data:                                    \n"
                          f"ID: {hex(vgm[cursor + 1])}                      \n"
                          f"Data bank: {stream_block[vgm[cursor + 2]]}      \n"
                          f"step base: {hex(vgm[cursor + 3])}\n"
                          f"step size: {hex(vgm[cursor + 4])}\n")
                    input("Press enter to continue...")
                    
                arr.extend(vgm[cursor:cursor+5])
                cursor += 5
                
            case 0x92:
                if not dump_mode in ["i", "d"]:
                    print(f"stream frequency:                           \n"
                          f"ID: {hex(vgm[cursor + 1])}                  \n"
                          f"Frequency: {struct.unpack('<I', vgm[cursor + 2:cursor + 6])[0]}hz\n")
                    input("Press enter to continue...")
                    
                arr.extend(vgm[cursor:cursor+6])
                cursor += 6
                
            case 0x93:
                if not dump_mode in ["i", "d"]:
                    datofs = struct.unpack('<I', vgm[cursor + 2:cursor + 6])[0] - 1
                    datlen = struct.unpack('<I', vgm[cursor + 7:cursor + 11])[0]
                    print(f"start stream:                             \n"
                          f"ID:                {hex(vgm[cursor + 1])}                \n"
                          f"Data start offset: {datofs}      \n"
                          f"Mode:              {hex(vgm[cursor + 6])}\n"
                          f"                   length mode: {['ignore', 'amnt of cmds', 'length in msecs', 'until data end'][vgm[cursor + 6]&0b11]}\n"
                          f"                   is reverse: {True if vgm[cursor + 6] & 0x10 else False}\n"
                          f"                   auto loop:  {True if vgm[cursor + 6] & 0x80 else False}\n"
                          f"Length:            {struct.unpack('<I', vgm[cursor + 7:cursor + 11])[0]}\n")
                    input("Press enter to continue...")
                    
                arr.extend(vgm[cursor:cursor+11])
                cursor += 11
                
            case 0x94:
                if not dump_mode in ["i", "d"]:
                    print(f"end stream:\n"
                          f"ID: {hex(vgm[cursor + 1]) if vgm[cursor + 1] < 0xFF else 'all streams'}\n")
                    input("Press enter to continue...")
                    
                arr.extend(vgm[cursor:cursor+2])
                cursor += 2
                
            case 0x95:
                if not dump_mode in ["i", "d"]:
                    print(f"fast start stream:                                   \n"
                          f"ID:    {hex(vgm[cursor + 1])}                        \n"
                          f"Block: {hex(vgm[vgm[cursor + 3] | cursor + 2])}      \n"
                          f"Mode:  {hex(vgm[cursor + 4])}\n"
                          f"       length mode: {['ignore', 'amnt of cmds', 'length in msecs', 'until data end']}\n"
                          f"       auto loop: {True if vgm[cursor + 4] & 0x1  else False}\n"
                          f"       reverse:    {True if vgm[cursor + 4] & 0x10 else False}\n")
                    input("Press enter to continue...")
                    
                arr.extend(vgm[cursor:cursor + 5])
                cursor += 5
            
            # data blocks
            case 0x67:  # omfg the meme
                arr.extend([0x67, 0x66])
                
                if not dump_mode in ["i", "d"]:
                    if vgm[cursor + 1] != 0x66:
                        print("something ain't right")
                    print(f"DATA BLOCK:\n"
                          f"Type:   {stream_block[vgm[cursor + 2]]}\n"
                          f"Length: {struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0]}")
                    if str(input("dump? [y/n]")).lower()[0] == "y":
                        open(f"data_block_{block_id}_" f"{stream_block[vgm[cursor + 2]]}" "_" f"{hex(struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0])}" ".raw", "wb").write(vgm[cursor + 7:cursor + 7 + struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0]])
                    else:
                        print("skipped dumping")
                    
                elif dump_mode == "d":
                    open(f"data_block_{block_id}_" f"{stream_block[vgm[cursor + 2]]}" "_" f"{hex(struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0])}" ".raw", "wb").write(vgm[cursor + 7:cursor + 7 + struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0]])
                else:
                    pass
                    
                datablock_arr.extend(vgm[cursor:cursor + struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0]])
                cursor += 7 + struct.unpack('<I', vgm[cursor + 3:cursor + 7])[0]
                block_id += 1
                
            case 0xE0:
                print(f"PCM seek location: {struct.unpack('<I', vgm[cursor + 1:cursor + 5])}")
                cursor += 5
                
        # print(f'current byte: {hex(current)} @ {hex(cursor)}')
    # print(arr)
    print("creating array")
    array = open(f"./{output_file}.c", "w", encoding='utf8')
    array.write(f"#define ARRAY_LENGTH {len(arr) + len(datablock_arr) + 2}\n"
                 "const uint8_t vgm[ARRAY_LENGTH] = {\n")
    print("procesing data")
    open(f"./{output_file}_VGM.raw", "wb").write(bytearray(arr))
    open(f"./{output_file}_VGM.raw", "ab").write(bytearray(datablock_arr))
   
    for _, __ in enumerate(datablock_arr):
        if not (_ + 1) % 16:
            array.write(f"{__},\n")
        else:
            array.write(f"{__}, ")
    array.write(f"\n")
    for _, __ in enumerate(arr):
        if not (_ + 1) % 16:
            array.write(f"{hex(__)},\n")
        else:
            array.write(f"{hex(__)}, ")
    array.write(f"\n")
    
    print("spicing things up...")
    array.write("\n};\n//" + f"{random_messages[random.randint(0, len(random_messages) - 1)]}")
    print("done!")

VGM_FILES = list_files(['.vgm', '.vgz'])

if __name__ == "__main__":
    try:
        file = int(input('Enter the ID of the file you want to process\n'))
        cap = int(input("Cap array length at...\n"))
        if cap < 1:
            cap = 2147483647
    except ValueError:
        print("bitch fuck yo ass mate i aint doing shit")
        raise Exception("ass")
    # print(VGM_FILES)
    pack_vgm(open(VGM_FILES[file - 1], 'rb').read(),cap=cap)


