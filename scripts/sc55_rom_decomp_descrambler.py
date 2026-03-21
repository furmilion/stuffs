from sc55_rom_decomp_globals import *
def unscramble_address(addr):
    if addr < 0x20:
        return addr
    out = 0
    for bit in range(20):
        out |= ((addr >> address_order[bit]) & 1) << bit
    return out
def unscramble_byte(b):
    out = 0
    for bit in range(8):
        out |= ((b >> byte_order[bit]) & 1) << bit
    return out
byte_lut = [unscramble_byte(_) for _ in range(256)]

def descramble_wave(
        files: list[str] = None,  # what to descramble
        ignore: bool | int = False,  # whether to not do anything so that i dont comment out the entire function
        id: int = -1,  # used when returning a buffer and sacing a file
        one_file: bool | int = False,  # whether to dump descrambled roms into a single file
        return_buffer: bool | int = False,  # whether to return a tuple of (id, data) instead  of writing to a file
) -> bytearray | tuple[int, list[int]] | None:
    if ignore:
        return
    if files is None:
        files = []
    if files == []:
        raise ValueError("this needs at least some input")
    if one_file:
        try:
            buffer = open(f"{model}{firmware}_wave_descrambled.rom", "xb")
        except FileExistsError:
            buffer = open(f"{model}{firmware}_wave_descrambled.rom", "wb")
    for x in range(len(files)):
        try:
            encoded_rom = open(files[x], "rb").read()
        except FileNotFoundError:
            print(
                f"uhhhhhhhh where is {files[x]} its like not found\n"
                f"or something, results will probably break"
                )
            continue

        dec_buf = [0 for _ in range(0x100000)]
        if not one_file and not return_buffer:
            try:
                buffer = open(f"{model}{firmware}_wave{x if len(files) > 1 else id}_descrambled.rom", "xb")
            except FileExistsError:
                buffer = open(f"{model}{firmware}_wave{x if len(files) > 1 else id}_descrambled.rom", "wb")

        print(f"bank {x}, id {id}")
        for y in range(0x100000):
            if y < 0x20:
                dec_buf[y] = encoded_rom[y]
                continue
            dec_buf[unscramble_address(y)] = byte_lut[encoded_rom[y]]
            # print(y)
        if not return_buffer:
            buffer.write(bytearray(dec_buf))
            if not one_file:
                buffer.close()
        # return bytearray(dec_buf)
    if one_file and not return_buffer:
        buffer.close()
    # this is real messy
    print("done")
    return (id, dec_buf)


def descramble_wave_multithread(
        files: list[list[str]] = None,  # what to descramble
        ignore: list[bool | int] = None,  # whether to not do anything so that i dont comment out the entire function
        id: list[int] = None,  # used when returning a buffer and sacing a file
        one_file: list[bool | int] = None,  # whether to dump descrambled roms into a single file
        return_buffer: list[bool | int] = None,  # whether to return a tuple of (id, data) instead  of writing to a file
):
    if files is None: files = [0]
    if ignore is None: ignore = [0 for _ in range(len(files))]
    if id is None: id = [_ for _ in range(len(files))]
    if one_file is None: one_file = [0 for _ in range(len(files))]
    if return_buffer is None: return_buffer = [0 for _ in range(len(files))]
    runners = min(len(files), len(ignore), len(id), len(one_file), len(return_buffer))
    if runners < 1:
        raise ValueError("One of the arguments was 0 in length.")
    fn = []
    for arg in range(runners):
        fn.append((files[arg], ignore[arg], id[arg], one_file[arg], return_buffer[arg]))
    print(
        f"runners: {runners}\n"
        f"args: {fn}"
        )
    with PPE(max_workers=runners) as exec:
        for args in fn:
            # print(*args)
            exec.submit(descramble_wave, *args)