
# system vars
SysEx_begin = "0xF0 0x41 0x10 0x45 0x12 [ 0x10 0x1 0x0 "
SysEx_data = ""
SysEx_end = " ] F7h"

# checksum calculation for OOB testing,
# so I don't die later rewriting this 2 times
def checksum(_):
    __ = 0                              # underscore core
    for ___ in range(len(_)):
        __ += (__ + _[___]) & 0b1111111
    __ = __ % 128
    return 128 - __
# construction of exclusive messages.
def construct_exclusive(_):             # underscore core part 2
    ___ = ''
    ____ = ''
    ______ = list(range(5 + 64 + 3 + 1 + 1))
    ______[0] = 0x00
    ______[1] = 0x00
    ______[2] = 0x00
    ______[3] = 0x00
    ______[4] = 0x00
    ______[5] = 0x10
    ______[6] = 0x01
    ______[7] = 0x00
    ______[72] = 0
    ______[73] = 0x00
    _______ = 3
    for __ in range(len(_)):
        ______[_______] = _[__]
        _______ += 1
        ___ += f"{hex(_[__])} "
        if (_[__] % 4) == 0:
            ____ += "\n"
        else:
            ____ += " "
        ____ += f"{bin(_[__])}"
    ______[67] = checksum(______)
    ______[0] = 0xF0
    ______[1] = 0x41
    ______[2] = 0x10
    ______[3] = 0x45
    ______[4] = 0x12
    ______[73] = 0x7F
    _____ = "0xF0 0x41 0x10 0x45 0x12 [ 0x10 0x1 0x0 " + ___ + "] 0xF7"
    return ((f"Output SysEx: \n"                                     
            f"{_____}\n"), ______)
    # f"Output Binary:\n"
    # f"{____}")
    # if str(input("Copy to clipboard? [y/n]\n")).lower() in ans:
mode = 0
yes = ["y", "ye", "yes", "д", "да", "1"]
no = ["n", "no", "nah", "н", "не", "нет", "0"]
masks = [0b01111, 0b10111, 0b11011, 0b11101, 0b11110]
rows_bin = ""
rows = ["h", "h", "h", "h", "h", "h", "h", "h", "h", "h", "h", "h", "h", "h", "h", "h"]
empty = ["\x20", "_", "-", "0"]
inputs_amount = 0
quick = "-1"    # quick mode, all rows have same data. Perfect for some kind of bar patterns
to_test = "-1"  # whether to test the constructed SysEx

# this is where we read the data from
# to construct out 5 light years long
# SysEx message
LED_Diodes = list(range(64))
for _ in range(len(LED_Diodes)):
    LED_Diodes[_] = 31

# just in case we STILL somehow end up in mode 2 (image to SysEx)
pygame_available = -1

# some text jjoj
print("Roland SC-55 Dot Display Image SysEx Generator")
print("Symbols considered as emptiness: ' ', '_', '-', '0'")

# complete bullshit import statements
# there's like 99% chance you can do something better
try:
    import pygame.image, pygame.surface
    # import pygame.midi
    # pygame.midi.init()

    # pygame.scrap can basically be ignored for now I have to find
    # another clipboard library, since scrap requires a window
    # to be initialized to operate
    # try:
    #     pygame.scrap.init()
    # except pygame.error:
    #     print("SCRAP pygame module unavailable, cannot use clipboard.")

    # this bad code, it is responsible for handling MIDI device stuff
    # it should be ignored as it just breaks when it comes to testing SysEx after converting
    # I HAVE NO IDEA WHY DO THE ERRORS EVEN HAPPEN HELP :sob:
    # print(f"MIDI Devices ({pygame.midi.get_count()} available): ")
    # for _devices_ in range(0, pygame.midi.get_count()):
    #     device = pygame.midi.get_device_info(_devices_)
    #     if device[2]:
    #       continue   # skip over if the device is an input one
    #     inputs_amount += 1  # counting output devices to later make a list of them with the same For loop
    #     device_name = ''
    #     for _ in range(len(pygame.midi.get_device_info(_devices_)[1])):         # why do I have to go through this much
    #         device_name += chr(pygame.midi.get_device_info(_devices_)[1][_])    # pain just to remove the ugly b'' from
    #     print(f"{_devices_}. {device_name}")  # it slows my code the hell down  # from devices' names ;-;
    # print("NOTE: only output devices are displayed! Not every single one!")
    #
    # _in_ = -2                                # so the while loop loops™
    # inputs = list(range(inputs_amount + 1))  # the list we earlier talked about to be made later™
    # _crs_ = 0                                # so we write to correct array indexes™
    # inputs[len(inputs) - 1] = -1             # so we can select not to output™
    #
    # for _devices_ in range(0, pygame.midi.get_count()):   # the ugly loop from before
    #     device = pygame.midi.get_device_info(_devices_)
    #     if device[2]:
    #       continue
    #     if device[3]:
    #         inputs[_crs_] = _devices_
    #         _crs_ += 1
    #
    # # help
    # while _in_ not in inputs:
    #     _in_ = int(input("Select MIDI port to output test SysEx data to. Use '-1' to not use any. "))
    #     if _in_ != -1 and _in_ in inputs:
    #         #  | | | | | |   this long string is just to display "SC" on the SC-xx's
    #         # \/\/\/\/\/\/   (I'll add SC-88's double display support later) display
    #         pygame.midi.Output(_in_).write_sys_ex(0, b'\xf0\x41\x10\x45\x12\x10\x01\x00\x00\x00\x00\x03\x06\x04\x04\x07\x01\x00\x04\x06\x07\x00\x00\x00\x00\x00\x00\x18\x19\t\x01\x01\x19\t\t\x19\x10\x00\x00\x00\x00\x00\x00\x1c\x16\x02\x00\x00\x00\x00\x02\x16\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4d\xf7')
    #         print(f"Opening device #{_in_}...")
    #     if _in_ != 1 and not _in_ in inputs:
    #         print("Not a MIDI out device!")
    # # we don't want to test out system exclusive messages straight out the box,
    # # we want to use Domino MIDI Editor©®™ or Sekaiju©®™ to test them in action later
    # if _in_ == -1:
    #     print("Skipping MIDI")
    #     pygame.midi.quit()     # just in case

    print("Pick a mode:\n"
          "1. String by hand\n"
          "2. Image as a source *\n"
          "* Image must be 16x16 (if larger one submitted, only top left 16x16 area will be read),\n"
          "the image is palettized. Whatever color has the RGB value of #000000 will be turned on, off otherwise.\n")
    pygame_available = True
except ImportError:
    print("Pygame not found, image conversion is unavailable.")
    pygame_available = False  # just in case...
    mode = 1

# setups
# -- none for now (or ever)

# I *do* plan to later add spritesheet support for
# animation sequences.
while mode not in [1, 2, 3]:
    try:
        mode = int(input())
    except TypeError:
        print("Not a number.")
    if mode not in [1, 2, 3]:
        print("Not a mode.")

if mode == 1:

    while quick.lower() not in yes and quick.lower() not in no:
        quick = str(input("Do you wish to use quick mode? (All rows will have same data) [y/n]\n")).lower()
        if quick not in yes and quick not in no:
            print("Not a valid answer.")

    if quick.lower() in yes:
        t = str(input("all   - row data -\n"))
        for i in range(16):
            rows[i] = t

    # by this time I probably spent more time writing this
    # small program than I would probably have taken to
    # manually program the damn sliding "DOOM" animation
    # with calculator.

    else:
        rows[0]  = str(input("Row 01: "))
        rows[1]  = str(input("Row 02: "))
        rows[2]  = str(input("Row 03: "))
        rows[3]  = str(input("Row 04: "))
        rows[4]  = str(input("Row 05: "))
        rows[5]  = str(input("Row 06: "))
        rows[6]  = str(input("Row 07: "))
        rows[7]  = str(input("Row 08: "))
        rows[8]  = str(input("Row 09: "))
        rows[9]  = str(input("Row 10: "))
        rows[10] = str(input("Row 11: "))
        rows[11] = str(input("Row 12: "))
        rows[12] = str(input("Row 13: "))
        rows[13] = str(input("Row 14: "))
        rows[14] = str(input("Row 15: "))
        rows[15] = str(input("Row 16: "))

    # a failsafe for if a string is <16 in length
    for _ in range(16):
        if len(rows[_]) < 15:
            print(f"row {_} is shorter than 16 symbols ({len(rows[_])})")
            for __ in range(16 - len(rows[_])):
                rows[_] += " "
        else:
            print(f"row {_} is 16 symbols long")

    # Roland Sound Canvas LCD looks like this:
    # #####|#####|#####|#          the | are separators
    #                              the display is divided into LED chunks 5 long each.
    #                              last chunk contains only a single LED.
    # a for loop does this:
    # assuming we have all rows contain data "0123456789ABCDEF":
    # it first scans characters 0:5 (0 through 4), reading "01234" from the string.
    # since 0 is considered LED off, it will mask it off, everything else remains.
    # as a result, we have 0b01111 as output.
    # advance, 5:10, '56789', no masking, 0b11111
    # advance, 10:15, no masking, 0b11111.                 NOTE: The loop reads every row before
    # last symbol, no masking, 0b11111.                    it advances to next chunk, since that's
    # and that is for every row.                                          how the LCD is arranged.

    # all the commented out stuff is debug stuff that I used to fix the code breaking
    # pain
    for _chunks_ in range(4):                                             # for 4 chunks...
        base_pos = (_chunks_ * 16)                                        # ...we get base position into the array
        # print(f"base cursor offset: {base_pos}")                        # to add offset of current row to later.
        # print(f"scanning chunk {_chunks_}")                             #
        if _chunks_ < 3:                                                  # if chunk is not 3...
            # print(f"scans {5 * _chunks_}:{5 * _chunks_ + 5}")           #
            for _rows_ in range(16):                                      # ...for every row...
                # print(f"cursor offset: {base_pos + _rows_}")            #
                # print(f"scanning row {_rows_}")                         # ... we read a string of 5 chars
                tempStr = rows[_rows_][5*_chunks_:5*_chunks_+5]           # with the offset based on current
                # print(f"contents: '{tempStr}'")                         # chunk.
                for _symbols_ in range(5):                                # for every symbol in the string...
                    # print(f"LED offset: {(base_pos + _rows_)}")         #
                    if tempStr[_symbols_] not in empty:                   # if it is on...
                        # print(f"LED at {_rows_}-{(_symbols_ + 1) * (_chunks_ + 1)} is on")
                        pass                                              # ...do nothing.
                    if tempStr[_symbols_] in empty:                       # if it is off...
                        # print(f"LED at {_rows_}-{(_symbols_ + 1) * (_chunks_ + 1)} is off")
                        LED_Diodes[base_pos + _rows_] &= masks[_symbols_] # ...well, turn it off by masking.
                # print(f"output: {bin(LED_Diodes[base_pos + _rows_])}")  #
                                                                          #
        else:                                                             # if it IS last chunk however...
            # print(f"scanning last symbol of each row")                  #
            for _rows_ in range(16):                                      # ...for every row...
                tempStr = rows[_rows_][15:]                               # scan the only symbol left.
                if tempStr not in empty:                                  # if it is on...
                    # print(f"LED at {_rows_}-16 is on ({tempStr})")      #
                    pass                                                  # ...do nothing.
                else:                                                     # else...
                    # print(f"LED at {_rows_}-16 is off ('{tempStr}')")   #
                    LED_Diodes[base_pos + _rows_] = 0                     # we mask it.
    # print(LED_Diodes)
    print(construct_exclusive(LED_Diodes)[0])  # run function to construct the full SysEx

    # this should be ignored as i have not found a way to cope with random PortMIDI errors
    # if pygame.midi.get_init() and pygame_available:
    #     while to_test.lower() not in yes and to_test.lower() not in no:
    #         to_test = str(input("Do you wish to test the SysEx right away? [y/n]\n")).lower()
    #         if to_test not in yes and to_test not in no:
    #             print("Not a valid answer.")
    #     if to_test in yes:
    #         print()
    #         pygame.midi.Output(_in_).abort()
    #         pygame.midi.Output(_in_).write_sys_ex(0, construct_exclusive(LED_Diodes)[1])
    #         print("Sent to opened device.")

if mode == 2 and pygame_available:

    img = ''
    palette_idx_on = 0 # the palette index that considered as an "ON" LED

    while 1:
        try:
            img = pygame.image.load(input("Image to load (path can be absolute or relative): "))
            imgR = img
            img = pygame.image.tobytes(img, "P")
        except FileNotFoundError:
            print("File not found")
            continue
        if len(img):
            _colors_ = ""
            for _cols_ in range(len(imgR.get_palette())):
                _colors_ += f"{imgR.get_palette_at(_cols_)} "
            # print(_colors_)
            while imgR.get_palette_at(palette_idx_on) != (0, 0, 0, 255):
                palette_idx_on += 1
            # print(f"Using index {palette_idx_on} to compare against")
            break

    for _ in range(16):
        rows[_] = img[(_*16):(_*16+16)]
    # print(rows)

    # this is basically the same loop except for some changes,
    # so I would consider it worth to separate it into a parse_data() function.
    # Especially since if I get to sprite sheets, this loop will be put into another
    # loop. Lmao.

    for _chunks_ in range(4):
        base_pos = (_chunks_ * 16)
        # print(f"base cursor offset: {base_pos}")
        # print(f"scanning chunk {_chunks_}")
        if _chunks_ < 3:
            # print(f"scanning symbols {5 * _chunks_} through {5 * _chunks_ + 5}\n")
            for _rows_ in range(16):
                # print(f"current cursor offset: {base_pos + _rows_}")
                # print(f"scanning row {_rows_}")
                tempStr = rows[_rows_][5*_chunks_:5*_chunks_+5]
                # print(f"contents: '{tempStr}'")
                for _symbols_ in range(5):
                    # print(f"for loop i {_symbols_}, contents: {tempStr[_symbols_]}")
                    # print(f"cursor position in LED_Diodes: {(base_pos + _rows_)}")
                    if tempStr[_symbols_] == palette_idx_on:
                        # print(f"LED at row {_rows_} pos {(_symbols_ + 1) * (_chunks_ + 1)} is on")
                        pass
                    else:
                        # print(f"LED at row {_rows_} pos {(_symbols_ + 1) * (_chunks_ + 1)} is off, masking")
                        LED_Diodes[base_pos + _rows_] &= masks[_symbols_]
                # print(f"output: {bin(LED_Diodes[base_pos + _rows_])}")

        else:
            # print(f"scanning last symbol of each row")
            for _rows_ in range(16):
                tempStr = rows[_rows_][5*_chunks_:5*_chunks_+1]
                if tempStr == palette_idx_on:
                    # print(f"LED at row {_rows_} pos 16 is on (contents: '{tempStr}')")
                    # print(f"output: {bin(LED_Diodes[base_pos + _rows_])}")
                    pass
                else:
                    # print(f"LED at row {_rows_} pos 16 is off, masking (contents: '{tempStr}')")
                    LED_Diodes[base_pos + _rows_] = 0
                    # print(f"output: {bin(LED_Diodes[base_pos + _rows_])}")

    print(construct_exclusive(LED_Diodes)[0])  # run function to construct the full SysEx

    # this should be ignored as i have not found a way to cope with random PortMIDI errors
    # if pygame.midi.get_init() and pygame_available:
    #     while to_test.lower() not in yes and to_test.lower() not in no:
    #         to_test = str(input("Do you wish to test the SysEx right away? [y/n]\n")).lower()
    #         if to_test not in yes and to_test not in no:
    #             print("Not a valid answer.")
    #     if to_test in yes:
    #         print()
    #         pygame.midi.Output(_in_).abort()
    #         pygame.midi.Output(_in_).write_sys_ex(0, construct_exclusive(LED_Diodes)[1])
    #         print("Sent to opened device.")

# if pygame_available:
#     pygame.midi.quit()