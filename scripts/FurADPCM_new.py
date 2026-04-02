"""
FurADPCM - Complete implementation with F1, F2, and F3 formats
"""

import math
import struct
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


# ============================================================================
# Enums and Configuration
# ============================================================================

class BlockFormat(Enum):
    F1 = 0xF1  # 8-step table, 2 samples/byte
    F2 = 0xF2  # 4-step table with multiplier, 2 samples/byte
    F3 = 0xF3  # Variable step size, 8 samples/byte (bit-packed)


class StepType(Enum):
    LIN4 = 0  # Linear +4 each step
    LIN16 = 1  # Linear +16 each step
    POW2 = 2  # Power of 2: 2^step
    POW3 = 3  # Power of 3: 3^step


class StepSizeStrategy(Enum):
    PEAK = "peak"
    RMS = "rms"
    ADAPTIVE = "adaptive"


class Endianness(Enum):
    BIG = "big"
    LITTLE = "little"


# ============================================================================
# Step Tables and Calculators
# ============================================================================

class StepCalculator:
    """Calculate step sizes for different formats"""

    # F1 step tables
    F1_8BIT = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
    F1_16BIT = [0x4000, 0x2000, 0x1000, 0x800, 0x400, 0x200, 0x100, 0x80]

    # F2 base steps
    F2_BASE = [0x0F, 0x07, 0x03, 0x01]

    @staticmethod
    def get_f2_scaled_steps(multiplier: int) -> List[int]:
        """Get scaled step table for F2"""
        return [step * multiplier for step in StepCalculator.F2_BASE]

    @staticmethod
    def get_f3_step(step_type: StepType, step_num: int, max_step: int = 1024) -> int:
        """Calculate step size for F3 based on step type"""
        if step_type == StepType.LIN4:
            return min(step_num * 4, max_step)
        elif step_type == StepType.LIN16:
            return min(step_num * 16, max_step)
        elif step_type == StepType.POW2:
            return min(2 ** step_num, max_step)
        elif step_type == StepType.POW3:
            return min(3 ** step_num, max_step)
        else:
            return 4

    @staticmethod
    def find_f2_multiplier(
            samples: List[int],
            strategy: StepSizeStrategy = StepSizeStrategy.ADAPTIVE,
            max_val: int = 255
            ) -> int:
        """Find optimal multiplier for F2 encoding"""
        if not samples:
            return 1

        max_abs = max(abs(s) for s in samples)
        max_base = max(StepCalculator.F2_BASE)

        # Peak-based (lower bound)
        peak_mult = max(1, (max_abs + max_base - 1) // max_base)

        if strategy == StepSizeStrategy.PEAK:
            return min(peak_mult, 8)

        # RMS calculation
        rms = math.sqrt(sum(s * s for s in samples) / len(samples))
        rms_mult = max(1, int((rms * 2.5 + max_base - 1) // max_base))

        if strategy == StepSizeStrategy.RMS:
            return min(max(peak_mult, rms_mult), 8)

        # Adaptive: combine with dynamics
        mean = sum(samples) / len(samples)
        variance = sum((s - mean) ** 2 for s in samples) / len(samples)
        std_dev = math.sqrt(variance)
        dynamic_mult = max(1, int((std_dev * 3 + max_base - 1) // max_base))

        # Zero-crossing rate for frequency content
        zero_crossings = 0
        for i in range(1, len(samples)):
            if samples[i] * samples[i - 1] < 0:
                zero_crossings += 1
        zcr = zero_crossings / len(samples)
        freq_factor = max(0.5, 1.0 - zcr)

        # Weighted combination
        candidate = int((rms_mult * 0.4 + dynamic_mult * 0.4 + peak_mult * 0.2) * freq_factor)
        candidate = max(peak_mult, min(candidate, 8))

        return min(candidate, 8)


# ============================================================================
# Abstract Base Classes
# ============================================================================

class BlockEncoder(ABC):
    """Abstract encoder for block formats"""

    @abstractmethod
    def encode(self, samples: List[int], **kwargs) -> Tuple[List[int], Dict[str, Any]]:
        """Encode samples to bytes with metadata"""
        pass


class BlockDecoder(ABC):
    """Abstract decoder for block formats"""

    @abstractmethod
    def decode(self, data: List[int], metadata: Dict[str, Any]) -> List[int]:
        """Decode bytes to samples"""
        pass


# ============================================================================
# F1 Implementation (8-step, 2 samples/byte)
# ============================================================================

class F1Encoder(BlockEncoder):
    """Format 1 encoder - 8-step table, 2 samples per byte"""

    def __init__(self, is_16bit: bool = False):
        self.is_16bit = is_16bit
        self.step_table = StepCalculator.F1_16BIT if is_16bit else StepCalculator.F1_8BIT
        self.max_val = 65535 if is_16bit else 255

    def encode(self, samples: List[int], initial_value: Optional[int] = None) -> Tuple[List[int], Dict[str, Any]]:
        """
        Encode samples to F1 format

        Returns:
            Tuple of (encoded_bytes, metadata)
        """
        if not samples:
            return [], {'initial_value': 0, 'is_16bit': self.is_16bit}

        initial_value = initial_value if initial_value is not None else samples[0]
        current_value = initial_value
        encoded = []

        # Process samples in pairs
        for i in range(0, len(samples), 2):
            byte = 0

            # First sample (upper nibble)
            if i < len(samples):
                diff = samples[i] - current_value
                step_idx, sign = self._quantize_step(diff)
                byte |= (sign << 3) | (step_idx & 0x07)

                # Update current value
                step = self.step_table[step_idx]
                if sign:
                    current_value -= step
                else:
                    current_value += step
                current_value = max(0, min(current_value, self.max_val))

            # Second sample (lower nibble)
            if i + 1 < len(samples):
                diff = samples[i + 1] - current_value
                step_idx, sign = self._quantize_step(diff)
                byte |= ((sign << 3) | (step_idx & 0x07)) << 4

                # Update current value
                step = self.step_table[step_idx]
                if sign:
                    current_value -= step
                else:
                    current_value += step
                current_value = max(0, min(current_value, self.max_val))

            encoded.append(byte)

        return encoded, {
            'initial_value': initial_value,
            'is_16bit': self.is_16bit,
            'format': BlockFormat.F1
        }

    def _quantize_step(self, diff: int) -> Tuple[int, int]:
        """Quantize difference to step index and sign"""
        if diff < 0:
            sign = 1
            abs_diff = -diff
        else:
            sign = 0
            abs_diff = diff

        for idx, step in enumerate(self.step_table):
            if step >= abs_diff:
                return idx, sign

        return len(self.step_table) - 1, sign


class F1Decoder(BlockDecoder):
    """Format 1 decoder"""

    def __init__(self, is_16bit: bool = False):
        self.is_16bit = is_16bit
        self.step_table = StepCalculator.F1_16BIT if is_16bit else StepCalculator.F1_8BIT
        self.max_val = 65535 if is_16bit else 255

    def decode(self, data: List[int], metadata: Dict[str, Any]) -> List[int]:
        """
        Decode F1 data to samples

        Args:
            data: Encoded bytes (without header)
            metadata: Must contain 'initial_value' and 'sample_count'
        """
        initial_value = metadata.get('initial_value', 0)
        sample_count = metadata.get('sample_count', len(data) * 2)

        current_value = initial_value
        samples = []

        for byte in data:
            # Upper nibble (first sample)
            nibble = (byte >> 4) & 0x0F
            step_idx = nibble & 0x07
            sign = (nibble >> 3) & 1

            step = self.step_table[step_idx]
            if sign:
                current_value -= step
            else:
                current_value += step
            current_value = max(0, min(current_value, self.max_val))
            samples.append(current_value)

            if len(samples) >= sample_count:
                break

            # Lower nibble (second sample)
            nibble = byte & 0x0F
            step_idx = nibble & 0x07
            sign = (nibble >> 3) & 1

            step = self.step_table[step_idx]
            if sign:
                current_value -= step
            else:
                current_value += step
            current_value = max(0, min(current_value, self.max_val))
            samples.append(current_value)

            if len(samples) >= sample_count:
                break

        return samples[:sample_count]


# ============================================================================
# F2 Implementation (4-step with multiplier, 2 samples/byte)
# ============================================================================

class F2Encoder(BlockEncoder):
    """Format 2 encoder - 4-step table with multiplier, 2 samples per byte"""

    def __init__(self, is_16bit: bool = False):
        self.is_16bit = is_16bit
        self.max_val = 65535 if is_16bit else 255

    def encode(
            self, samples: List[int],
            multiplier: Optional[int] = None,
            strategy: StepSizeStrategy = StepSizeStrategy.ADAPTIVE
            ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Encode samples to F2 format

        Returns:
            Tuple of (encoded_bytes, metadata)
        """
        if not samples:
            return [], {'multiplier': 1, 'initial_value': 0, 'is_16bit': self.is_16bit}

        # Auto-select multiplier if not provided
        if multiplier is None:
            multiplier = StepCalculator.find_f2_multiplier(samples, strategy, self.max_val)

        scaled_steps = StepCalculator.get_f2_scaled_steps(multiplier)

        initial_value = samples[0]
        current_value = initial_value
        encoded_nibbles = []

        # Encode each sample (skip first as reference)
        for sample in samples[1:]:
            diff = sample - current_value

            # Quantize to nearest step
            step_idx, sign = self._quantize_step(diff, scaled_steps)

            # Store as nibble (sign + 2-bit step index)
            nibble = (sign << 2) | (step_idx & 0x03)
            encoded_nibbles.append(nibble)

            # Update current value
            step = scaled_steps[step_idx]
            if sign:
                current_value -= step
            else:
                current_value += step
            current_value = max(0, min(current_value, self.max_val))

        # Pack nibbles into bytes
        encoded_bytes = []
        for i in range(0, len(encoded_nibbles), 2):
            byte = 0
            if i < len(encoded_nibbles):
                byte |= encoded_nibbles[i] << 4
            if i + 1 < len(encoded_nibbles):
                byte |= encoded_nibbles[i + 1]
            encoded_bytes.append(byte)

        return encoded_bytes, {
            'multiplier': multiplier,
            'initial_value': initial_value,
            'is_16bit': self.is_16bit,
            'format': BlockFormat.F2
        }

    def _quantize_step(self, diff: int, steps: List[int]) -> Tuple[int, int]:
        """Quantize difference to step index and sign"""
        if diff < 0:
            sign = 1
            abs_diff = -diff
        else:
            sign = 0
            abs_diff = diff

        # Find best matching step (smallest that's >= abs_diff)
        for idx, step in enumerate(steps):
            if step >= abs_diff:
                return idx, sign

        return len(steps) - 1, sign


class F2Decoder(BlockDecoder):
    """Format 2 decoder"""

    def __init__(self, is_16bit: bool = False):
        self.is_16bit = is_16bit
        self.max_val = 65535 if is_16bit else 255

    def decode(self, data: List[int], metadata: Dict[str, Any]) -> List[int]:
        """
        Decode F2 data to samples

        Args:
            data: Encoded bytes (without header)
            metadata: Must contain 'multiplier', 'initial_value', and 'sample_count'
        """
        multiplier = metadata.get('multiplier', 1)
        initial_value = metadata.get('initial_value', 0)
        sample_count = metadata.get('sample_count', len(data) * 2 + 1)

        scaled_steps = StepCalculator.get_f2_scaled_steps(multiplier)
        current_value = initial_value
        samples = [initial_value]

        # Extract nibbles
        nibbles = []
        for byte in data:
            nibbles.append((byte >> 4) & 0x0F)
            nibbles.append(byte & 0x0F)

        print(f"samples got: {len(samples)}")
        print(f"nibbles got: {len(nibbles)}")

        # Decode each nibble
        for nibble in nibbles:
            if len(samples) >= sample_count:
                break
            print(f"sharting nibble {nibble}")

            step_idx = nibble & 0x03
            sign = (nibble >> 2) & 1

            step = scaled_steps[step_idx]
            if sign:
                current_value -= step
            else:
                current_value += step
            current_value = max(0, min(current_value, self.max_val))
            samples.append(current_value)

        return samples[:sample_count]


# ============================================================================
# F3 Implementation (Variable step, 8 samples/byte)
# ============================================================================

class F3Encoder(BlockEncoder):
    """Format 3 encoder - Variable step size, 8 samples per byte (bit-packed)"""

    def __init__(self, max_step: int = 1024):
        self.max_step = max_step

    def encode(
            self, samples: List[int],
            step_type: StepType,
            initial_value: Optional[int] = None,
            is_16bit: bool = False
            ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Encode samples to F3 format

        Returns:
            Tuple of (encoded_bytes, metadata)
        """
        if not samples:
            return [], {'initial_value': 0, 'step_type': step_type, 'is_16bit': is_16bit}

        max_val = 65535 if is_16bit else 255
        initial_value = initial_value if initial_value is not None else samples[0]
        current_value = initial_value

        bits = []
        step_num = 0
        is_negative = False

        for sample in samples:
            # Determine direction
            if sample <= current_value:
                if not is_negative:
                    step_num = 0
                is_negative = True
                bits.append(0)
                current_value -= StepCalculator.get_f3_step(step_type, step_num, self.max_step)
            else:
                if is_negative:
                    step_num = 0
                is_negative = False
                bits.append(1)
                current_value += StepCalculator.get_f3_step(step_type, step_num, self.max_step)

            # Clamp to valid range
            current_value = max(0, min(current_value, max_val))
            step_num += 1

        # Pack bits into bytes (MSB first, 8 bits per byte)
        encoded = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j, bit in enumerate(bits[i:i + 8]):
                byte |= bit << (7 - j)
            encoded.append(byte)

        return encoded, {
            'initial_value': initial_value,
            'step_type': step_type,
            'is_16bit': is_16bit,
            'sample_count': len(samples),
            'format': BlockFormat.F3
        }


class F3Decoder(BlockDecoder):
    """Format 3 decoder"""

    def __init__(self, max_step: int = 1024):
        self.max_step = max_step

    def decode(self, data: List[int], metadata: Dict[str, Any]) -> List[int]:
        """
        Decode F3 data to samples

        Args:
            data: Encoded bytes (without header)
            metadata: Must contain 'initial_value', 'step_type', and 'sample_count'
        """
        initial_value = metadata.get('initial_value', 0)
        step_type = metadata.get('step_type', StepType.LIN4)
        sample_count = metadata.get('sample_count', len(data) * 8)
        is_16bit = metadata.get('is_16bit', False)

        max_val = 65535 if is_16bit else 255
        current_value = initial_value
        samples = []
        step_num = 0
        is_negative = False

        for byte in data:
            for bit_pos in range(7, -1, -1):
                if len(samples) >= sample_count:
                    break

                bit = (byte >> bit_pos) & 1

                if bit == 0:
                    if not is_negative:
                        step_num = 0
                    is_negative = True
                    current_value -= StepCalculator.get_f3_step(step_type, step_num, self.max_step)
                else:
                    if is_negative:
                        step_num = 0
                    is_negative = False
                    current_value += StepCalculator.get_f3_step(step_type, step_num, self.max_step)

                current_value = max(0, min(current_value, max_val))
                samples.append(current_value)
                step_num += 1

        return samples[:sample_count]


# ============================================================================
# Main FurADPCM Class with File I/O
# ============================================================================

@dataclass
class AudioInfo:
    """Audio file information"""
    sample_rate: int
    channels: int
    bit_depth: int
    samples: List[int]


class FurADPCM:
    """Main codec class with file handling"""

    MAGIC = b"FurADPCM"
    EXTENSION = ".fa"

    def __init__(self):
        self.encoders = {
            BlockFormat.F1: lambda is_16bit: F1Encoder(is_16bit),
            BlockFormat.F2: lambda is_16bit: F2Encoder(is_16bit),
            BlockFormat.F3: lambda is_16bit: F3Encoder()
        }
        self.decoders = {
            BlockFormat.F1: lambda is_16bit: F1Decoder(is_16bit),
            BlockFormat.F2: lambda is_16bit: F2Decoder(is_16bit),
            BlockFormat.F3: lambda is_16bit: F3Decoder()
        }

    def encode(
            self, samples: List[int], sample_rate: int, channels: int = 1,
            block_format: BlockFormat = BlockFormat.F3,
            bit_depth: int = 8,
            **kwargs
            ) -> bytes:
        """
        Encode samples to FurADPCM format

        Args:
            samples: List of samples (interleaved for stereo)
            sample_rate: Sample rate in Hz
            channels: Number of channels (1 or 2)
            block_format: Which block format to use
            bit_depth: 8 or 16
            **kwargs: Format-specific options (step_type for F3, strategy for F2)

        Returns:
            Encoded bytes ready to save to file
        """
        is_16bit = (bit_depth == 16)
        max_val = 65535 if is_16bit else 255

        # Convert to unsigned if needed (assuming input is signed)
        if min(samples) < 0:
            offset = 128 if not is_16bit else 32768
            samples = [s + offset for s in samples]

        # Split channels if stereo
        if channels == 2:
            channel_samples = [samples[i::2] for i in range(2)]
        else:
            channel_samples = [samples]

        # Build header
        header = self._build_header(sample_rate, is_16bit, channels, block_format)

        # Encode each channel
        all_encoded = bytearray(header)

        for ch_samples in channel_samples:
            # Get appropriate encoder
            encoder_class = self.encoders[block_format]
            encoder = encoder_class(is_16bit) if block_format != BlockFormat.F3 else encoder_class(False)

            # Encode in blocks (max 4096 bytes per block for F3, adjust for others)
            max_samples_per_block = 4096 * 8 if block_format == BlockFormat.F3 else 8192

            for i in range(0, len(ch_samples), max_samples_per_block):
                print(f"encoding block {i//max_samples_per_block}")
                block_samples = ch_samples[i:i + max_samples_per_block]

                # Encode block
                if block_format == BlockFormat.F1:
                    encoded_data, metadata = encoder.encode(block_samples)
                elif block_format == BlockFormat.F2:
                    strategy = kwargs.get('strategy', StepSizeStrategy.ADAPTIVE)
                    encoded_data, metadata = encoder.encode(block_samples, strategy=strategy)
                else:  # F3
                    step_type = kwargs.get('step_type', StepType.LIN4)
                    encoded_data, metadata = encoder.encode(block_samples, step_type, is_16bit=is_16bit)

                # Build block header
                block_header = self._build_block_header(
                    block_format, len(encoded_data), metadata
                )

                all_encoded.extend(block_header)
                all_encoded.extend(encoded_data)

        return bytes(all_encoded)

    def decode(self, data: bytes) -> AudioInfo:
        """
        Decode FurADPCM data to samples

        Args:
            data: Raw FurADPCM file bytes

        Returns:
            AudioInfo with decoded samples and metadata
        """
        # Parse header
        if data[:8] != self.MAGIC:
            raise ValueError("Not a FurADPCM file")

        sample_rate = struct.unpack('>H', data[8:10])[0] * 2
        metadata_byte = data[10]

        is_16bit = bool((metadata_byte >> 7) & 1)
        channels = 2 if bool((metadata_byte >> 6) & 1) else 1
        block_format = BlockFormat(data[11])  # Fx block info start

        # Decode blocks
        decoded_channels = [[] for _ in range(channels)]
        pointer = 12  # Start after initial header
        current_channel = 0

        while pointer < len(data):
            # Parse block header
            if data[pointer] != block_format.value:
                raise ValueError(f"Unexpected block format: {hex(data[pointer])}")

            block_data, metadata, block_size = self._parse_block_header(data[pointer:], block_format)
            print(f"decoding at {pointer}, left: {len(data) - pointer};\n"
                  f"blocks left: {(len(data) - 12) // (block_size + 8)}")
            # Get decoder
            decoder_class = self.decoders[block_format]
            decoder = decoder_class(is_16bit) if block_format != BlockFormat.F3 else decoder_class(False)

            # Decode block
            decoded = decoder.decode(block_data, metadata)

            # Assign to appropriate channel
            decoded_channels[current_channel].extend(decoded)

            # Move to next channel or next block
            current_channel = (current_channel + 1) % channels
            pointer += block_size

        # Interleave stereo
        if channels == 2:
            min_len = min(len(decoded_channels[0]), len(decoded_channels[1]))
            interleaved = []
            for i in range(min_len):
                interleaved.append(decoded_channels[0][i])
                interleaved.append(decoded_channels[1][i])
            samples = interleaved
        else:
            samples = decoded_channels[0]

        # Convert back to signed
        if is_16bit:
            samples = [s - 32768 for s in samples]
        else:
            samples = [s - 128 for s in samples]

        return AudioInfo(
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=16 if is_16bit else 8,
            samples=samples
        )

    def _build_header(
            self, sample_rate: int, is_16bit: bool, channels: int,
            block_format: BlockFormat
            ) -> bytes:
        """Build file header"""
        header = bytearray(self.MAGIC)
        header.extend(struct.pack('>H', sample_rate // 2))

        metadata_byte = 0
        metadata_byte |= (1 << 7) if is_16bit else 0
        metadata_byte |= (1 << 6) if channels == 2 else 0
        header.append(metadata_byte)
        header.append(block_format.value)  # Fx Block Info Start

        return bytes(header)

    def _build_block_header(
            self, block_format: BlockFormat, data_size: int,
            metadata: Dict[str, Any]
            ) -> bytes:
        """Build block header based on format"""
        header = bytearray()
        header.append(block_format.value)

        if block_format == BlockFormat.F1:
            # F1: block_size (16-bit)
            block_size = data_size
            header.extend(struct.pack('>H', block_size))
            header.append(0xF0)  # Block end marker

        elif block_format == BlockFormat.F2:
            # F2: multiplier (3 bits) + block_size (13 bits)
            multiplier = metadata.get('multiplier', 1) - 1  # 0-7
            block_size = data_size
            header.append(((multiplier & 0x07) << 5) | ((block_size >> 8) & 0x1F))
            header.append(block_size & 0xFF)
            header.append(0xF0)

        else:  # F3
            # F3: step_type (2 bits) + block_size (14 bits)
            step_type = metadata.get('step_type', StepType.LIN4).value
            block_size = data_size
            header.append(((step_type & 0x03) << 6) | ((block_size >> 8) & 0x3F))
            header.append(block_size & 0xFF)

            # Flags + reserved
            is_16bit = 1 if metadata.get('is_16bit', False) else 0
            header.append(is_16bit << 7)
            header.append(0)  # Reserved

            # Initial value (16-bit)
            initial_value = metadata.get('initial_value', 0)
            header.extend(struct.pack('>H', initial_value))
            header.append(0xF0)  # Block end marker

        return bytes(header)

    def _parse_block_header(self, block_start: bytes, block_format: BlockFormat) -> Tuple[
        List[int], Dict[str, Any], int]:
        """Parse block header and return data, metadata, and total size"""

        if block_format == BlockFormat.F1:
            block_size = struct.unpack('>H', block_start[1:3])[0]
            metadata = {'sample_count': block_size * 2}
            data_start = 4  # After F1, size, and F0
            total_size = 4 + block_size

        elif block_format == BlockFormat.F2:
            multiplier = ((block_start[1] >> 5) & 0x07) + 1
            block_size = ((block_start[1] & 0x1F) << 8) | block_start[2]
            metadata = {'multiplier': multiplier, 'sample_count': block_size * 2 + 1}
            data_start = 4  # After F2, header, and F0
            total_size = 4 + block_size

        else:  # F3
            step_type = StepType((block_start[1] >> 6) & 0x03)
            block_size = ((block_start[1] & 0x3F) << 8) | block_start[2]
            is_16bit = bool((block_start[3] >> 7) & 1)
            initial_value = struct.unpack('>H', block_start[5:7])[0]

            metadata = {
                'step_type': step_type,
                'initial_value': initial_value,
                'is_16bit': is_16bit,
                'sample_count': block_size * 8
            }
            data_start = 8  # After F3, header, flags, reserved, correction, and F0
            total_size = 8 + block_size

        # Extract block data (excluding the trailing F0)
        block_data = list(block_start[data_start:data_start + block_size])

        return block_data, metadata, total_size


# ============================================================================
# WAV File Support
# ============================================================================

class WAVHandler:
    """Simple WAV file reader/writer"""

    @staticmethod
    def read(filepath: str) -> AudioInfo:
        """Read WAV file and return AudioInfo"""
        import wave

        with wave.open(filepath, 'rb') as wav:
            params = wav.getparams()
            frames = wav.readframes(params.nframes)

            if params.sampwidth == 1:
                # 8-bit unsigned
                samples = [b - 128 for b in frames]
            elif params.sampwidth == 2:
                # 16-bit signed little-endian
                samples = [struct.unpack_from('<h', frames, i)[0]
                           for i in range(0, len(frames), 2)]
            else:
                raise ValueError(f"Unsupported sample width: {params.sampwidth}")

            return AudioInfo(
                sample_rate=params.framerate,
                channels=params.nchannels,
                bit_depth=params.sampwidth * 8,
                samples=samples
            )

    @staticmethod
    def write(filepath: str, audio: AudioInfo):
        """Write AudioInfo to WAV file"""
        import wave

        with wave.open(filepath, 'wb') as wav:
            wav.setnchannels(audio.channels)
            wav.setsampwidth(audio.bit_depth // 8)
            wav.setframerate(audio.sample_rate)

            # Convert samples to bytes
            if audio.bit_depth == 8:
                # Unsigned 8-bit
                data = bytes([s + 128 for s in audio.samples])
            else:
                # Signed 16-bit little-endian
                data = b''
                for s in audio.samples:
                    data += struct.pack('<h', s)

            wav.writeframes(data)


# ============================================================================
# Example Usage and Testing
# ============================================================================

if __name__ == "__main__":
    # Generate test signal (sine wave)
    def generate_sine(freq: float, duration: float, sample_rate: int, amplitude: float = 0.5):
        num_samples = int(duration * sample_rate)
        samples = []
        for i in range(num_samples):
            t = i / sample_rate
            val = int(amplitude * 32767 * math.sin(2 * math.pi * freq * t))
            samples.append(val)
        return samples


    # Create test audio
    test_signal = generate_sine(440, 2.0, 44100, 0.5)

    codec = FurADPCM()

    print("=== Testing All Formats ===\n")

    for format_type in [BlockFormat.F1, BlockFormat.F2, BlockFormat.F3]:
        print(f"\n--- Testing {format_type.name} ---")

        # Encode
        if format_type == BlockFormat.F3:
            encoded = codec.encode(
                test_signal, 44100, 1, format_type, 16,
                step_type=StepType.LIN4
                )
        else:
            encoded = codec.encode(test_signal, 44100, 1, format_type, 16)

        print(f"Original size: {len(test_signal) * 2} bytes (16-bit)")
        print(f"Encoded size: {len(encoded)} bytes")
        print(f"Compression ratio: {len(test_signal) * 2 / len(encoded):.2f}:1")

        # Decode
        decoded_audio = codec.decode(encoded)

        # Calculate error
        mse = sum((a - b) ** 2 for a, b in zip(test_signal, decoded_audio.samples)) / len(test_signal)
        print(f"MSE: {mse:.2f}")
        print(f"SNR: {10 * math.log10(32767 ** 2 / mse):.2f} dB")

    print("\n=== Testing with WAV File ===")
    #print("To test with actual WAV files, uncomment the code below:")

    #Example: Encode a WAV file
    wav_handler = WAVHandler()
    audio = wav_handler.read("SOUNDTEST/FA_TEST.wav")

    # Encode with different formats
    for format_type in [BlockFormat.F2, BlockFormat.F3]:
        print(f"Now encoding and decoding with: {format_type}")
        encoded = codec.encode(audio.samples, audio.sample_rate, audio.channels,
                               format_type, audio.bit_depth,
                               step_type=StepType.LIN4,
                               strategy=StepSizeStrategy.ADAPTIVE
                               )

        with open(f"output{format_type.name}.fa", "wb") as f:
            f.write(encoded)

        # Decode back
        decoded_audio = codec.decode(encoded)
        wav_handler.write(f"decoded_{format_type.name}.wav", decoded_audio)