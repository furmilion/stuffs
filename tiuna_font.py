"""
This script can be used to produce graphical assets,
specifically the 7x8 font for the credits screen of TIunA

For letters, use (█, 1) or (░, 0) characters for on/off bits
respectfully
"""
tiuna_font = [
"00000000000000",
"3c66666666663c",
"6666667c66667c",
"7e18181818187e",
"00000000181800",
"6060607c66667c",
"7e60607e60607e",
"1818181818187e",
"6060607c60607e",
"66667676767e66",
"7c66666666667c",
"183c3c66666666",
"66666e6e767666",
"66667e66663c18",
"7c66667c66667c",
"7c06063c60603e",
"3c66606060663c",
]
def image_from_string(string: str = '.text x"00000000000000"'):
    visual_output = ""
    if string.__contains__('.text x"'):
        temp = string.split('.text x"')[1][:14]
        if len(temp) < 14 or temp.__contains__('"'):
            raise ValueError('Improper string. The string should look like following:\n'
                             '.text x"00000000000000"\n'
                             'or\n'
                             '00000000000000.')
    else:
        temp = string
    if len(temp) < 14:
        raise ValueError('Improper string. The string should look like following:\n'
                         '.text x"00000000000000"\n'
                         'or\n'
                         '00000000000000.')
    temp2 = [temp[_ * 2] + temp[_ * 2 + 1] for _ in range(7)]
    temp2.reverse()
    for i in range(7):
        t2 = bin(int(temp2[i], 16))[2:]
        if len(t2) < 8:
            t2 = ("0" * (8 - len(t2))) + t2
        t3 = ""
        for _ in t2:
            match _:
                case "1":
                    t3 += "█" * 2 # for thickness
                case "0":
                    t3 += "░" * 2
        visual_output += (t3 + "\n")
    return visual_output

def string_from_image(image: str = ""):  # the name is a bit misleading as you still input a string, a single-line one
    pass

if __name__ == "__main__":
    for _ in tiuna_font:
        print(image_from_string(_))