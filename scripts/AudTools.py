import funcs



def convert_12_to_16(data12: list[int] | bytes = None):
    if not data12: return [0, 0]
    data16 = [0 for _ in range((len(data12) * 2) // 3)]
    #pain(f"data16 array len {len(data16)}")
    #pain(f"data12 in array len {len(data12)}")
    i, j = 0, 0
    while i < len(data16):
        data16[i + 0] = (data12[j + 0] << 8) | (data12[j + 1] & 0xf0)
        if (i + 1) < len(data16):
            data16[i + 1] = (data12[j + 2] << 8) | ( (data12[j + 1] << 4) & 0xf0)
        i += 2
        j += 3
    #print(f"sample {i} byte {i}")
    return data16

