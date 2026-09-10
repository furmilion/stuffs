import sys

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
    with open(r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_1_DED.bin", "rb") as wave:
        files.append(wave.read(-1))
    with open(r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_2_DED.bin", "rb") as wave:
        files.append(wave.read(-1))
    with open(r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_3_DED.bin", "rb") as wave:
        files.append(wave.read(-1))
    #READ_SIZE = 54747
    #START = 47616
    #END = 54747
    #testFile = open(r"E:\D Drive (HDD)\- THE ULTIMATE STUFF COLLECTION -\Git\Git\NukeYKT Nuked SC-55\Nuked-55 Imp\roms\mk1\waverom_2_DED.bin", "rb").read(READ_SIZE+1)
    #SIZE = len(file)
    #print(testFile) if DEBUG else None
    #samples = [0 for _ in range(END-START+1)]
    #for spl in range(START, END+1):
        #delta = decode_fce(testFile, spl) / (1 << 30)
        #print(f"sample: {sample}, delta: {delta} ({decode_fce(testFile, spl)})") if DEBUG else None
        #sample += delta
        #samples[spl - START] = sample
    for file in files:
        SIZE = len(file)
        sample = 0
        samples = [0 for _ in range(SIZE)]
        for smpl in range(SIZE):
            #delta = decode_fce(testFile, smpl) / (1 << 30)
            delta = decode_fce(file, smpl)
            sample += delta
            samples[smpl] = sample
        print(f"file {files.index(file) + 1} done")
        print(samples) if DEBUG else None
        #writer = FurWave.WaveWriter(data=samples, bitdepth=32.0, packed=1)
        writer = FurWave.WaveWriter(data=samples, bitdepth=32, packed=False)
        #writer.set_data(samples)
        print(writer.get_data()) if DEBUG else None
        writer.write_file(f"./waverom_{files.index(file) + 1}.wav", True)
