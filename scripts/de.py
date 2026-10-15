data = open("beatkick.bin", "rb").read()
out_data = []
for _ in data:
    if not _ & 0x80:
        out_data.append(255 - _)
    else:
        out_data.append(_ & 0x7f)

open("beatkick_demu.bin", "wb").write(bytes(out_data))