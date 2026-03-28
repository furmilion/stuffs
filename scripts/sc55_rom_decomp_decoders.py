import numpy as np

from sc55_rom_decomp_globals import *

"""
int16_t mb87419_mb87420_device::decode_sample(int8_t data)
{
	int16_t val;
	int16_t sign;
	uint8_t shift;
	int16_t result;

	if (data < 0)
	{
		sign = -1;
		val = -data;
	}
	else
	{
		sign = +1;
		val = data;
	}

	// thanks to Sarayan for figuring out the decoding formula
	shift = val >> 4;
	val &= 0x0F;
	if (! shift)
		result = val;
	else
		result = (0x10 + val) << (shift - 1);
	return result * sign;
}
"""
char = np.uint8
uint8_t = np.uint8
int8_t = np.int8
ushort = np.uint16
short = np.int16
ulong = np.uint32
long = np.int32
ulonglong = np.uint64
longlong = np.int64
def ldpcm_decode(data: char = 0):
    """
    this is a dummy function for now
    """
    pass