loc = input("where file: ")
data = list(open(loc, "rb").read())
for _ in range(len(data)):
    data[_] = (data[_] + 0x80) & 255
l = len(data)
pointer = 0
outdata = []
while l > pointer:
    if data[pointer] == 0x80:
        print(f"0 byte at {hex(pointer)}! silence for {((data[pointer + 1] + 0x80) & 255)} bytes")
        pointer += 1
        outdata.extend( [0x0 for _ in range( (data[pointer] + 0x80) & 255)] )
        #outdata.append(0x7f)
    else:
        outdata.append(data[pointer])
    pointer += 1
open(f"{loc}.decomp", "wb").write(bytearray(outdata))