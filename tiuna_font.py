"""
This script can be used to produce graphical assets,
specifically the 7x8 font for the credits screen of TIunA
It can also convert general graphics into an "image"

For letters, use (█, 1) or (░, 0) characters for on/off bits
respectfully
"""
twin_credits_font = [ # font_gfx
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

title_gfx = [
"80408000f05050504060d0", # title_gfx0
"03820300d0a884b4b4b4fc", # title_gfx1
"1f101d051d15b5b5054db7", # title_gfx2
"020c0204020208100a0202", # title_gfxw
]
subt_gfx = [
"1e1e10184c4602121e0c", # subt_gfx0
"193d2521212121253d19", # subt_gfx1
"21232222e2e222222321", # subt_gfx2
"8cde525212121252de8c", # subt_gfx3
"47e7b494979794949797", # subt_gfx4
"a4a4242439392424bcb8", # subt_gfx5
]
icon_gfx = [
"000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", # icon_gfx0
"3f7f405f5f2f2f2f171717170b0b0b050505050202020101010100000000000000000000000000000000000000000000000000", # icon_gfx1
"ffff00fffffefcfcfcfcfefffffefefefcfcfcfcfcfc7c7c7c7cbcbcbc5c5c5c5c2c2e2f171717170b0b0b0505050402030100", # icon_gfx2
"ffff00ffffff7f7f7f7fffffffffffff7f7f7f7e7e7e7c7c7c7c7878787171717262e2e2c4c4c4c8888888101010202020c0c0", # icon_gfx3
"f8fc06f2f2e2e2e2c4c4c4c8888888101010202020204040408080808000000000000000000000000000000000000000000000", # icon_gfx4
]
warn_gfx = [
"6666ffffffffdbdbdbdbdbdbdbc3c3c3", # warn_gfx0
"66666666667e7e66666666663c3c1818", # warn_gfx1
"cdcdcdcdddd9d9f9f9cdcdcdcdcdf9f9", # warn_gfx2
"9b9b99b9b9b9b9f9f9d9d9d9d9999b9b", # warn_gfx3
"d9d9999b9b9b9b9f9f9d9d9d9d99d9d9", # warn_gfx4
"8e9f9bb3b3b3b3b7b7b0b0b0b19b9f8e", # warn_gfx5
]
flash_gfx = [
"8d8d8989c9c98989e8e8", # flash_gfx0
"495d5545cdd951559d89", # flash_gfx1
"55555555d5d555555756", # flash_gfx2
"33735252524242527222", # flash_gfx3
"55555555555555555d59", # flash_gfx4
"c9dd14058d991115ddc9", # flash_gfx5
]
ayce_gfx = [
"00000000383800000000", # ayce_gfx0
"fefe8282fefe0202fefe", # ayce_gfx1
"fefe0202fefe82828282", # ayce_gfx2
"fefe808080808080fefe", # ayce_gfx3
"fefe8080fefe8282fefe", # ayce_gfx4
"00000000383800000000", # ayce_gfx5
]

def image_from_string(string: str = '00000000000000', no_reverse = False):
    visual_output = ""
    temp2 = [string[_ * 2] + string[_ * 2 + 1] for _ in range(len(string)//2)]
    if not no_reverse: temp2.reverse()
    for i in range(len(string)//2):
        t2 = bin(int(temp2[i], 16))[2:]
        if len(t2) < 8:
            t2 = ("0" * (8 - len(t2))) + t2
        t3 = ""
        for _ in t2:
            match _:
                case "1":
                    t3 += "█"# * 2 # for thickness
                case "0":
                    t3 += "░"# * 2
        visual_output += (t3 + "\n")
    return visual_output

def string_from_image(image: str = ""):  # the name is a bit misleading as you still input a string, a single-line one
    image_split = image.split("|")  # use pipe as a separator
    arr = []
    out_pre = []
    out = ""
    for _ in image_split:
        tempstr = ""
        for __ in _:
            if __ == "░":
                tempstr += "0"
            elif __ == "█":
                tempstr += "1"
            elif __ == "0":
                tempstr += _
            elif __ == "1":
                tempstr += _
            else:
                raise ValueError(f"unexpected character {__}")
        #print(tempstr)
        arr.append(tempstr)
    for _ in arr:
        tempstr = hex(int(_, 2))[2:]
        tempstr = ("0" * (2 - len(tempstr))) + tempstr
        #print(tempstr)
        out_pre.append(tempstr)
    out_pre.reverse()
    for _ in out_pre:
        out += _
    print(image_from_string(out))
    return f'.text x"{out}"'

if __name__ == "__main__":
    #for _ in twin_credits_font:
    #    print(image_from_string(_))
    for _ in subt_gfx:
        print(image_from_string(_, 0))
    # print(string_from_image(
    #     "░░░░░██░|"
    #     "░░░░██░░|"
    #     "░░░░██░░|"
    #     "░░░██░░░|"
    #     "░░██░░░░|"
    #     "░░██░░░░|"
    #     "░██░░░░░"
    # ))

"""
░░░░██░░ ░░░██░░█ ░░█░░░░█ █░░░██░░ █░░█░███ █░███░░░
░░░████░ ░░████░█ ░░█░░░██ ██░████░ █░░█░███ █░████░░
░░░█░░█░ ░░█░░█░█ ░░█░░░█░ ░█░█░░█░ █░░█░█░░ ░░█░░█░░
░░░░░░█░ ░░█░░░░█ ░░█░░░█░ ░░░█░░█░ █░░█░█░░ ░░█░░█░░
░█░░░██░ ░░█░░░░█ ███░░░█░ ░░░█░░█░ █░░█░███ ░░███░░█
░█░░██░░ ░░█░░░░█ ███░░░█░ ░░░█░░█░ █░░█░███ ░░███░░█
░░░██░░░ ░░█░░░░█ ░░█░░░█░ ░█░█░░█░ █░░█░█░░ ░░█░░█░░
░░░█░░░░ ░░█░░█░█ ░░█░░░█░ ░█░█░░█░ █░██░█░░ ░░█░░█░░
░░░████░ ░░████░█ ░░█░░░██ ██░████░ ███░░███ █░█░░█░░
░░░████░ ░░░██░░█ ░░█░░░░█ █░░░██░░ ░█░░░███ █░█░░█░░
"""









