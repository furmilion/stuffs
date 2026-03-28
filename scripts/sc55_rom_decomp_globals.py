from funcs import text_from_bytes, clamp, note_from_key, _
from os import name as osName
try:
    import numpy as np
except ImportError:
    raise NotImplementedError("NumPy is required for operation here. I'm sotty, but that's how it is.")
posix = osName == "posix"
nt = osName == "nt"
model = "mk1"
firmware = "_120"
wave = "_wave/"  # wave roms
from FurWave import WaveWriter
from concurrent.futures import ProcessPoolExecutor as PPE
address_order = [0x02,0x00,0x03,0x04,0x01,0x09,0x0D,0x0A,0x12,
               0x11,0x06,0x0F,0x0B,0x10,0x08,0x05,0x0C,0x07,0x0E,0x13]
byte_order = [2, 0, 4, 5, 7, 6, 3, 1]
