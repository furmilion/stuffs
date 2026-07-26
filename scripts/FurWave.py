from funcs import clamp  # external import for clamp function
from funcs import _
import struct
import math
from typing import Union, List, Tuple, Dict, Optional, Any#, BinaryIO

FurWaveVersion = "1.0"

try:
    import numpy as np
    # >'np' in the try block with 'except ImportError' should also be defined in the except block
    # no pycharm, no.
    NUMPY = True
except ImportError:
    print("NumPy not found.\nIt is recommended to install NumPy for a speed boost.")
    NUMPY = False


class WaveWriter:
    # WAV file format constants
    RIFF_HEADER = b'RIFF'
    WAVE_HEADER = b'WAVE'
    FMT_CHUNK = b'fmt '
    DATA_CHUNK = b'data'

    # Supported formats
    SUPPORTED_INT_DEPTHS = [8, 16, 24, 32]
    SUPPORTED_FLOAT_DEPTHS = [32, 64]
    # todo: will we ever support Microsoft ADPCM?

    # NumPy dtype mapping for packed data
    NUMPY_DTYPE_MAP = {
        8: np.uint8,  # 8-bit is unsigned in WAV
        16: np.int16,  # 16-bit is signed
        24: None,  # 24-bit needs special handling (no native dtype);
                   # would've been funny if C had an alias for this, I'd imagine it being "short long"
        32: np.int32,  # 32-bit is signed
        32.0: np.float32,  # 32-bit float
        64.0: np.float64,  # 64-bit float
    }

    def __init__(
            self,
            channels: int = 1,
            samplerate: int = 44100,
            bitdepth: Union[int, float, str] = 16,
            chunks: Optional[Dict[bytes, Any]] = None,
            data: Optional[Union[List, Tuple, np.ndarray, bytes, bytearray]] = None,
            packed: bool = False
            ):
        """
        Initialize a WAV file writer.

        Args:
            channels: Number of audio channels (1=mono, 2=stereo, etc.)
            samplerate: Sample rate in Hz (e.g., 44100, 48000)
            bitdepth: Bit depth (8, 16, 24, 32 for int; 32.0, '32f', 64.0, '64f' for float)
            chunks: Dictionary of additional chunks (e.g., cue points)
            data: Audio data samples (can be packed multi-byte values if packed=True or if detected automatically)
            packed: If True, data contains packed multi-byte values (e.g., [65535, 32768] for 16-bit)
        """
        self.channels = channels if isinstance(channels, int) and channels > 0 else 1
        self.samplerate = samplerate if isinstance(samplerate, int) and samplerate > 0 else 44100
        self.bitdepth = self._validate_bitdepth(bitdepth)
        self.chunks = chunks if chunks and isinstance(chunks, dict) else {}
        self.packed = packed or (max(data) > 255 if data is not None else False)

        # Determine audio format
        self._is_float = isinstance(self.bitdepth, float) or (
                    isinstance(self.bitdepth, str) and 'f' in str(self.bitdepth))
        self._bytes_per_sample = self._get_bytes_per_sample()
        self._fmt_code = self._get_format_code()

        # Initialize data
        self.data = self._initialize_data(data)

    def _validate_bitdepth(self, bitdepth: Union[int, float, str]) -> Union[int, float]:
        """Validate and normalize bit depth."""
        # Handle string formats
        if isinstance(bitdepth, str):
            bitdepth = bitdepth.lower()
            if bitdepth in ['32f', 'f32']:
                return 32.0
            elif bitdepth in ['64f', 'f64']:
                return 64.0
            else:
                try:
                    bitdepth = int(bitdepth)
                except ValueError:
                    raise ValueError(f"Invalid bit depth string: {bitdepth}")

        # Handle integer depths
        if isinstance(bitdepth, int):
            if bitdepth in self.SUPPORTED_INT_DEPTHS:
                return bitdepth
            else:
                raise ValueError(f"Integer bit depth must be one of {self.SUPPORTED_INT_DEPTHS}")

        # Handle float depths
        if isinstance(bitdepth, float):
            if bitdepth in self.SUPPORTED_FLOAT_DEPTHS:
                return bitdepth
            else:
                raise ValueError(f"Float bit depth must be one of {self.SUPPORTED_FLOAT_DEPTHS}")

        raise ValueError(f"Invalid bit depth type: {type(bitdepth)}")

    def _get_bytes_per_sample(self) -> int:
        """Calculate bytes per sample based on bit depth."""
        if self._is_float:
            return int(self.bitdepth) // 8
        else:
            return self.bitdepth // 8 if self.bitdepth != 24 else 3  # 24-bit is special (3 bytes)

    def _get_format_code(self) -> int:
        """Get WAV format code (1=PCM, 3=IEEE float)."""
        return 3 if self._is_float else 1

    def _detect_signed(self, data: np.ndarray) -> bool:
        """Detect if data contains negative values."""
        if NUMPY and isinstance(data, np.ndarray):
            return np.any(data < 0)
        elif isinstance(data, (list, tuple)):
            return any(x < 0 for x in data)
        return False

    def _get_optimal_dtype(self, data: Any) -> Optional[type]:
        """Get optimal NumPy dtype based on data range and bit depth."""
        if not NUMPY:
            return None

        # For packed data, we need to know the target format
        if self.packed:
            # Packed data should be in the native format of the target bit depth
            if self.bitdepth == 8:
                # 8-bit WAV is unsigned
                return np.uint8
            elif self.bitdepth == 16:
                # Check if data has negative values for 16-bit
                if self._detect_signed(data):
                    return np.int16
                else:
                    return np.uint16
            elif self.bitdepth == 24 or (self.bitdepth == 32 and not self._is_float):
                # 24-bit has no native dtype, so we use int32, which is also why we merged the check for both
                if self._detect_signed(data):
                    return np.int32
                else:
                    return np.uint32
            elif self.bitdepth == 32.0:
                return np.float32
            elif self.bitdepth == 64.0:
                return np.float64
        else:
            # For unpacked data (individual bytes), always use uint8
            return np.uint8

        return None

    def _pack_samples(self, data: np.ndarray) -> np.ndarray:
        """
        Pack multi-byte samples into individual bytes.
        Test: [65535, 32768] (16-bit) -> [255, 255, 128, 0] (bytes)
        """
        if not NUMPY:
            # Without NumPy, we'd need to do manual packing (slow)
            result = bytearray()
            # bytes_per = self._bytes_per_sample

            for sample in data:
                if self._is_float:
                    # For float, we need to pack differently
                    if self.bitdepth == 32.0:
                        result.extend(struct.pack('<f', float(sample)))
                    else:
                        result.extend(struct.pack('<d', float(sample)))
                else:
                    # For integers
                    if self.bitdepth == 8:
                        # 8-bit is already a byte
                        result.append(int(sample) & 0xFF)
                    elif self.bitdepth == 16:
                        # 16-bit to 2 bytes (little-endian)
                        sample = int(sample) & 0xFFFF
                        result.append(sample & 0xFF)
                        result.append((sample >> 8) & 0xFF)
                    elif self.bitdepth == 24:
                        # 24-bit to 3 bytes
                        sample = int(sample) & 0xFFFFFF
                        result.append(sample & 0xFF)
                        result.append((sample >> 8) & 0xFF)
                        result.append((sample >> 16) & 0xFF)
                    elif self.bitdepth == 32:
                        # 32-bit to 4 bytes
                        sample = int(sample) & 0xFFFFFFFF
                        for _ in range(4):
                            result.append(sample & 0xFF)
                            sample >>= 8
            return np.frombuffer(result, dtype=np.uint8)

        # With NumPy, use efficient view casting
        if self._is_float:
            # For float, we need to use proper dtype
            if self.bitdepth == 32.0:
                return data.astype(np.float32).view(np.uint8)
            else:
                return data.astype(np.float64).view(np.uint8)
        else:
            # For integers, determine the appropriate dtype
            if self.bitdepth == 8:
                # 8-bit is already bytes
                return data.astype(np.uint8)
            elif self.bitdepth == 16:
                # For 16-bit, check if we need signed or unsigned
                if np.any(data < 0):
                    # Use int16 for signed
                    return data.astype(np.int16).view(np.uint8)
                else:
                    # Use uint16 for unsigned
                    return data.astype(np.uint16).view(np.uint8)
            elif self.bitdepth == 24:
                # 24-bit needs special handling - convert to int32 first
                # Then view as 3-byte chunks (but NumPy can't do 3-byte views directly)
                # So we'll do it manually but efficiently
                int32_data = data.astype(np.int32)
                # Reshape to add a dimension for bytes
                bytes_data = np.zeros(len(int32_data) * 3, dtype=np.uint8)
                for i, val in enumerate(int32_data):
                    val = val & 0xFFFFFF
                    bytes_data[i * 3] = val & 0xFF
                    bytes_data[i * 3 + 1] = (val >> 8) & 0xFF
                    bytes_data[i * 3 + 2] = (val >> 16) & 0xFF
                return bytes_data
            elif self.bitdepth == 32:
                return data.astype(np.int32).view(np.uint8)

    def _initialize_data(self, data: Optional[Any]) -> Any:
        """Initialize the audio data array with proper packing detection."""
        if data is None:
            # Create a silent track (1 second of silence)
            num_samples = self.samplerate * self.channels
            if NUMPY:
                if self.packed:
                    # For packed data, create zeros in the target format
                    dtype = self._get_optimal_dtype(None)
                    if dtype:
                        return np.zeros(num_samples, dtype=dtype)
                    else:
                        return np.zeros(num_samples)
                else:
                    # For unpacked data (bytes), use uint8
                    return np.zeros(num_samples * self._bytes_per_sample, dtype=np.uint8)
            else:
                if self.packed:
                    return [0] * num_samples
                else:
                    return [0] * (num_samples * self._bytes_per_sample)

        if NUMPY:
            # Convert to numpy array if not already
            if not isinstance(data, np.ndarray):
                data = np.array(data)

            # If data is packed, ensure it's in the optimal dtype
            if self.packed:
                optimal_dtype = self._get_optimal_dtype(data)
                if optimal_dtype and data.dtype != optimal_dtype:
                    data = data.astype(optimal_dtype)
                return data
            else:
                # Unpacked data should be uint8
                return data.astype(np.uint8)
        else:
            # Without NumPy, just store as list
            return list(data) if data else []

    # ========== Property getters/setters ==========

    def set_channels(self, channels: int) -> None:
        """Set number of channels."""
        if isinstance(channels, int) and channels > 0:
            self.channels = channels
        else:
            raise ValueError("channels must be a positive integer!")

    def get_channels(self) -> int:
        return self.channels

    def set_samplerate(self, samplerate: int) -> None:
        """Set sample rate."""
        if isinstance(samplerate, int) and samplerate > 0:
            self.samplerate = samplerate
        else:
            raise ValueError("samplerate must be a positive integer!")

    def get_samplerate(self) -> int:
        return self.samplerate

    def set_depth(self, bitdepth: Union[int, float, str]) -> None:
        """Set bit depth."""
        self.bitdepth = self._validate_bitdepth(bitdepth)
        self._is_float = isinstance(self.bitdepth, float)
        self._bytes_per_sample = self._get_bytes_per_sample()
        self._fmt_code = self._get_format_code()

    def get_depth(self) -> Union[int, float]:
        return self.bitdepth

    def set_packed(self, packed: bool) -> None:
        """Set whether data is packed."""
        self.packed = packed

    # ========== Chunk management ==========

    def add_chunk(self, chunk_id: str = "chnk", data: Union[List, bytearray, np.ndarray, bytes, dict] = None) -> None:
        """
        Add a custom chunk to the WAV file.

        Args:
            chunk_id: 4-character chunk ID (will be padded/truncated to 4 chars)
            data: Chunk data (will be converted to bytes)
        """
        if data is None:
            raise ValueError("Chunk data cannot be None")

        # Normalize chunk ID to 4 bytes
        chunk_id = str(chunk_id).encode('ascii', errors='replace')[:4]
        if len(chunk_id) < 4:
            chunk_id = chunk_id + b' ' * (4 - len(chunk_id))

        # Convert data to bytes
        if isinstance(data, (bytes, bytearray)):
            chunk_data = bytes(data)
        elif isinstance(data, (list, tuple, np.ndarray)):
            if NUMPY and isinstance(data, np.ndarray):
                chunk_data = data.tobytes()
            else:
                # Assume list of integers
                chunk_data = bytes(data)
        elif isinstance(data, dict):
            # For structured chunks like cue points, we'll handle specially
            chunk_data = self._encode_cue_chunk(data) if chunk_id == b'cue ' else bytes(str(data), 'ascii')
        elif isinstance(data, str):
            chunk_data = data.encode('ascii')
        else:
            raise ValueError(f"Unsupported chunk data type: {type(data)}")

        self.chunks[chunk_id] = chunk_data

    def _encode_cue_chunk(self, cue_data: dict) -> bytes:
        """
        Encode cue point data according to WAV specification.

        Expected format:
        {
            'points': [
                {'id': 1, 'position': 0, 'chunk_id': b'data', 'chunk_start': 0, 'block_start': 0, 'sample_offset': 0},
                ...
            ]
        }
        """
        if 'points' not in cue_data:
            return b''

        points = cue_data['points']
        num_cues = len(points)

        # Cue chunk structure:
        #   dwCuePoints (4 bytes) - Number of cue points
        #   For each point:
        #     dwName (4 bytes) - Cue point ID
        #     dwPosition (4 bytes) - Position in sample frames
        #     fccChunk (4 bytes) - Chunk ID (usually 'data')
        #     dwChunkStart (4 bytes) - Byte offset of chunk
        #     dwBlockStart (4 bytes) - Block start (usually 0)
        #     dwSampleOffset (4 bytes) - Sample offset within block

        result = struct.pack('<I', num_cues)

        for point in points:
            result += struct.pack(
                '<II4sIII',
                point.get('id', 0),
                point.get('position', 0),
                point.get('chunk_id', b'data').encode() if isinstance(point.get('chunk_id'), str) else point.get(
                    'chunk_id', b'data'
                    ),
                point.get('chunk_start', 0),
                point.get('block_start', 0),
                point.get('sample_offset', 0)
            )

        return result

    def get_chunk(self, chunk_id: str) -> bytes:
        """Get a chunk's data by ID."""
        chunk_id = chunk_id.encode('ascii', errors='replace')[:4]
        if len(chunk_id) < 4:
            chunk_id = chunk_id + b' ' * (4 - len(chunk_id))

        if chunk_id in self.chunks:
            return self.chunks[chunk_id]
        else:
            raise KeyError(f"Chunk {chunk_id} does not exist")

    def remove_chunk(self, chunk_id: str) -> None:
        """Remove a chunk by ID."""
        chunk_id = chunk_id.encode('ascii', errors='ignore')[:4]
        if len(chunk_id) < 4:
            chunk_id = chunk_id + b' ' * (4 - len(chunk_id))

        if chunk_id in self.chunks:
            del self.chunks[chunk_id]

    def set_smpl_chunk(self, manufacturer=0, product=0, sample_period=0,
                       midi_unity_note=0, midi_pitch_fraction=0, smpte_format=0, smpte_offset=0,
                       sample_loop_count=1, sampler_data_size=0, sampler_data=None,
                       loop_identifiers=None, loop_types=None, loop_starts=None, loop_ends=None,
                       fraction=0, play_count=0):
        """
        Wrapper for add_chunk(). For more info: https://wavref.til.cafe/chunk/smpl/
        Loop types:
            - 0: forwards
            - 1: ping-pong/ idirectional
            - 2: reverse
        """
        if loop_identifiers is None:
            loop_identifiers = [0 for _ in range(sample_loop_count)] if sample_loop_count else None
        else:
            while len(loop_identifiers) < sample_loop_count:
                loop_identifiers.append(0)
        sample_loop_count = min(len(loop_starts), len(loop_ends))
        if loop_types is None:
            loop_types = [0 for _ in range(sample_loop_count)] if sample_loop_count else None
        else:
            while len(loop_types) < sample_loop_count:
                loop_types.append(0)

        if loop_starts is None:
            loop_starts = [0 for _ in range(sample_loop_count)] if sample_loop_count else None
        else:
            while len(loop_starts) < sample_loop_count:
                loop_starts.append(0)

        if loop_ends is None:
            loop_ends = [0 for _ in range(sample_loop_count)] if sample_loop_count else None
        else:
            while len(loop_ends) < sample_loop_count:
                loop_ends.append(0)

        if sampler_data is None:
            sampler_data = [0 for _ in range(sampler_data_size)] if sampler_data_size else None
        else:
            while len(sampler_data) < sampler_data_size:
                sampler_data.append(0)

        data = [  # i cant be bothered to use struct here so deal with this lmao
            (manufacturer >>  0) & 0xFF,        (manufacturer >>  8) & 0xFF,
            (manufacturer >> 16) & 0xFF,        (manufacturer >> 24) & 0xFF,
            (product >>  0) & 0xFF,             (product >>  8) & 0xFF,
            (product >> 16) & 0xFF,             (product >> 24) & 0xFF,
            (sample_period >>  0) & 0xFF,       (sample_period >>  8) & 0xFF,
            (sample_period >> 16) & 0xFF,       (sample_period >> 24) & 0xFF,

            (midi_unity_note >>  0) & 0xFF,     (midi_unity_note >>  8) & 0xFF,
            (midi_unity_note >> 16) & 0xFF,     (midi_unity_note >> 24) & 0xFF,
            (midi_pitch_fraction >>  0) & 0xFF, (midi_pitch_fraction >>  8) & 0xFF,
            (midi_pitch_fraction >> 16) & 0xFF, (midi_pitch_fraction >> 24) & 0xFF,
            (smpte_format >>  0) & 0xFF,        (smpte_format >>  8) & 0xFF,
            (smpte_format >> 16) & 0xFF,        (smpte_format >> 24) & 0xFF,
            (smpte_offset >>  0) & 0xFF,        (smpte_offset >>  8) & 0xFF,
            (smpte_offset >> 16) & 0xFF,        (smpte_offset >> 24) & 0xFF,

            (sample_loop_count >>  0) & 0xFF,   (sample_loop_count >>  8) & 0xFF,
            (sample_loop_count >> 16) & 0xFF,   (sample_loop_count >> 24) & 0xFF,
            (sampler_data_size >>  0) & 0xFF,   (sampler_data_size >>  8) & 0xFF,
            (sampler_data_size >> 16) & 0xFF,   (sampler_data_size >> 24) & 0xFF,

        ]
        data.extend(sampler_data) if sampler_data else _()
        for index in range(sample_loop_count):  # add sample loops
            data.extend(
                [
                    (loop_identifiers[index] >>  0) & 0xFF, (loop_identifiers[index] >>  8) & 0xFF,
                    (loop_identifiers[index] >> 16) & 0xFF, (loop_identifiers[index] >> 24) & 0xFF,
                    (loop_types[index] >>  0) & 0xFF,       (loop_types[index] >>  8) & 0xFF,
                    (loop_types[index] >> 16) & 0xFF,       (loop_types[index] >> 24) & 0xFF,
                    (loop_starts[index] >>  0) & 0xFF,      (loop_starts[index] >>  8) & 0xFF,
                    (loop_starts[index] >> 16) & 0xFF,      (loop_starts[index] >> 24) & 0xFF,
                    (loop_ends[index] >>  0) & 0xFF,        (loop_ends[index] >>  8) & 0xFF,
                    (loop_ends[index] >> 16) & 0xFF,        (loop_ends[index] >> 24) & 0xFF,
                ]
            )
        data.extend(
            [
                (fraction >> 24) & 0xFF,   (fraction >> 16) & 0xFF,
                (fraction >>  8) & 0xFF,   (fraction >>  0) & 0xFF,
                (play_count >> 24) & 0xFF, (play_count >> 16) & 0xFF,
                (play_count >>  8) & 0xFF, (play_count >>  0) & 0xFF,
            ]
        )
        self.add_chunk("smpl", data)

    def remove_smpl_chunk(self):
        self.remove_chunk("smpl")

    # ========== Data management ==========

    def set_data(self, data: Union[List, Tuple, np.ndarray, bytes, bytearray], packed: Optional[bool] = None) -> None:
        """
        Set the audio data.

        Args:
            data: Audio data
            packed: If provided, overrides the instance's packed setting
        """
        if packed is not None:
            self.packed = packed

        self.data = self._initialize_data(data)

    def get_data(self) -> Any:
        return self.data

    def get_packed_data(self) -> Optional[np.ndarray]:
        """Get the data in packed format (multi-byte samples)."""
        if not NUMPY:
            # Without NumPy, we can't easily reconstruct packed data
            return None

        if self.packed:
            # Already packed
            return self.data
        else:
            # Need to pack the byte data back into multi-byte samples
            bytes_per = self._bytes_per_sample
            if len(self.data) % bytes_per != 0:
                return None

            # Reshape and convert
            if self._is_float:
                if self.bitdepth == 32.0:
                    return self.data.view(np.float32)
                else:
                    return self.data.view(np.float64)
            else:
                if self.bitdepth == 8:
                    return self.data
                elif self.bitdepth == 16:
                    return self.data.view(np.int16)
                elif self.bitdepth == 24:
                    # 24-bit needs special handling
                    result = np.zeros(len(self.data) // 3, dtype=np.int32)
                    for i in range(len(result)):
                        val = (int(self.data[i * 3]) |
                               (int(self.data[i * 3 + 1]) << 8) |
                               (int(self.data[i * 3 + 2]) << 16))
                        # Sign extend if necessary
                        if val & 0x800000:
                            val |= ~0xFFFFFF
                        result[i] = val
                    return result
                elif self.bitdepth == 32:
                    return self.data.view(np.int32)

    def generate_sine(self, frequency: float = 440.0, duration: float = 1.0, amplitude: float = 0.5) -> None:
        """
        Generate a sine wave.

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
        """
        amplitude = clamp(amplitude, 0.0, 1.0)
        num_samples = int(duration * self.samplerate) * self.channels

        if NUMPY:
            if self.packed:
                # Generate packed samples directly
                t = np.linspace(0, duration, num_samples // self.channels, endpoint=False)
                if self._is_float:
                    # For float formats, generate float samples
                    mono = amplitude * np.sin(2 * np.pi * frequency * t)
                    if self.channels > 1:
                        mono = np.repeat(mono, self.channels)

                    # Scale to appropriate range for the format
                    if self.bitdepth == 32.0:
                        self.data = mono.astype(np.float32)
                    else:
                        self.data = mono.astype(np.float64)
                else:
                    # For integer formats
                    mono = amplitude * np.sin(2 * np.pi * frequency * t)
                    if self.channels > 1:
                        mono = np.repeat(mono, self.channels)

                    # Scale to integer range
                    if self.bitdepth == 8:
                        # 8-bit is unsigned, range 0-255
                        self.data = ((mono * 127) + 128).astype(np.uint8)
                    elif self.bitdepth == 16:
                        # 16-bit signed range -32768 to 32767
                        self.data = (mono * 32767).astype(np.int16)
                    elif self.bitdepth == 24:
                        # 24-bit signed range -8388608 to 8388607
                        self.data = (mono * 8388607).astype(np.int32)
                    elif self.bitdepth == 32:
                        # 32-bit signed range -2147483648 to 2147483647
                        self.data = (mono * 2147483647).astype(np.int32)
            else:
                # Generate unpacked bytes directly
                t = np.linspace(0, duration, num_samples // self.channels, endpoint=False)
                mono = amplitude * np.sin(2 * np.pi * frequency * t)
                if self.channels > 1:
                    mono = np.repeat(mono, self.channels)

                # Convert to bytes
                if self._is_float:
                    if self.bitdepth == 32.0:
                        bytes_data = mono.astype(np.float32).tobytes()
                    else:
                        bytes_data = mono.astype(np.float64).tobytes()
                else:
                    if self.bitdepth == 8:
                        bytes_data = ((mono * 127) + 128).astype(np.uint8).tobytes()
                    elif self.bitdepth == 16:
                        bytes_data = (mono * 32767).astype(np.int16).tobytes()
                    elif self.bitdepth == 24:
                        # 24-bit needs special handling
                        int32_data = (mono * 8388607).astype(np.int32)
                        bytes_data = bytearray()
                        for val in int32_data:
                            val = val & 0xFFFFFF
                            bytes_data.append(val & 0xFF)
                            bytes_data.append((val >> 8) & 0xFF)
                            bytes_data.append((val >> 16) & 0xFF)
                    else:
                        bytes_data = (mono * 2147483647).astype(np.int32).tobytes()

                self.data = np.frombuffer(bytes_data, dtype=np.uint8)
        else:
            # Without NumPy, generate samples manually
            self.data = []
            samples_per_channel = int(duration * self.samplerate)

            for i in range(samples_per_channel):
                t = i / self.samplerate
                sample = amplitude * math.sin(2 * math.pi * frequency * t)

                if self.packed:
                    # Store packed samples
                    for _ in range(self.channels):
                        self.data.append(sample)
                else:
                    # Convert to bytes
                    if self._is_float:
                        if self.bitdepth == 32.0:
                            self.data.extend(struct.pack('<f', sample))
                        else:
                            self.data.extend(struct.pack('<d', sample))
                    else:
                        if self.bitdepth == 8:
                            self.data.append(int((sample * 127) + 128) & 0xFF)
                        elif self.bitdepth == 16:
                            sample_int = int(sample * 32767) & 0xFFFF
                            self.data.append(sample_int & 0xFF)
                            self.data.append((sample_int >> 8) & 0xFF)
                        elif self.bitdepth == 24:
                            sample_int = int(sample * 8388607) & 0xFFFFFF
                            self.data.append(sample_int & 0xFF)
                            self.data.append((sample_int >> 8) & 0xFF)
                            self.data.append((sample_int >> 16) & 0xFF)
                        else:
                            sample_int = int(sample * 2147483647) & 0xFFFFFFFF
                            for _ in range(4):
                                self.data.append(sample_int & 0xFF)
                                sample_int >>= 8

    def generate_silence(self, duration: float = 1.0) -> None:
        """Generate silence."""
        num_samples = int(duration * self.samplerate) * self.channels

        if NUMPY:
            if self.packed:
                # Create zeros in the appropriate format
                if self._is_float:
                    if self.bitdepth == 32.0:
                        self.data = np.zeros(num_samples, dtype=np.float32)
                    else:
                        self.data = np.zeros(num_samples, dtype=np.float64)
                else:
                    if self.bitdepth == 8:
                        # 8-bit silence is 128 (midpoint)
                        self.data = np.full(num_samples, 128, dtype=np.uint8)
                    elif self.bitdepth == 16:
                        self.data = np.zeros(num_samples, dtype=np.int16)
                    elif self.bitdepth == 24:
                        self.data = np.zeros(num_samples, dtype=np.int32)
                    else:
                        self.data = np.zeros(num_samples, dtype=np.int32)
            else:
                # Create zero bytes
                bytes_per = self._bytes_per_sample
                if self.bitdepth == 8:
                    # 8-bit silence is 128
                    self.data = np.full(num_samples * bytes_per, 128, dtype=np.uint8)
                else:
                    self.data = np.zeros(num_samples * bytes_per, dtype=np.uint8)
        else:
            if self.packed:
                self.data = [0.0] * num_samples
            else:
                bytes_per = self._bytes_per_sample
                if self.bitdepth == 8:
                    self.data = [128] * (num_samples * bytes_per)
                else:
                    self.data = [0] * (num_samples * bytes_per)

    # ========== Sample conversion ==========

    def _samples_to_bytes(self) -> bytes:
        """Convert samples to bytes according to bit depth and format."""
        if NUMPY and isinstance(self.data, np.ndarray):
            if self.packed:
                # Pack the data into bytes
                packed_data = self._pack_samples(self.data)
                return bytes(packed_data)
            else:
                # Data is already bytes
                return bytes(self.data)
        else:
            # Manual conversion without NumPy
            result = bytearray()

            if self.packed:
                # Pack multi-byte samples
                for sample in self.data:
                    if self._is_float:
                        if self.bitdepth == 32.0:
                            result.extend(struct.pack('<f', float(sample)))
                        else:
                            result.extend(struct.pack('<d', float(sample)))
                    else:
                        if self.bitdepth == 8:
                            result.append(int(sample) & 0xFF)
                        elif self.bitdepth == 16:
                            sample = int(sample) & 0xFFFF
                            result.append(sample & 0xFF)
                            result.append((sample >> 8) & 0xFF)
                        elif self.bitdepth == 24:
                            sample = int(sample) & 0xFFFFFF
                            result.append(sample & 0xFF)
                            result.append((sample >> 8) & 0xFF)
                            result.append((sample >> 16) & 0xFF)
                        else:
                            sample = int(sample) & 0xFFFFFFFF
                            for _ in range(4):
                                result.append(sample & 0xFF)
                                sample >>= 8
            else:
                # Data is already bytes
                result.extend(self.data)

            return bytes(result)

    # ========== File writing ==========

    def write_file(self, path: str = r".\output.wav", overwrite: bool | int = False) -> None:
        """
        Write the WAV file to disk.

        Args:
            path: Output file path
        """
        # Prepare audio data
        audio_data = self._samples_to_bytes()
        data_size = len(audio_data)

        # Calculate chunk sizes
        fmt_size = 16  # Standard PCM fmt chunk size
        if self._is_float:
            fmt_size = 18  # Extra format bytes for float

        # Build the WAV file
        with open(path, 'wb') as f:
            # RIFF header
            f.write(self.RIFF_HEADER)

            # File size (4 bytes) = total size - 8
            file_size = 4 + (8 + fmt_size) + (8 + data_size)
            for chunk_data in self.chunks.values():
                file_size += 8 + len(chunk_data)
            f.write(struct.pack('<I', file_size))

            f.write(self.WAVE_HEADER)

            # fmt chunk
            f.write(self.FMT_CHUNK)
            f.write(struct.pack('<I', fmt_size))

            # Audio format (1=PCM, 3=IEEE float)
            f.write(struct.pack('<H', self._fmt_code))
            f.write(struct.pack('<H', self.channels))
            f.write(struct.pack('<I', self.samplerate))

            # Byte rate = samplerate * channels * bytes_per_sample
            byte_rate = self.samplerate * self.channels * self._bytes_per_sample
            f.write(struct.pack('<I', byte_rate))

            # Block align = channels * bytes_per_sample
            block_align = self.channels * self._bytes_per_sample
            f.write(struct.pack('<H', block_align))

            # Bits per sample
            bits_per_sample = self._bytes_per_sample * 8
            if self.bitdepth == 24:
                bits_per_sample = 24
            f.write(struct.pack('<H', bits_per_sample))

            # Extra format bytes for float
            if self._is_float:
                f.write(struct.pack('<H', 0))  # No extra data

            # Additional chunks (before data)
            for chunk_id, chunk_data in self.chunks.items():
                if chunk_id != b'data':  # data chunk handled separately
                    f.write(chunk_id)
                    f.write(struct.pack('<I', len(chunk_data)))
                    f.write(chunk_data)

            # data chunk
            f.write(self.DATA_CHUNK)
            f.write(struct.pack('<I', data_size))
            f.write(audio_data)

    # ========== Utility methods ==========

    def get_duration(self) -> float:
        """Get the duration of the audio in seconds."""
        if NUMPY and isinstance(self.data, np.ndarray):
            if self.packed:
                num_samples = len(self.data)
            else:
                num_samples = len(self.data) // self._bytes_per_sample
        else:
            if self.packed:
                num_samples = len(self.data)
            else:
                num_samples = len(self.data) // self._bytes_per_sample

        if self.channels > 0:
            num_frames = num_samples // self.channels
            return num_frames / self.samplerate
        return 0.0

    def get_info(self) -> dict:
        """Get information about the WAV file."""
        return {
            'channels': self.channels,
            'samplerate': self.samplerate,
            'bitdepth': self.bitdepth,
            'is_float': self._is_float,
            'packed': self.packed,
            'duration': self.get_duration(),
            'samples': len(self.data) if self.packed else len(self.data) // self._bytes_per_sample,
            'bytes': len(self.data),
            'format_code': self._fmt_code,
            'bytes_per_sample': self._bytes_per_sample,
            'num_chunks': len(self.chunks)
        }

    # ========== System ==========
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self


# ========== Testing ==========

if __name__ == "__main__":
    print(f"NumPy available: {NUMPY}")
    print("=" * 50)

    # Test 1: Packed 16-bit data (shows the [65535, 32768] -> bytes conversion)
    print("\nTest 1: Packed 16-bit data")
    wav1 = WaveWriter(channels=1, samplerate=44100, bitdepth=16, packed=True)

    # Create packed 16-bit samples
    if NUMPY:
        # Generate a simple sine wave as packed 16-bit values
        t = np.linspace(0, 1, 44100, endpoint=False)
        # 16-bit range: -32768 to 32767
        samples = (32767 * np.sin(2 * np.pi * 440 * t)).astype(np.int16)
        wav1.set_data(samples)

        print(f"Packed data shape: {wav1.data.shape}")
        print(f"Packed data dtype: {wav1.data.dtype}")
        print(f"First 5 packed samples: {wav1.data[:5]}")

        # Show the byte conversion
        bytes_data = wav1._samples_to_bytes()
        print(f"Converted to bytes: first 10 bytes: {list(bytes_data[:10])}")
        print(f"[65535, 32768] should become [255, 255, 128, 0] in 16-bit mode")
    else:
        # Without NumPy, use list of packed values
        samples = []
        for i in range(44100):
            t = i / 44100
            sample = int(32767 * math.sin(2 * math.pi * 440 * t))
            samples.append(sample)
        wav1.set_data(samples)

    wav1.write_file("packed_16bit.wav")
    print(f"Created packed_16bit.wav - Info: {wav1.get_info()}")

    # Test 2: Automatic signed/unsigned detection
    print("\nTest 2: Automatic signed/unsigned detection")

    # Mixed positive/negative data (should detect signed)
    mixed_data = [-32768, -16384, 0, 16384, 32767]
    wav2 = WaveWriter(channels=1, samplerate=44100, bitdepth=16, packed=True)
    wav2.set_data(mixed_data)

    if NUMPY:
        print(f"Mixed data dtype: {wav2.data.dtype}")  # Should be int16
        print(f"Contains negative: {np.any(wav2.data < 0)}")

    # All positive data (could use unsigned)
    positive_data = [0, 16384, 32767, 49152, 65535]
    wav3 = WaveWriter(channels=1, samplerate=44100, bitdepth=16, packed=True)
    wav3.set_data(positive_data)

    if NUMPY:
        print(f"Positive data dtype: {wav3.data.dtype}")  # Should be uint16
        print(f"Contains negative: {np.any(wav3.data < 0)}")
    wav2.write_file("sign_test_s16.wav")
    wav3.write_file("sign_test_u16.wav")

    # Test 3: Unpacked vs Packed comparison
    print("\nTest 3: Unpacked vs Packed comparison")

    # Create the same audio in both formats
    freq = 440
    duration = 0.1  # Short duration for Test

    # Packed version
    packed_wav = WaveWriter(channels=1, samplerate=44100, bitdepth=16, packed=True)
    packed_wav.generate_sine(freq, duration, 0.5)

    # Unpacked version (bytes)
    unpacked_wav = WaveWriter(channels=1, samplerate=44100, bitdepth=16, packed=True)
    packed_wav.generate_sine(freq, duration, 0.5)

    # Unpacked version (bytes)
    unpacked_wav = WaveWriter(channels=1, samplerate=44100, bitdepth=16, packed=False)
    unpacked_wav.generate_sine(freq, duration, 0.5)

    print(f"Packed data length: {len(packed_wav.data)} samples")
    print(f"Unpacked data length: {len(unpacked_wav.data)} bytes")
    print(f"Ratio: {len(unpacked_wav.data) / len(packed_wav.data)} bytes per sample")

    if NUMPY:
        print(f"\nPacked data type: {packed_wav.data.dtype}")
        print(f"Unpacked data type: {unpacked_wav.data.dtype}")

        # Demonstrate packing/unpacking
        print(f"\nFirst 5 packed samples: {packed_wav.data[:5]}")

        # Get back packed data from unpacked version
        reconstructed = unpacked_wav.get_packed_data()
        if reconstructed is not None:
            print(f"Reconstructed packed data (first 5): {reconstructed[:5]}")

    # Test 4: Different bit depths with packed data
    print("\nTest 4: Various bit depths with packed data")

    depths = [8, 16, 24, 32, 32.0]
    for depth in depths:
        wav = WaveWriter(channels=1, samplerate=44100, bitdepth=depth, packed=True)
        wav.generate_sine(440, 0.1, 0.5)

        depth_str = f"{depth}f" if isinstance(depth, float) else str(depth)
        print(f"{depth_str:6} bit - Data shape: {wav.data.shape if NUMPY else len(wav.data)}")

        if NUMPY:
            print(f"          Data dtype: {wav.data.dtype}")
        wav.write_file(f"depth_test_{depth}.wav")

    print("\nAll Test files created successfully!")






# ps да, мне платят за количество строк