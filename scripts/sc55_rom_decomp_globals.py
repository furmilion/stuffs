from funcs import text_from_bytes, clamp, note_from_key, _
from os import name as osName
posix = osName == "posix"
nt = osName == "nt"
from FurWave import WaveWriter
from concurrent.futures import ProcessPoolExecutor as PPE
address_order = [2, 0, 3, 4, 1, 9, 13, 10, 18, 17, 6, 15, 11, 16, 8, 5, 12, 7, 14, 19] # address bit order..?
byte_order =    [2, 0, 4, 5, 7, 6, 3, 1] # byte bit order