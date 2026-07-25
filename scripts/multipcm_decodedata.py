from time import sleep as s, sleep
from os import mkdir, remove as rm
from FurWave import *
# import wave as w
    
try:  # numpy is a better option than standard python list stuff
    import numpy as np
    NUMPY = True
    # print("nupi")
except ImportError:
    print("NumPY not found.\n"
          "It is recommended to install NumPY as this offers slightly better performance.")
    NUMPY = False

from funcs import *    # various utils used by this file that should probably also be able to be used on their own

CHIP_SETTINGS = {
    "opl4": (33868800, 32, 24),
    "gew7": (8000000, 8, 28),
    "mpcm": (9878400, 8, 28),
    "mu5":  (9400000, 8, 28),
}

class MultiPCMSampleExtractorLegacy:
    # thanks to that uhhh boykisser pfp guy i forgor their name
    # their comment stuff
    # why must I do this, I don't know.
    # but it works with this number so that's good I guess
    # ok now it works yay
    """
    NOTE: THIS A LEGACY CLASS!!!! USE THE NEW MultiPCMSampleExtractor() CLASS INSTEAD!!!
    """
    def __init__(me, out_loc, log_name, bank, bank2=None, bankswitchtype=0):
        me.addresses = {
                     "mpr-16491": "m1",  # Daytona USA -- Sample ROM
                     "mpr-16492": "m1",  # Daytona USA -- SFX ROM
                     "daytona_sampleroms": "m1",
                     "daytona_sfxroms": "m1",
                     # "daytona_sfxroms": "m1",
                     # "daytona_sfxroms": "m1",
                     "cop_sampleroms": "m1",
                     "cop_sfxroms": "m1",
                     "outrunners_sampleroms": "m2"
                    }

        me.hashes = {
                  # MD5 File Hashes for File Detection
                  # I probably will disregard the former two.
                  "00fafc26797c95f104bee47b5784929d": "m1Daytona USA Sample ROM",
                  "1d99c9ac716500586f19c5e4dd4bb4b0": "m1Daytona USA SFX ROM",

                  "6ccd6376e416a56f92b21368fd14d9df": "m1Virtua Cop Sample ROM",
                  "6e1d01e270bad869ab8c1869481033de": "m1Virtua Cop SFX ROM",

                  "bb2262db75e5c1bdf982c95cf0ff278f": "m2OutRunners Sample ROM",
        }

        me.garbage_indexes = {
                           # Garbage sample indexes

                           # Daytona USA -- Sample ROM
                           "Daytona USA Sample ROM": [40, 41, 42, 43,
                                                      92, 93,
                                                      138, 151, 152, 153, 154, 155, 164, 165, 199,
                                                      200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
                                                      210, 211, 212, 213, 214],
                           # Daytona USA -- SFX ROM
                           "Daytona USA SFX ROM": [186, 187, 188, 189, 190, 191],
        }
        # Outdated - its way easier to look by sample indexes
        # exceptions = [1108552, 1044293, 1044543, 1044793, 1045043, 1044293,  # Start addresses
        #               1044543, 1044793, 1045043, 989449,  2079581, 1774376,  # Of Daytona USA Sample Bank.
        #               2092319, 2092794, 2984319, 3134206,
        #
        #               3587684, 3593147, 3618391, 3626012, 3631363, 3650594, 3658946,  # Of Daytona USA SFX Bank.
        #               3662765, 3667582, 3687181, 3713956, 3719234, 3722569, 3736746,
        #               3750973, 3763351, 3794300, 3809765, 3814375, 3825918, 3837560,
        #               3847270, 3864821, 3867926, 3871047, 3875476, 3878901, 3883890,
        #               3900099, 3919428, 3924147, 3935739, 3948749, 3985033, 3991284,
        #               3994523, 3999388, 4003012, 4041263, 4060202, 4069197, 4079608,
        #               4087180, 4090924, 4102861, 4125797, 4151011, 4169490,
        #               ]
        me.extract_samples(out_loc, log_name, bank, bank2, bankswitchtype)

    def main_loop(me, raw, bank, idx_uint32_t=1, sample_id=1, it_data_len=0,
                  out_loc="", log_name="", bankswitchtype=0, datatype="m", bank_name=""):
        """
        Main loop of legacy extractor.
        """
        # This thing needs to be supplied most of the data from the main func
        # Setups
        check = 0
        logged_1 = False
        logged_2 = False
        addr = 0
        # data_start_append = 0
        if not it_data_len:
            print("lmao what")
        try: garbage = me.garbage_indexes[bank_name]
        except KeyError: garbage = []
        # The only part of code that is here from MAME
        while addr < it_data_len:
            addr = idx_uint32_t * 12
            (data_start, data_format, data_loop,
             data_len,   data_atk,    data_de1,
             data_de2,   data_del,    data_rel,
             data_ksr,   data_vib,    data_amd,
             data_lfs                          ) = get_sample_data(raw[addr:addr+12], "m")
            temp_data_start = data_start
            data_types = {0: "8-bit", 1: "12-bit", 3: "16-bit (OPL4 only)", 4: "Prohibited"}
            pcm_type = data_types[data_format]

            if pcm_type == data_types[1]:
                print("dies")

            if sample_id in garbage:
                print(f'Skipped sample {idx_uint32_t}.')
                with open(f"./samples/{log_name}_log.txt", "a") as log:
                    log.write(f"#################################\n"
                              f"Sample {sample_id} skipped.\n"
                              f"Address {data_start} isn't proper\n\n")
                    log.close()
                idx_uint32_t += 1
                sample_id += 1
                continue
            if bankswitchtype == 1:

                if temp_data_start == 1048576:
                    print("Check")
                    check += 1
                    sleep(0.5)

                if check == 2:
                    data_start += 1048576
                    if not logged_1:
                        with open(f"./samples/{log_name}_log.txt", "a") as log:
                            log.write(f"#################################\n\n"
                                      f"-+-+-==== BANKSWITCHING ====-+-+-\n\n"
                                      f"#################################\n\n")
                            log.close()
                        logged_1 = True
                if check == 3:
                    data_start += 2097152
                    if not logged_2:
                        with open(f"./samples/{log_name}_log.txt", "a") as log:
                            log.write(f"#################################\n\n"
                                      f"-+-+-==== BANKSWITCHING ====-+-+-\n\n"
                                      f"#################################\n\n")
                            log.close()
                        logged_2 = True

            deeta = raw[data_start:(data_start + data_len)]
            unnecessary = check_bytes(bank, 0xFF)

            if True:
                print(f"{sample_id} @ {data_start}")

            if data_start >= unnecessary or data_len >= unnecessary:
                print("Avoiding unnecessary samples")
                break
            if deeta == b'':
                print('No data.')
                break
            with open(f"./samples/{log_name}_log.txt", "a") as log:
                log.write(f"#################################\n\n"
                          f"Sample {sample_id}:\n"
                          f"Inst def address:     {addr}\n"
                          f"Start offset in ROM:  {data_start}\n"
                          f"End offset in ROM:    {data_len + data_start}\n"
                          f"Length:               {data_len}\n"
                          f"Loop start:           {data_loop}\n"
                          f"Sample type:          {pcm_type}\n"
                          f"Inst AR:              {data_atk}\n"
                          f"Inst D1:              {data_de1}\n"
                          f"Inst D2:              {data_de2}\n"
                          f"Inst DL:              {data_del}\n"
                          f"Inst RR:              {data_rel}\n"
                          f"Inst RC:              {data_ksr}\n"
                          f"Inst VD:              {data_vib}\n"
                          f"Inst AD:              {data_amd}\n"
                          f"Inst LS:              {data_lfs}\n")
                if data_format:
                    log.write(f"Data saved as raw file.\n\n")
                else:
                    log.write(f"\n")
                log.close()
            if not data_format:
                print(f'Sample {idx_uint32_t} logged. {pcm_type}.')
            else:
                print(f'Sample {idx_uint32_t} logged. {pcm_type}. Saved as raw data.')
            idx_uint32_t += 1
            if not data_format:
                new_deeta = []
                for ini in deeta:
                    new_deeta.append(ini + 128 & 0xff)
                new_deeta = bytearray(new_deeta)
                save_riff(location=f'./samples/{out_loc}/sample_{sample_id}.wav', rate=44100, bdep=8, data=new_deeta,
                          loop_start=data_loop, loop_end=data_len)

            else:
                with open(f'./samples/{out_loc}/sample_{sample_id}.raw', 'wb') as fl:
                    fl.write(deeta)
                    fl.close()
            sample_id += 1
        return None

    def extract_samples(me, out_loc, log_name, bank, bank2=None, bankswitchtype=0) -> None:
        """
        Legacy extractor setup function.
        """
        # Bankswitch types:
        # 0: Generic/None (Most likely what OPL4 uses)
        # 1: Daytona-like MultiPCM Games
        # 2: Yet-to-be-implemented OutRunners bankswitching mode (there probably is       -- PRETEND THIS IS
        #                                                         none going on, but      -- STRIKETHROUGH TEXT
        #                                                         what do I know, right?) -- ITS WRONG
        # Actually there is some. Welp.

        try:
            raw = open(f"{bank}", "rb").read()
            if bank2 != None:
                try:
                    raw += open(f"{bank2}","rb").read()
                except FileNotFoundError:
                    print("Invalid or missing bank 2 path")
            try:
                open(f'./samples/{out_loc}/test.test', 'wb')
            except FileNotFoundError:
                mkdir(f"./samples/{out_loc}")
        except FileNotFoundError:
            print("No such file.")
            quit()
        s(1)
        idx_uint32_t = 1
        addr = 0
        sample_id = 1
        # open log file and write base data
        with open(f"./samples/{log_name}_log.txt", "w") as log:
            log.write(f"Log Start\n\n")
            log.close()


        print(f"File MD5: {ret_hash(raw, 'md5')}")
        if ret_hash(raw, "md5") in me.hashes:
            print(f"This is most likely to be {me.hashes[str(ret_hash(raw, 'md5'))][2:]}, will use automatic options:\n"
                  f"[datatype=\"{me.hashes[str(ret_hash(raw, 'md5'))][0]}\", "
                  f"bankswitchtype={me.hashes[str(ret_hash(raw, 'md5'))][1]}]")
            bankswitchtype=int(me.hashes[str(ret_hash(raw, 'md5'))][1])
            bank__name = me.hashes[str(ret_hash(raw, 'md5'))][2:]
        else:
            print("Cannot determine ROM")
            bank__name = ""
        sleep(2)
        print(bankswitchtype)
        print(len(raw))
        addr = 0
        it_data_len = int(0x10000 - ((raw[1] << 16) & 0x3F | (raw[2] << 8) | raw[3]))
        print(f'Skipping Instrument Table. Length: {it_data_len}.')
        with open(f"./samples/{log_name}_log.txt", "a") as log:
            log.write(f"#################################\n\n"
                      f"Instrument Table skipped.\n"
                      f"Length: {it_data_len}\n\n")
            log.close()
        sample_id += 1
        idx_uint32_t += 1

        if bank.lower in ["yrw801.bin", "yrw801.raw", "yrw801", "opl4.bin", "opl4.raw", "opl4"]:
            # print("OPL4, not implemented yet")
            # with open(f"./samples/{log_name}_log.txt", "a") as log:
            #     log.write(f"#################################\n\n"
            #               f"Log end due to OPL4 format.\n")
            #     log.close()
            pass
        else:
            me.main_loop(raw,bank,idx_uint32_t, sample_id, it_data_len, out_loc, log_name, bankswitchtype, bank, bank__name)

        with open(f"./samples/{log_name}_log.txt", "a") as log:
            log.write(f'----++++===## SUMMARY ##===++++----\n\n'
                      f'Length: {len(raw)}\n'
                      f'Total samples: {sample_id}\n\n'
                      f'----++++===## # ### # ##===++++----')
            log.close()

class MultiPCMSampleExtractor:
    """
    New extractor, now as a class instead of random ass functions.
    """
    def __init__(me,
                 out_loc:         str = "samples",  # the output folder. always placed inside "./samples" one.
                 log_name:        str = "log",        # the name of the log within the "./samples" folder.
                 bank1:           str = None,         # path to bank 1, for stitching. when None, uses bank2.
                 bank2:           str = None,         # path to bank 2, for stitching. can be omitted.
                 debug:           bool = False,       # wait for a keystroke to proceed, after every instrument
                 chip_type:       str = "multipcm_c", # the chip type, affects sample type detection algorithm.
                                                      # can be: "opl4", "multipcm", "7gew" --
                                                      # (due to how get_instrument_data() works). case insensetive.
                 bankswitch_type: str = "m",          # left for legacy reasons.
                 clock_rate: int = 8053975,           # chip rate.
                                                      # should really not be filled out
                                                      # unless the rate is different
                                                      # 33868800 for OPL4, 9878400 for MPCM, 8000000 for GEW7, ~9400000 for MU5
                                                      # (to result in 44100hz)
                 divider: int = 8,                    # clock divider. 32 is the one for OPL4, 8 for MPCM, GEW7
                 chans: int = 28,                     # channels. 24 for OPL4, 28 for MPCM, GEW7
                 only_log: bool | int = False,        # whether to only log instruments instead of also dumping their samples
                 chip_settings = None,
                 ):
        me.out_loc = out_loc
        me.log_name = log_name
        me.bank1 = bank1
        me.bank2 = bank2
        me.bankswitch_type = bankswitch_type
        me.chip_type = chip_type.lower()
        me.only_log = only_log
        match me.chip_type:
            case "multipcm":
                me.formats = {
                    0: 8,          # 0b00
                    1: 12,         # 0b01
                    2: -1,         #
                    3: -1,         #
                }
                me.rate = 35955
                # OpenMSX(?) OPL4 PCM Emulation says that 0b01 is the "Prohibited" of MultiPCM.
                # the question is, is that it? or is that the OPL4 way?
            case "opl4":
                me.formats = {
                    0: 8,   # 0b00
                    1: 12,  # 0b01
                    2: 16,  # 0b10
                    3: 16,  # 0b11
                }
                me.rate = 44100 # OPL4: 
            case _:
                me.formats = {
                    0: 8,   # 0b00
                    1: 12,  # 0b01
                    2: 16,  # 0b10
                    3: 16,  # 0b11
                }
                me.rate = chip_settings[0] / (chip_settings[1] * chip_settings[2]) if chip_settings and len(chip_settings) == 3 else clock_rate / (divider * chans) 
        me.debug = debug
        match (bank1, bank2):
            case (None, _):
                print('Bank 2 not none')
                try:
                    me.bank = open(bank2, 'rb').read()
                    if test_file(f"./samples/{out_loc}"):
                        pass
                    else:
                        try: mkdir(f"./samples")
                        except: pass
                        mkdir(f"./samples/{out_loc}")
                except FileNotFoundError:
                    print('File does not exist.')
                    return
            case (_, None):
                print('Bank 1 not none')
                me.bank = open(bank1, 'rb').read()
                try:
                    me.bank = open(bank1, 'rb').read()
                    # print(f"? {me.bank}") # debug
                    if test_file(f"./samples/{out_loc}"):
                        pass
                    else:
                        try: mkdir(f"./samples")
                        except: pass
                        mkdir(f"./samples/{out_loc}")
                except FileNotFoundError:
                    print('File does not exist.')
                    return
            case (_, _):
                print('Stitching')
                try:
                    me.bank = open(bank1, 'rb').read() + open(bank2, 'rb').read()
                    if test_file(f"./samples/{out_loc}"):
                        pass
                    else:
                        mkdir(f"./samples/{out_loc}")
                except FileNotFoundError:
                    print('File does not exist.')
                    return
            case (None, None):
                me.bank = b''
                print('Nothing to extract from')
                return
            case _:
                me.bank = b''
                return
        me.instrument_table = me.bank[
                                get_sample_data(me.bank[:12])[1]:
                                get_sample_data(me.bank[:12])[1] + get_sample_data(me.bank[:12])[3]
                                ]
        try:
            me.log = open(f'./samples/{log_name}.txt', 'x')
        except FileExistsError:
            me.log = open(f'./samples/{log_name}.txt', 'w')

        me.known_roms_legacy = {  # md5 hashes of full roms, not usable for ones stitched from vgms
            '6ccd6376e416a56f92b21368fd14d9df': "0Virtua Cop Sample ROM",
            '6e1d01e270bad869ab8c1869481033de': "1Virtua Cop SFX ROM",
            '00fafc26797c95f104bee47b5784929d': "2Daytona USA Sample ROM",
            '1d99c9ac716500586f19c5e4dd4bb4b0': "3Daytona USA SFX ROM",
            '42af93619160ef2116416f74a6cb12f2': "4OPL4 YRW801",
            'bb2262db75e5c1bdf982c95cf0ff278f': "5OutRunners Sample ROM",
            'ad8d254e9d2637b5824a2b44504bd023': "6Virtua Racing Sample ROM 1",
            '48c472241ad7c280f930a9c59b216274': "7Virtua Racing Sample ROM 2",
        }
        me.known_roms = {  # md5 hashes of rom instrument tables
            'bfc869e4e6009bbbbde9857e0d4602ab': "0_Virtua Cop Sample ROM",
            'dd165c69654084f0dfaaf01b4806a8a9': "1_Virtua Cop SFX ROM",
            'b0996ee23be61a1db77d5bbb82791316': "2_Daytona USA Sample ROM",
            '52c10680b0be2ef357d9f4b90d4ae5ca': "3_Daytona USA SFX ROM",
            '3dcbfe07d62693b7d8bf92fa3777427e': "4_OPL4 YRW801",
            '3ae69910e4efdc398c9ae956f985ef73': "5_OutRunners Sample ROM",
            '75c53fdc5ac0297e4e0947b7467935bd': "6_Virtua Racing Sample ROM 1",
            'f5367cb72a6f8a81933cf6f27dd793fb': "7_Virtua Racing Sample ROM 2",
            '865b509bae66b74e02728387f6b7b6fc': "8_Desert Tank Sample ROM",
            '0c5c205b45495038ba428c647011cda2': "9_Desert Tank SFX ROM",
            'fd2878a379f8368386c3b82eab04f32e': "100_Yamaha MU5 Wave ROM",
        }
        if hash := ret_hash(me.bank[
            get_sample_data(me.bank)[1]:
            get_sample_data(me.bank)[1] + get_sample_data(me.bank)[3]]
        ):
            print(f"Hash: {hash}\n"
                  "Detected ROM: ", end='')
            if hash in me.known_roms:
                match int(me.known_roms[hash].split("_")[0]):
                    case 0: me.set_rom_params(82, [], [])
                    case 1: me.set_rom_params(207, [range(111, 158), range(158, 207)], [])
                    case 2:
                        me.set_rom_params(198, [range(93, 138), range(138, 65535)],
                                           [139,
                                            142, 145,
                                            150, 151, 152, 153, 154, 156, 159,
                                            161, 163, 164,
                                            198, 199,
                                            200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
                                            210, 211, 212, 213]
                                           )
                    case 3: me.set_rom_params(185, [range(87, 139), range(139, 65535)], [])
                    case 4: me.set_rom_params(); me.chip_type = "opl4" # untested
                    case 5: me.set_rom_params() # untested
                    case 6: me.set_rom_params(bad_samples=[14]) # untested
                    case 7: me.set_rom_params() # untested
                    case 8: me.set_rom_params(251, [range(127, 189), range(189, 65536)], [range(53, 63), 100, range(101, 127), range(157, 189)])
                    case 9: me.set_rom_params(206, [range(127, 175), range(175, 65536)], [range(54, 63), 100, range(118, 127), range(172, 175)])
                    case 100: me.set_rom_params(512, [],
                                               [488, 489,
                                                490, 491, 492, 493, 494, 495, 496, 497, 498,
                                                500, 502,
                                                510, 511
                                               ]
                                               )
                    case _: me.set_rom_params() # any other rom

                print(me.known_roms[hash].split("_")[1] if hash in me.known_roms else "Unidentified ROM")
                me.log.write(f"ROM hash: {hash}\n"
                               f"Detected ROM: {me.known_roms[hash].split('_')[1] if hash in me.known_roms else 'Unidentified ROM'}\n")
            else:
                me.set_rom_params()
                me.log.write(f"ROM hash: {hash}\n"
                               f"Detected ROM: {me.known_roms[hash].split('_')[1] if hash in me.known_roms else 'Unidentified ROM'}\n")
                print("Unidentified ROM")
        s(2)  # wait 2 secs
        me.extract()

    def set_rom_params(me, samples=None, switch_ranges=None, bad_samples=None):
        me.samples = samples if samples else len(me.instrument_table) // 12
        me.switch_ranges = switch_ranges if switch_ranges else []
        me.bad_samples = []
        if bad_samples:
            for val in bad_samples:  # populate the list with ranges also.
                if isinstance(val, (range, list, tuple)):
                    me.bad_samples.extend(list(val))
                elif isinstance(val, int):
                    me.bad_samples.append(val)
                else:
                    log(f"Uh oh, an unsupported value type! {type(val)}")
                    pass

    def check_ranges(me, iter: int = 0) -> int:
        """
        purpose: checking for bankswitch ranges and returning 1048576 << bank, else 0
        """
        for i in range(len(me.switch_ranges)):
            if iter in me.switch_ranges[i]:
                return 1048576 << i
        return 0

    def calculate_params(
            me,
            type: str = "none",
            param1: int = 0,
            param2: int = 0,
            param3: int = 0, # reserved
            param4: int = 0  # reserved
    ) -> str | bi.float | int:
        """
        returns parameter values
        """
        vib_strengths = [0, 3.376,
                         5.065, 6.75,
                         10.114, 20.17,
                         40.108, 79.307]
        am_strengths = [0, 1.781,
                        2.906, 3.656,
                        4.406, 5.906,
                        7.406, 11.91]
        lfo_speeds = [0.168, 2.019,
                      3.196, 4.206,
                      5.215, 5.888,
                      6.224, 7.056]
        sustains = [0, 3, 6, 9,
                    12, 15, 18, 21,
                    24, 27, 30, 33,
                    36, 39, 42, 93]

        attacks = [float("inf"), float("inf"), float("inf"), float("inf"),
                   6222.95, 4978.37, 4148.66, 3556.011,
                   3111.47, 2489.21, 2074.33, 1778,
                   1555.74, 1244.63, 1037.19,  889.02,
                    777.87,  622.31,  518.59,  444.54,
                    388.93,  311.16,  259.32,  222.27,
                    194.47,  155.6,   129.66,  111.16,
                     97.23,   77.82,   64.85,   55.6,
                     48.62,   38.91,   32.43,   27.8,
                     24.31,   19.46,   16.24,   13.92,
                     12.15,    9.75,    8.12,    6.98,
                      6.08,    4.9,     4.08,    3.49,
                      3.04,    2.49,    2.13,    1.9,
                      1.72,    1.41,    1.18,    1.04,
                       .91,     .73,     .59,     .5,
                       .45,     .45,     .45,    0,
        ]
        decays = [float("inf"), float("inf"), float("inf"), float("inf"),
                  89164.63, 71331.75, 59443.13, 50951.25,
                  44582.31, 35665.9,  29721.59, 25475.65,
                  22291.16, 17832.97, 14860.82, 12737.82,
                  11145.58,  8916.51,  7430.43,  6368.93,
                   5572.79,  4458.28,  3715.24,  3184.49,
                   2786.39,  2229.16,  1857.64,  1592.24,
                   1393.2,   1114.6,    928.84,   796.15,
                    696.6,    557.32,   464.44,   398.1,
                    348.3,    278.68,   232.24,   199.05,
                    174.15,   139.37,   116.15,    99.55,
                     87.07,    69.71,    58.1,     49.8,
                     43.54,    34.83,    29.02,    24.9,
                     21.77,    17.41,    14.51,    12.43,
                     10.08,     8.71,     7.23,     6.21,
                      5.44,     5.44,     5.44,     5.44,
        ]
        match type.lower():
            case "vib":
                return (vib_strengths[param1] / 44100) * me.rate \
                        if me.rate != 44100 else vib_strengths[param1]
            case "am":
                return (am_strengths[param1] / 44100) * me.rate \
                        if me.rate != 44100 else am_strengths[param1]
            case "lfo":
                return (lfo_speeds[param1] / 44100) * me.rate \
                        if me.rate != 44100 else lfo_speeds[param1]
            case "sus":
                return sustains[param1]
            case "atk":
                match param1:
                    case 0:
                        return '∞'
                    case 15:
                        return attacks[63]
                    case _:
                        return (attacks[clamp(param1 + param2, 0, 63)] / 44100) * me.rate \
                                if me.rate != 44100 else attacks[clamp(param1 + param2, 0, 63)]
            case "dec":
                match param1:
                    case 0:
                        return '∞'
                    case 15:
                        return decays[63]
                    case _:
                        return (decays[clamp(param1 + param2, 0, 63)] / 44100) * me.rate \
                                if me.rate != 44100 else attacks[clamp(param1 + param2, 0, 63)]
            case _:
                return "Placeholder"

    def actually_save_samples(me, iter: int = 0, NUMPY: bool = False, only_log: bool | int = False) -> None:
        """
        This function takes in a sample index, fetches the data from instrument table and then fetches the sample itself from the data.
        """
        if iter in me.bad_samples:
            print(f"Sample {iter} is garbage, skipping")
            me.log.write(
                f'##############################################\n'
                f'Instrument {iter} skipped\n'
                f'\n'
            )
            return None
        current_instrument = list(get_sample_data(me.bank[(iter * 12) + 12:(iter * 12) + 24], me.chip_type))
        current_instrument[0] += me.check_ranges(iter)
        if me.debug:
            print(f"Current Instrument: {iter}\n"
                  f"Sample start:          {current_instrument[0]}\n"
                  f"Sample length:         {current_instrument[3]}\n"
                  f'Sample bytelength:     {(current_instrument[3] * 3 / 2) if me.formats.get(current_instrument[1], -1) == 12 else (current_instrument[3] * 2) if me.formats.get(current_instrument[1], -1) == 16 else current_instrument[3]}\n'
                  f"Sample loop start:     {current_instrument[2]}\n"
                  f"Sample format:         {current_instrument[1]}, {me.formats[current_instrument[1]] if current_instrument[1] in me.formats else 'Invalid'}\n"
                  f"AD1D2SR:               {current_instrument[4]}/{current_instrument[5]}/{current_instrument[6]}/{current_instrument[7]}/{current_instrument[8]}\n"
                  f'Rate scaling:          {current_instrument[9]}\n'
                  f'Vibrato & AM strength: {current_instrument[10]}/{current_instrument[11]}\n'
                  f'LFO Speed:             {current_instrument[12]}\n'
                  f'\n'
                  )
            print(f"length in-place calculation: {ceil((current_instrument[3]*3)/2)}")
            input()
        data = list(me.bank[current_instrument[0]:current_instrument[0] + current_instrument[3]])
        if len(data) == 0 or int(min(data)) == int(max(data)):
            print("Sample empty, skipping")
            me.log.write(
                f'##############################################\n'
                f'Instrument {iter} is empty\n'
                f'\n'
            )
            return
        if only_log: return
        match (me.formats[current_instrument[1]] if current_instrument[1] in me.formats else "invalid"):  # pcm format
            case 8:
                if NUMPY:
                    data_ready = (np.array(data, np.uint8) + 128) & 255
                else:
                    data_ready = [(val + 128) & 255 for val in data]
                with WaveWriter(channels=1,
                                samplerate=44100,
                                bitdepth=8,
                                data=list(data_ready)
                                ) as Wave:
                    Wave.set_smpl_chunk(sample_loop_count=1,
                                    loop_types=[0],
                                    loop_starts=[current_instrument[2] - 1],
                                    loop_ends=[current_instrument[3] - 1])
                    Wave.write_file(f"./samples/{me.out_loc}/sample_{iter}_8bit.wav")
                # save_riff(
                #     data=data_ready,
                #     rate=44100,
                #     bdep=8,
                #     location=f'./samples/{me.out_loc}/sample_{iter}.wav',
                #     loop_start=current_instrument[2],
                # )
            case 12:
                # comment text
                print("converting 12 bit...")
                data12 = convert_12_to_16(me.bank[current_instrument[0]:ceil((current_instrument[0] + (current_instrument[3]*3)/2))])
                with WaveWriter(
                        channels=1,
                        samplerate=44100,
                        bitdepth=16,
                        data=data12
                        ) as Wave:
                    Wave.set_smpl_chunk(
                        sample_loop_count=1,
                        loop_types=[0],
                        loop_starts=[current_instrument[2] - 1],
                        loop_ends=[len(data12) - 1]
                        )
                    Wave.write_file(f"./samples/{me.out_loc}/sample_{iter}_12bit.wav")
                print("done")
                #print("12 bit sample detected, skipping for now.")
            case 16:
                with WaveWriter(
                        channels=1,
                        samplerate=44100,
                        bitdepth=16,
                        data=data
                        ) as Wave:
                    Wave.set_smpl_chunk(
                        sample_loop_count=1,
                        loop_types=[0],
                        loop_starts=[current_instrument[2] - 1],
                        loop_ends=[current_instrument[3] - 1]
                        )
                    Wave.write_file(f"./samples/{me.out_loc}/sample_{iter}_16bit.wav")
                # save_riff(
                #     data=me.bank[current_instrument[1]:current_instrument[1] + current_instrument[3]],
                #     rate=44100,
                #     bdep=16,
                #     location=f'./samples/{me.out_loc}/sample_{iter}.wav'
                # )

        # have to precalculate those since cant do inplace
        atk = round(me.calculate_params("atk", current_instrument[4], current_instrument[9]), 4) \
            if type(me.calculate_params("atk", current_instrument[4], current_instrument[9])) in [int, float] \
            else me.calculate_params("atk", current_instrument[4], current_instrument[9])
        d1r = round(me.calculate_params("dec", current_instrument[5], current_instrument[9]), 4) \
            if type(me.calculate_params("dec", current_instrument[5], current_instrument[9])) in [int, float] \
            else me.calculate_params("dec", current_instrument[5], current_instrument[9])
        d2r = round(me.calculate_params("dec", current_instrument[6], current_instrument[9]), 4) \
            if type(me.calculate_params("dec", current_instrument[6], current_instrument[9])) in [int, float] \
            else me.calculate_params("dec", current_instrument[6], current_instrument[9])
        rel = round(me.calculate_params("dec", current_instrument[8], current_instrument[9]), 4) \
            if type(me.calculate_params("dec", current_instrument[8], current_instrument[9])) in [int, float] \
            else me.calculate_params("dec", current_instrument[8], current_instrument[9])

        me.log.write(
            f'##############################################\n'
            f'Instrument {iter}\n'
            f'\n'
            f'Start address in bank: {current_instrument[0]}\n'
            f'Sample length:         {current_instrument[3]}\n'
            f'Sample bytelength:     {(current_instrument[3] * 3 / 2) if me.formats.get(current_instrument[1], -1) == 12 else (current_instrument[3] * 2) if me.formats.get(current_instrument[1], -1) == 16 else current_instrument[3]}\n'
            f'Sample loop start:     {current_instrument[2]}\n'
            f'Sample format:         {me.formats.get(current_instrument[1], "Invalid")}-bit ({current_instrument[1]})\n'
            f'INSTRUMENT SETTINGS:\n'
            f'Attack Rate:           {current_instrument[4]} | {atk}ms\n'
            f'Decay 1 Rate:          {current_instrument[5]} | {d1r}ms\n'
            f'Decay 2 Rate:          {current_instrument[6]} | {d2r}ms\n'
            f'Sustain Level:         {current_instrument[7]} | {me.calculate_params("sus", current_instrument[7])}dB\n'   # ∞
            f'Release Rate:          {current_instrument[8]} | {rel}ms\n'
            f'Rate correction:       {current_instrument[9]}\n'
            f'Vibrato strength:      {current_instrument[10]} | {me.calculate_params("vib", current_instrument[10])} cents\n'
            f'AM strength:           {current_instrument[11]} | {me.calculate_params("am", current_instrument[11])}dB\n'
            f'LFO Speed:             {current_instrument[12]} | {round(me.calculate_params("lfo", current_instrument[12]), 4)}Hz\n'
            f'\n'
        )
        return None

    def extract(me) -> None:  # optimized version
        """
        The function that continuously calls the extractor itself and passes it the iteration.
        """
        # kill me please
        me.log.write(
            f'!!NOTE!! Rates take rate correction into account.\n\n'
        )
        for _ in range(me.samples):
            print(f"Current sample: {_}")
            me.actually_save_samples(_, NUMPY, me.only_log)
        return None

if __name__ == "__main__":
    if nt:
        path = "E:/D Drive (HDD)/PycharmProjects/BananaBot/mpt2fur/rom stuff/roms"
    elif posix:
        path = "../../mpcm"
    else:
        path = "."
    print(f"{path}/roms/desert_samplerom.raw")
    MultiPCMSampleExtractor(
        out_loc="mu5_test",
        log_name="mu5_test_log",
        chip_settings = CHIP_SETTINGS["mu5"],
        bank1=r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\MAME\roms\mu5\yamaha_mu5_waverom_xp50280-801.bin",
        debug=0
        )

# ps да, мне платят за количество строк