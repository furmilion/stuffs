from sc55_rom_decomp_globals import *

char = np.uint8
uint8_t = np.uint8
int8_t = np.int8
ushort = np.uint16
short = np.int16
ulong = np.uint32
long = np.int32
ulonglong = np.uint64
longlong = np.int64

def rpcm_decode(data: np.int8 | np.uint8 = None) -> int:
    # from mamedev/mame/src/devices/sound/rolandpcm.cpp
    # RPCM is just my name for this specific pcm type.
    if not data: return 0
    if not isinstance(data, (np.int8, np.uint8)): raise TypeError("Input must be of type numpy.int8 or numpy.uint8!")
    data = int(data.view(np.int8)) if isinstance(data, np.uint8) else int(data)
    if data < 0:
        sign = -1
        val = -data
    else:
        sign = 1
        val = data
    shift = val >> 4
    val &= 15
    if not shift:
        result = val * sign
    else:
        result = ((0x10 + val) << (shift - 1)) * sign
    return result
    if result < 0:
        return (~result) - 32768
    return result
    # CM32L pcm

def ldpcm_decode(data: char = 0):
    """
    LDPCM is a DPCM compression type used on all of Roland's GS synths, and was named as such by Edward d-tech
    this is a dummy function for now
    """
    pass