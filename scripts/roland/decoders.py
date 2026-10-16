import sys
import numpy as np

sys.path.append("../")
import FurWave

DEBUG = False

def decode_fce_address(address: int = 0):
    print(f"decoding address {address}") if DEBUG else None
    scaleAddress=((address & 0xFFFFF) >> 5) | (address & 0xF00000) # latter for banks
    print(f"scalar address {scaleAddress}") if DEBUG else None
    scaleNibble=address&0x10
    print(f"scalar nibble: {1 if scaleNibble else 0} ({scaleNibble})") if DEBUG else None
    return scaleAddress, scaleNibble

def decode_fce(bank: list[int] | bytes | None = None, address: int = 0) -> int:
    if not bank:
        return 0
    scalars = decode_fce_address(address)
    print(f"scalars: {scalars}") if DEBUG else None
    scaledNibble = (bank[scalars[0]]>>4) if scalars[1] else (bank[scalars[0]]&15)
    print(f"scalar at bank: {bank[scalars[0]]}, nibble: {scaledNibble}") if DEBUG else None
    bankSample = (bank[address] ^ 128) - 128
    return (bankSample << scaledNibble) << 14

def scale_fce(val: int = 0, tofloat: bool = False, scale: int = 30):
    if tofloat:
        return val / (1 << scale)
    else:
        return val & (1 << scale)

# BEHOLD! The holy testing area
# You might want to change those
# paths on your machine if you
# decide to run this as a module
# instead of just importing the
# functions and using those.
# Also requires descrambling
# the wave ROMs beforehand.
if __name__ == '__main__':
    files = []
    with open(r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom1_DED.bin", "rb") as wave:
        files.append(wave.read())
    with open(r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk2\waverom2_DED.bin", "rb") as wave:
        files.append(wave.read())
    for file in files:
        SIZE = len(file)
        deltas = [decode_fce(file, _) for _ in range(SIZE)]
        print(f"file {files.index(file) + 1} done")
        print(samples) if DEBUG else None
        writer = FurWave.WaveWriter(data=np.cumsum(deltas), bitdepth=32, packed=False)
        print(writer.get_data()) if DEBUG else None
        writer.write_file(f"./waverom_{files.index(file) + 1}.wav", True)
