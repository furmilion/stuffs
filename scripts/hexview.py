# me when https://hexed.it but only with hex view
#
# Stuff should look something like this:
#
#      | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ...............................
# -----+-------------------------------------------------+---------------------------------
#  000 | 00 FE 12 A2 C1 11 11 98 AA AB 89 AB 29 30 56 32 | .. þ.. ¢ Á...... ª «.. « ) 0 V 2
#  ... | .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. | ................................
#  ... | .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. | ................................
#  270 | 36 38 98 21 11 21 84 48 0A FE 8F A2 5B 2B 12 32 |  6 8.. !.. !.. H.. þ.. ¢ [ +.. 2

from os import name as osName, system as shl


class HexViewer:
    def __init__(self):

        self.MAJOR_VERSION = "beta 0"
        self.MINOR_VERSION = 5
        self.PATCH_VERSION = 1
        self.VERSION_STRING = (f"{self.MAJOR_VERSION}"
                               f"{('.' + str(self.MINOR_VERSION)) if self.MINOR_VERSION > 0 else ''}"
                               f"{('.' + str(self.PATCH_VERSION)) if self.PATCH_VERSION > 0 else ''}")

        self.FULL_VERSION_STRING = "#"
        for _ in range(60 - len(self.VERSION_STRING)): self.FULL_VERSION_STRING += " "
        self.FULL_VERSION_STRING += 'v' + self.VERSION_STRING + " #\n"

        self.BANNER = (
            f"[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]\n"
            f"#             ______  _   __                                   #\n"
            f"#            / __  / | | / / HH  HH  EEEEEE  XX  XX            #\n"
            f"#           / /__//  | |/ /  HH  HH  EE       XXXX             #\n"
            f"#          / ____/   \\   /   HHHHHH  EEEE      XX              #\n"
            f"#         / /       _/  /    HH  HH  EE       XXXX             #\n"
            f"#        /_/       [___/     HH  HH  EEEEEE  XX  XX  ED.       #\n"
            f"{self.FULL_VERSION_STRING}"
            f"[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]\n"
        )
        self.WELCOME = (
            f"Welcome to PYHEXed!\n"
            f"This is a console hex editor painfully written in Python.\n"
            f"To begin, type 'HLP' to get a list of available keywords.\n"
            f"\n"
        )
        self.file = []
        self.cursor = 0
        self.viewSize = [8, 8]         # [width, height]
        self.keywords = ["cnk",        # view field size, in Lines by Columns
                         "nav",        # navigation through the data
                         "edt",        # editing of data
                         "opn",        # open a file to edit
                         "sav",        # save a file
                         "new",        # new empty file
                         "!qt", "qt",  # quit the progtram
                         "hlp",        # display this list
                         "del",        # remove data
                         "echo",       # echo
                         ]
        self.die = False
        self.lastStatus = self.BANNER + self.WELCOME
        self.status = 1
        self.PRINTABLE_SHIT = (' !"#$%&\'()*+,-./'
             '0123456789'
             ':;<=>?@'
             'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\\]^_`'
             'abcdefghijklmnopqrstuvwxyz'
             '{|}~'
             '¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿'
             'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ'
             '×'
             'ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ')
        self.main()

    def load(self, file):
        """
        Attempt loading specified file.
        :param file: The file in question
        :return:
        """
        try:
            self.file = open(file, "rb").read()
        except FileNotFoundError as e:
            self.lastStatus = f"{file} cannot be read: {e}."
            return 1
        self.main()

    def save(self, file):
        try:
            open(file, "wb").write(bytes(self.file))
        except FileExistsError:
            open(file, "xb").write(bytes(self.file)) \
                if input("\nAre you sure you want to overwrite the file? [Y/N]").lower() == "y" \
                else self._()
        print("what")
        return 2

    def new(self) -> int:
        """
        Empties the data array, "creating" a new empty file.
        Always returns 0.
        :return:
        """
        self.file = []
        return 0

    def draw(self) -> int:
        """
        The drawer of the viewfield.
        :return:
        """
        match osName:
            case "nt":
                shl("cls")
            case "posix":
                shl("clear")
        viewfield = (
                '  '
                + (' ' * len(hex(len(self.file))[2:]))
                + '|'
        )

        # TODO: fix this specific loop
        for _ in range(self.viewSize[1]):
            viewfield += (
                    f's 0{hex(_)[2:].upper() + ("0" * (len(hex(self.viewSize[1])[2:]) - 1))}'
                    if len(hex(self.viewSize[1])[2:]) < len(hex(_)[2:]) else f' FUCK{hex(_)[2:].upper()}'
            )

        viewfield += (
                ' |' '  '
                + (' ' * self.viewSize[0])
                + '\n'
                + '--'
                + ('-' * len(hex(len(self.file))[2:]))
                + '+'
                + ('---' * self.viewSize[0])
                + '-+' '--'
                + ('--' * self.viewSize[0])
                + '\n'
        )
        for _ in range(self.viewSize[1]):
            viewfield += (
                    ' '
                    + (
                        hex(_)[2:].upper()
                        + '0'
                        * (len(hex(len(self.file))[2:]) - 1)
                        if len(hex(_)[2:]) < len(hex(len(self.file))[2:])
                        else hex(_)[2:].upper()
                    )
                    + ' |'
            )
            for __ in range(self.viewSize[1]):
                viewfield += (
                    f' {hex(self.file[(_ * self.viewSize[1]) + __])[2:].upper()}'
                    if ((_ * self.viewSize[1]) + __) < len(self.file) else ' ..'
                )
            viewfield += ' | '
            for ___ in range(self.viewSize[1]):
                if ((_ * self.viewSize[1]) + ___) < len(self.file):
                    viewfield +=\
                    " ." if chr(((_ * self.viewSize[1]) + ___)) not in self.PRINTABLE_SHIT\
                        else ' ' + chr(((_ * self.viewSize[1]) + ___))
                else:
                    viewfield += " ."
            viewfield += "\n"

        print(viewfield)
        return 0

    def parse(self) -> int:
        """
        Prints '>>>' and waits for user input.
        Once the input is acquired, it is being split into a list containing
        a keyword and parameters, all separated by a colon.

        Returns an integer code upon operation completion:
         - 0: success
         - 1: insignificant error
         - 2: keyword error or a significant error
         - 3: breaking bad
        :return: Integer code
        """
        self.status = 0
        self.lastStatus = ""
        cmd: list = input(">>> ").lower().split(":")
        while len(cmd) < 4: cmd.append('')

        if cmd[0].lower() not in self.keywords:  # early check for an invalid command
            self.lastStatus = f"Unknown keyword '{cmd[0]}'. Use 'HLP' to print a list of usable keywords."
            return 2

        match cmd[0].lower():
            case "cnk":  # changing the size of viewed data chunk
                if len(cmd) < 3:
                    print("No.")
                    return 3  # TODO: improve this shitass exception protection
                try:
                    int(cmd[2])
                    int(cmd[1])
                except ValueError:
                    self.lastStatus = (f'Warning: {cmd[1]}/{cmd[2]}: either of the arguments is a hexadeximal.')
                    try:
                        int(cmd[2], 16)
                        int(cmd[1], 16)
                        self.viewSize = [int(cmd[1], 16), int(cmd[2], 16)]
                    except ValueError:
                        self.lastStatus = (f'Invalid values {cmd[1]}/{cmd[2]}: either of the arguments cannot be'
                                           f'treated as an integer')
                        return 1

                self.viewSize = [int(cmd[1]), int(cmd[2])]
                return 0
            case "nav":  # navigating the data

                if len(cmd) < 2:
                    print("No.")
                    return 3  # TODO: improve this shitass exception protection

                if 'i' in cmd[2]:
                    try:
                        self.cursor = int(cmd[1])
                    except ValueError:
                        try:
                            self.cursor = int(cmd[1], 16)
                            self.lastStatus = f"{cmd[1]} cannot be parsed as a decimal integer, fallback to hexadecimal."
                            return 1
                        except ValueError:
                            self.lastStatus = f"{cmd[1]} cannot be parsed as a hexadecimal integer, command not performed."
                            return 1
                else:
                    try:
                        self.cursor = int(cmd[1], 16)
                    except ValueError:
                        self.lastStatus = f"{cmd[1]} cannot be parsed as a decimal integer, fallback to hexadecimal."
                        return 1
                return 0
            case "edt":  # editing the data
                data_offset = 0

                if len(cmd) < 4:
                    print("No.")
                    return 3  # TODO: improve this shitass exception protection

                # edit statuses describe how exactly should the data be edited.
                # edit status 'i': treat the edit address as an integer
                # edit status 'p': offset from the file start or the cursor
                # edit status 'I': treat data as an integer

                # status check
                if 'i' in cmd[3]:
                    try:
                        data_offset = int(cmd[1])
                    except ValueError:
                        self.lastStatus += f"{cmd[1]} cannot be parsed as a decimal integer, fallback to hexadecimal.\n"
                        try:
                            data_offset = int(cmd[1], 16)
                        except ValueError:
                            self.lastStatus += f"{cmd[2]} cannot be parsed as a hexadecimal integer, command not performed.\n"
                            return 1

                if 'p' in cmd[3]:
                    data_offset = data_offset + self.cursor

                if 'I' in cmd[3]:
                    try:
                        dataInt = int(cmd[2])
                        data = []
                        while dataInt > 255:
                            data.append(dataInt & 255)
                            dataInt >>= 8
                    except ValueError:
                        self.lastStatus += f"{cmd[2]} cannot be parsed as a decimal integer, fallback to hexadecimal.\n"
                        try:
                            dataInt = int(cmd[2], 16)
                            data = []
                            while dataInt > 255:
                                data.append(dataInt & 255)
                                dataInt >>= 8
                        except ValueError:
                            self.lastStatus += f"{cmd[2]} cannot be parsed as a hexadecimal integer, command not performed.\n"
                            return 1

                # handle attempt to interpret parameter 2 (data) as a hexadecimal number
                try:
                    dataInt = int(cmd[2], 16)
                    data = []
                    while dataInt > 255:
                        data.append(dataInt & 255)
                        dataInt >>= 8
                except ValueError:
                    self.lastStatus += f"{cmd[1]} cannot be as a hexadecimal integer, command not performed.\n"
                    return 1

                # handle data editing
                if len(data) <= (len(self.file) - data_offset):
                    for idx, value in enumerate(data):
                        self.file[(len(self.file) - data_offset) + idx] = value
                elif len(data) > (len(self.file) - data_offset):
                    self.file.append(
                        value
                        for value in range(len(data) - (len(self.file) - data_offset))
                    )
                    for idx, value in enumerate(data):
                        self.file[(len(self.file) - data_offset) + idx] = value
                else:
                    self.lastStatus += f"something went really wrong, command not performed.\n"
                    return 3
                return 0
                # 'ㅤ' (hangul filler)
            case "opn":

                if len(cmd) < 2:
                    print("No.")
                    return 3  # TODO: improve this shitass exception protection

                return self.load(str(cmd[1]))
            case "sav":

                if len(cmd) < 2:
                    print("No.")
                    return 3  # TODO: improve this shitass exception protection

                return self.save(str(cmd[1]))
            case "new":
                return self.new()
            case "hlp":
                self.status = 1
                match osName:
                    case "nt":
                        shl("cls")
                    case "posix":
                        shl("clear")
                if cmd[1].lower() not in self.keywords and cmd[1].lower() != '':  # early check for an invalid command
                    self.lastStatus = f"Unknown keyword '{cmd[1]}'. Use 'HLP' to print a list of usable keywords."
                    return 2
                match cmd[1].lower():
                    case "general" | "":
                        self.lastStatus = self.BANNER + \
                                          (
                                              "Following keywords are available:\n"
                                              "CNK:<rows>:<columns>            Change the size of the 'viewport'\n"
                                              "NAV:<address>:<flags>           Navigate the file\n"
                                              "OPN:<file>                      Load a file for editing\n"
                                              "SAV:<file>                      Save a file\n"
                                              "NEW                             Make a blank file\n"
                                              "EDT:<address>:<data>:<flags>    Edit data at a specified address\n"
                                              "DEL:<address>:<amount>:<flags>  Remove a specified amount of bytes at a\n"
                                              "                                                      specified address\n"
                                              "HLP:<keyword>                   Display general help, or for a specific\n"
                                              "                                    keyword,vif the argument is present\n"
                                              "!QT                             Quit the editor\n"
                                              "All the keywords are case-insensetive. Flags, however, are.\n"
                                          )
                    case "cnk":
                        self.lastStatus = self.BANNER + \
                                          (
                                              "Help for the keyword 'CNK'.\n"
                                              "CNK - changes the size of viewport aka the viewable part of the file.\n"
                                              "Parameters:\n"
                                              "<rows>: the amount of rows ro show. If unspecified, defaults to\n"
                                              "last set value.\n"
                                              "<columns>: the amounts of columns to show. If unspecified, defaults\n"
                                              "to last set value.\n"
                                          )
                    case "nav":
                        self.lastStatus = self.BANNER + \
                                          (
                                              "Help for the keyword 'NAV'.\n"
                                              "NAV - navigates the viewport throughout the file.\n"
                                              "Parameters:\n"
                                              "<address>: Navigate to the specified address.\n"
                                              "<flags>: Flags that change the way parameters are interpreted.\n"
                                              "Available flags:\n"
                                              "    - i: attempt to treat the address as a decimal integer.\n"
                                          )
                    case "opn":
                        self.lastStatus = self.BANNER + \
                                          (
                                              "Help for the keyword 'OPN'.\n"
                                              "OPN - opens a file to edit.\n"
                                              "Parameters:\n"
                                              "<file>: the file in question that you want to open.\n"
                                          )
                    case "sav":
                        self.lastStatus = self.BANNER + \
                                  (
                                      "Help for the keyword 'SAV'.\n"
                                      "OPN - saves a file to disk.\n"
                                      "Parameters:\n"
                                      "<file>: the file in question that you want to save.\n"
                                  )
                    case "new":
                        self.lastStatus = self.BANNER + \
                                  (
                                      "Help for the keyword 'NEW'.\n"
                                      "NEW - creates a blank 'file'.\n"
                                      "Parameters:\n"
                                      "None\n"
                                  )
                    case "edt":
                        self.lastStatus = self.BANNER + \
                                          (
                                              "Help for the keyword 'EDT'.\n"
                                              "EDT - edit data at specified address.\n"
                                              "Parameters:\n"
                                              "<address>: The address to edit data from.\n"
                                              "<data>: Data that overwrites the present one at that address.\n"
                                              "<flags>: Flags that change the way parameters are interpreted.\n"
                                              "Available flags:\n"
                                              "    - i: attempt to treat the address as a decimal integer.\n"
                                              "    - p: address is relative to viewport position.\n"
                                              "    - I: attempt to treat the data as a decimal integer.\n"
                                          )
                    case "del":
                        self.lastStatus = self.BANNER + \
                                          (
                                              "Help for the keyword 'DEL'.\n"
                                              "DEL - delete data at specified address.\n"
                                              "Parameters:\n"
                                              "<address>: The address to delete data from.\n"
                                              "<amount>: Amount of bytes to delete.\n"
                                              "<flags>: Flags that change the way parameters are interpreted.\n"
                                              "Available flags:\n"
                                              "    - i: attempt to treat the address as a decimal integer.\n"
                                              "    - p: address is relative to viewport position.\n"
                                          )
                    case "hlp":
                        self.lastStatus = self.BANNER + \
                                  (
                                      "Help for the keyword 'HLP'.\n"
                                      "HLP - Displays help.\n"
                                      "Parameters:\n"
                                      "<keyword>: if specified, the command will attempt to fetch help for\n"
                                      "this keyword.\n"
                                  )
                    case "!qt" | "qt":
                        self.lastStatus = self.BANNER + \
                                  (
                                      "Help for the keyword '!QT'.\n"
                                      "!QT - Quits the editor.\n"
                                      "Parameters:\n"
                                      "None\n"
                                  )
                    case "echo":
                        self.lastStatus = self.BANNER + \
                                  (
                                      "Help for the keyword 'ECHO'.\n"
                                      "ECHO - Echoes whatever argument was passed to it.\n"
                                      "Parameters:\n"
                                      "<value>: Whatever that needs to be echoed.\n"
                                  )
                    case _:
                        self.lastStatus = f"No help available for {cmd[1]}. I probably forgot to add it."
            case "!qt" | "qt":
                print("Bye-bye!")
                self.die = 1
                return 4
            case "echo":
                self.lastStatus = ' '.join(cmd[1:])
                return 0
            case _:  # fallback if i somehow mess up and forget to add the command to parser
                self.lastStatus = (f"my ass forgogt to implement {cmd[0]} 💀")
                return 2

    def main(self):
        while not self.die:
            self.draw() if self.status == 0 else self._()
            print('\n' + self.lastStatus)
            self.parse()
        return ""

    def _(self):
        pass


def hexview(string: bytes = b'', length: int = 8) -> None:
    # prepare initial stuff
    # temp1 = ""
    temp2 = ""
    temp3 = ""
    final = ""
    try:
        length = int(length)  # what if something inputted is not a number?
    except ValueError:
        print("Invalid length, reverting to 8")
        length = 8
    # string = str(string)  # no way to know for sure if we work with string
    # prepare the first row or something
    temp1 = "  "
    # dots = ""

    # print("Preparing first row")

    for i in range(len(str(hex(len(string))[2:]))):  # prepare first empty column, pad to length of total data
        temp1 += " "
    if len(temp1) < 4:
        temp1 += " "
    temp1 += "| "
    for i in range(length):
        if len(str(hex(i))[2:]) < 2:
            temp1 += f"0{str(hex(i))[2:]} "  # prepare numbers
        else:
            temp1 += str(hex(i))[2:] + " "  # prepare numbers
    temp1 += "| "  # insert another pipe at the end
    for i in range(length):
        temp1 += "."
    final += temp1.upper() + "\n"  # print flush

    # print("Drawing separator")

    temp1 = ""  # flush all data
    for i in range(len(str(hex(len(string))[2:])) + 2):  # separator
        temp1 += "-"
    if len(temp1) < 4:
        temp1 += "-"
    temp1 += "+"
    for i in range(length):
        temp1 += "---"
    temp1 += "-+-"
    for i in range(length):
        temp1 += "-"
    temp1 += "-"  # it must be just one symbol longer than the rest
    final += temp1.upper() + "\n"  # print flush
    # array of printable chars, if the char is not in an array, it is displayed as dots
    chars = (" !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
             "¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ")
    # Here is the funny loop part: iterating over string data to print
    temp1 = f" "  # flush all deeta
    offset = 0
    toiter = len(string) // length
    if divmod(len(string), length)[1]:
        toiter += 1
    for i in range(toiter):

        # print(f"Rendering row {i + 1}... Offset: {hex(offset)[:2] + hex(offset)[2:].upper()}")

        if len(str(hex(offset)[2:])) < 2:
            temp2 += f"0{hex(offset)[2:].upper()}"
        else:
            temp2 += f"{hex(offset)[2:].upper()}"
        if len(temp2) < len(str(hex(len(string))[2:])):
            for i in range(len(str(hex(len(string))[2:])) - len(temp2)):
                temp3 += "0"
            temp2 = temp3 + temp2
        temp1 += temp2
        temp1 += " | "
        temp2 = ""  # flush
        temp3 = ""  # flush
        for dt in range(length):
            try:
                if string[dt + offset]:
                    # temp5 = hex(string[dt + offset]).upper()[2:] \
                    #     if len(hex(string[dt + offset]).upper()[2:]) < 2 \
                    #     else ('0' + hex(string[dt + offset]).upper()[2:])
                    # temp1 += f"{temp5} "  # i
                    temp1 += f"""{
                    ('0' + hex(string[dt + offset]).upper()[2:])
                    if len(hex(string[dt + offset])[2:]) < 2
                    else (hex(string[dt + offset]).upper()[2:]
                    )} """  # i
            except IndexError:
                temp1 += ".. "
        temp1 += "| "
        for char in range(length):
            try:
                if chr(string[char + offset]) in chars:
                    temp1 += f"{chars[chars.index(chr(string[char + offset]))]}"
            except IndexError:
                temp1 += "."
        temp1 += "\n "
        offset += length
    final += temp1
    print(final)  # print flush


# hexview("0",8)
# hexview("0123456789A",8)
# hexview("0123456789ABCDEF",16)
# hexview("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",8)
# hexview(str(list(range(2048))), 12)
# hexview("a",11)
# help(rtc)
# help("funcs")
# hexview(open("hexview.py", "rb").read(), 32)
HexViewer()