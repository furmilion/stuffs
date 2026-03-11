from funcs import clamp  # external import for clamp function

try:
    import numpy as np

    NUMPY = True
except ImportError:
    print("NumPy not found.\nIt is recommended to install NumPy for a speed boost.")
    NUMPY = False


class WaveWriter:
    def __init__(this,
        channels=1,  # default channel amount
        bitdepth=8,  # default bit depth
        chunks: dict | None = None,  # a dict of additional chunks besides the very basic required ones
        data: list | bytearray | np.ndarray | bytes | bytearray | None = None,  # the data itself
    ):
        this.data = data if data and isinstance(data, (list, tuple, np.ndarray, bytes, bytearray)) else [0] # can also be directly accessed from within the class,
                                          # and is really the only way to alter data after class creation;
                                          # todo: use numpy arrays if available to speed things up
                                          # and because python has no alternative of C's "(int)1.0";
                                          # maybe even require numpy
        this.channels = channels if channels and isinstance(channels, int) else 1  # we don't allow non-int here
        this.bitdepth = bitdepth if bitdepth and isinstance(bitdepth, int) else 8  # ditto
        this.chunks = chunks if chunks and isinstance(chunks, dict) else {}


    def set_channels(this, channels) -> None:
        if isinstance(this.channels, int):
            this.channels = channels & ((1 << 32) - 1)
            return
        else:
            raise ValueError("channels must be an integer!")
    def get_channels(this) -> int:
        return this.channels


    def set_depth(this, bitdepth) -> None:
        if isinstance(bitdepth, int):
            match bitdepth:
                case 8 | 16 | 24 | 32:
                    this.bitdepth = bitdepth
                    return
                case _:
                    raise ValueError("bit depth must be a multiple of 8 and must match any of [8, 16, 24, 32]")
        elif isinstance(bitdepth, (float, str)):
            match bitdepth:
                case 32.0 | 64.0 | "32f" | "64f" | "f32" | "f64":
                    this.bitdepth = bitdepth
                    return
                case _:
                    raise ValueError("bit depth must be either one of [32.0, '32f', 64.0, '64f']")
    def get_depth(this) -> int | float:
        return this.bitdepth


    def add_chunk(this, chunk = "chnk", data: list | bytearray | np.ndarray | None = None) -> None:
        if not data:
            raise ValueError("there must be at least *some* data")
        chunk = str(chunk)[:4] if not isinstance(chunk, str) else chunk[:4]
        chunk += " " * (4 - len(chunk))
        # some shady magic to convert all chunk data to bytes goes here
        this.chunks[chunk] = data
    def get_chunk(this, chunk) -> bytes:
        # check for if chunk name is a string and if not then converting and padding/cutting down to string length 4 goes here
        if chunk in this.chunks:
            return this.chunks[chunk]
        else:
            raise ValueError(f"chunk {chunk} does not exist")

    def set_data(this, data: list | tuple | np.ndarray | bytes | bytearray | None = None):
        if isinstance(data, (list, tuple, np.ndarray, bytes, bytearray)):
            this.data = list(data) if not NUMPY else np.array(data)
            # some shady code that decompresses data into single bytes when no numpy goes here
        else:
            raise ValueError("Data must be one of the following types, [list, tuple, numpy.ndarray, bytes, bytearray]")
    def get_data(this):
        return this.data

    def write_file(this, path: str = r".\output.wav"):
        # write logic goes here
        ...