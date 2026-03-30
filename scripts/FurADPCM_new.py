import math
import struct
from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

class StepSizeStrategy(Enum):
    """Strategy for choosing step size multiplier in F2"""
    PEAK = "peak"           # Based on maximum absolute value
    RMS = "rms"             # Based on root mean square
    ADAPTIVE = "adaptive"   # Analyzes signal characteristics

@dataclass
class F2BlockConfig:
    """Configuration for F2 block encoding"""
    multiplier: int          # 3-bit value (1-8, stored as 0-7)
    block_size: int         # Number of samples (max 8192)
    step_table: List[int]   # Will be scaled step table

class StepCalculator:
    """Calculate appropriate step sizes for F2 blocks"""
    
    F2_BASE_STEPS = [0x0F, 0x07, 0x03, 0x01]  # Base step values
    
    @staticmethod
    def get_scaled_step_table(multiplier: int) -> List[int]:
        """
        Scale the base step table by multiplier.
        Multiplier range: 1-8 (stored as 0-7 in header)
        """
        return [step * multiplier for step in StepCalculator.F2_BASE_STEPS]
    
    @classmethod
    def find_optimal_multiplier_peak(cls, samples: List[int], max_allowed: int = 255) -> int:
        """
        Find multiplier that ensures no clipping based on peak value.
        """
        if not samples:
            return 1
        
        max_abs = max(abs(s) for s in samples)
        
        # Need the largest step to be >= max_abs
        # Largest step = max(step_table) * multiplier
        max_step_base = max(cls.F2_BASE_STEPS)  # 0x0F = 15
        
        multiplier = max(1, (max_abs + max_step_base - 1) // max_step_base)
        return min(multiplier, 8)  # Cap at 8 (3 bits)
    
    @classmethod
    def find_optimal_multiplier_rms(cls, samples: List[int], max_allowed: int = 255) -> int:
        """
        Find multiplier based on RMS (root mean square) value.
        """
        if not samples:
            return 1
        
        # Calculate RMS
        rms = math.sqrt(sum(s*s for s in samples) / len(samples))
        
        # Target: largest step should be about 2-3x RMS
        # This gives good quantization while allowing peaks
        max_step_base = max(cls.F2_BASE_STEPS)
        
        multiplier = max(1, int((rms * 2.5 + max_step_base - 1) // max_step_base))
        return min(multiplier, 8)
    
    @classmethod
    def find_optimal_multiplier_adaptive(cls, samples: List[int], max_allowed: int = 255) -> int:
        """
        Advanced: Analyze signal characteristics to find optimal multiplier.
        Considers:
        - Peak values
        - Signal dynamics (variance)
        - Zero-crossing rate (frequency content)
        """
        if not samples:
            return 1
        
        # 1. Peak-based lower bound
        max_abs = max(abs(s) for s in samples)
        max_step_base = max(cls.F2_BASE_STEPS)
        peak_mult = max(1, (max_abs + max_step_base - 1) // max_step_base)
        
        # 2. RMS-based suggestion
        rms = math.sqrt(sum(s*s for s in samples) / len(samples))
        rms_mult = max(1, int((rms * 2 + max_step_base - 1) // max_step_base))
        
        # 3. Analyze dynamics (variance)
        mean = sum(samples) / len(samples)
        variance = sum((s - mean) ** 2 for s in samples) / len(samples)
        std_dev = math.sqrt(variance)
        dynamic_mult = max(1, int((std_dev * 3 + max_step_base - 1) // max_step_base))
        
        # 4. Zero-crossing rate (indicates frequency)
        zero_crossings = 0
        for i in range(1, len(samples)):
            if samples[i] * samples[i-1] < 0:
                zero_crossings += 1
        zcr = zero_crossings / len(samples)
        
        # High frequency content needs smaller steps for detail
        freq_factor = max(0.5, 1.0 - zcr)
        
        # Combine factors
        # Peak is absolute upper bound, RMS and dynamics guide optimal value
        candidate = int((rms_mult * 0.4 + dynamic_mult * 0.4 + peak_mult * 0.2) * freq_factor)
        candidate = max(peak_mult, min(candidate, 8))  # Between peak and 8
        
        return min(candidate, 8)
    
    @classmethod
    def find_optimal_multiplier(cls, samples: List[int], 
                               strategy: StepSizeStrategy = StepSizeStrategy.ADAPTIVE) -> int:
        """Main entry point for multiplier selection"""
        if strategy == StepSizeStrategy.PEAK:
            return cls.find_optimal_multiplier_peak(samples)
        elif strategy == StepSizeStrategy.RMS:
            return cls.find_optimal_multiplier_rms(samples)
        else:
            return cls.find_optimal_multiplier_adaptive(samples)

class BlockF1Encoder:
    """
    Format 1: 8-step table, 2 samples per byte
    Structure: Each byte contains 2 samples
    - Upper nibble: sample 1 (4 bits: sign + 3-bit step index)
    - Lower nibble: sample 2 (4 bits: sign + 3-bit step index)
    """
    
    STEP_TABLE_8BIT = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
    STEP_TABLE_16BIT = [0x4000, 0x2000, 0x1000, 0x800, 0x400, 0x200, 0x100, 0x80]
    
    def __init__(self, is_16bit: bool = False):
        self.step_table = self.STEP_TABLE_16BIT if is_16bit else self.STEP_TABLE_8BIT
        self.max_val = 65535 if is_16bit else 255
        self.is_16bit = is_16bit
    
    def encode_block(self, samples: List[int], initial_value: Optional[int] = None) -> Tuple[List[int], int]:
        """
        Encode a block of samples using F1 format.
        Returns: (encoded_bytes, initial_value_used)
        """
        if not samples:
            return [], 0
        
        initial_value = initial_value if initial_value is not None else samples[0]
        current_value = initial_value
        encoded = []
        
        # Process samples in pairs
        for i in range(0, len(samples), 2):
            byte = 0
            
            # First sample (upper nibble)
            if i < len(samples):
                diff = samples[i] - current_value
                step_idx, sign = self._quantize_step(diff, current_value)
                byte |= (sign << 3) | (step_idx & 0x07)
                
                # Update current value based on encoded step
                step = self.step_table[step_idx]
                if sign:
                    current_value -= step
                else:
                    current_value += step
                current_value = max(0, min(current_value, self.max_val))
            
            # Second sample (lower nibble)
            if i + 1 < len(samples):
                diff = samples[i + 1] - current_value
                step_idx, sign = self._quantize_step(diff, current_value)
                byte |= ((sign << 3) | (step_idx & 0x07)) << 4
                
                # Update current value
                step = self.step_table[step_idx]
                if sign:
                    current_value -= step
                else:
                    current_value += step
                current_value = max(0, min(current_value, self.max_val))
            
            encoded.append(byte)
        
        return encoded, initial_value
    
    def _quantize_step(self, diff: int, current_value: int) -> Tuple[int, int]:
        """
        Quantize the difference to a step index and sign.
        Returns: (step_index, sign) where sign=1 for negative, 0 for positive
        """
        if diff < 0:
            sign = 1
            abs_diff = -diff
        else:
            sign = 0
            abs_diff = diff
        
        # Find the smallest step that's >= abs_diff
        for idx, step in enumerate(self.step_table):
            if step >= abs_diff:
                return idx, sign
        
        # If diff is larger than all steps, use largest step
        return len(self.step_table) - 1, sign
    
    def decode_block(self, encoded: List[int], block_size: int, 
                     initial_value: int) -> List[int]:
        """Decode an F1 block"""
        current_value = initial_value
        samples = []
        
        for byte in encoded:
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
        
        # Trim to expected block size
        return samples[:block_size * 2]

class BlockF2Encoder:
    """
    Format 2: 4-step table with multiplier, 1 sample per nibble
    Structure: 
    - Header: 2 bytes (format + multiplier + block size)
    - Data: 1 nibble per sample (4 bits: sign + 2-bit step index)
    """
    
    BASE_STEPS = [0x0F, 0x07, 0x03, 0x01]
    
    def __init__(self, is_16bit: bool = False):
        self.max_val = 65535 if is_16bit else 255
        self.is_16bit = is_16bit
    
    def encode_block(self, samples: List[int], 
                    multiplier: Optional[int] = None,
                    strategy: StepSizeStrategy = StepSizeStrategy.ADAPTIVE) -> Tuple[List[int], int, int]:
        """
        Encode a block using F2 format.
        
        Args:
            samples: List of samples to encode
            multiplier: Optional multiplier (auto-calculated if None)
            strategy: Strategy for auto-multiplier selection
        
        Returns:
            (encoded_bytes, multiplier_used, initial_value)
        """
        if not samples:
            return [], 1, 0
        
        # Auto-select multiplier if not provided
        if multiplier is None:
            multiplier = StepCalculator.find_optimal_multiplier(samples, strategy)
        
        # Scale step table
        scaled_steps = [step * multiplier for step in self.BASE_STEPS]
        
        initial_value = samples[0]
        current_value = initial_value
        encoded_nibbles = []
        
        for sample in samples[1:]:  # First sample is reference
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
        
        return encoded_bytes, multiplier, initial_value
    
    def _quantize_step(self, diff: int, steps: List[int]) -> Tuple[int, int]:
        """Quantize difference to step index and sign"""
        if diff < 0:
            sign = 1
            abs_diff = -diff
        else:
            sign = 0
            abs_diff = diff
        
        # Find best matching step
        for idx, step in enumerate(steps):
            if step >= abs_diff:
                return idx, sign
        
        return len(steps) - 1, sign
    
    def decode_block(self, encoded: List[int], multiplier: int, 
                    block_size: int, initial_value: int) -> List[int]:
        """Decode an F2 block"""
        scaled_steps = [step * multiplier for step in self.BASE_STEPS]
        current_value = initial_value
        samples = [initial_value]
        
        # Extract nibbles
        nibbles = []
        for byte in encoded:
            nibbles.append((byte >> 4) & 0x0F)
            nibbles.append(byte & 0x0F)
        
        # Decode each nibble
        for nibble in nibbles[:block_size]:  # block_size is number of samples minus initial
            step_idx = nibble & 0x03
            sign = (nibble >> 2) & 1
            
            step = scaled_steps[step_idx]
            if sign:
                current_value -= step
            else:
                current_value += step
            current_value = max(0, min(current_value, self.max_val))
            samples.append(current_value)
        
        return samples[:block_size + 1]  # +1 for initial value

class CompleteFurADPCM:
    """Complete implementation with all block formats"""
    
    def __init__(self):
        self.f1_encoders = {}
        self.f2_encoders = {}
    
    def encode_block_f1(self, samples: List[int], is_16bit: bool = False) -> Tuple[List[int], int]:
        """Encode with F1 format"""
        encoder = BlockF1Encoder(is_16bit)
        return encoder.encode_block(samples)
    
    def encode_block_f2(self, samples: List[int], is_16bit: bool = False,
                       multiplier: Optional[int] = None,
                       strategy: StepSizeStrategy = StepSizeStrategy.ADAPTIVE) -> Tuple[List[int], int, int]:
        """Encode with F2 format"""
        encoder = BlockF2Encoder(is_16bit)
        return encoder.encode_block(samples, multiplier, strategy)
    
    def encode_block_f3(self, samples: List[int], step_type: StepType,
                       is_16bit: bool = False) -> Tuple[List[int], int]:
        """Encode with F3 format (from previous implementation)"""
        # ... (use your existing F3 encoder)
        pass
    
    def analyze_multiplier_effectiveness(self, samples: List[int]) -> dict:
        """
        Analyze which multiplier would work best for given samples.
        Useful for debugging and optimization.
        """
        results = {}
        
        for multiplier in range(1, 9):
            encoder = BlockF2Encoder()
            steps = [step * multiplier for step in encoder.BASE_STEPS]
            
            # Simulate encoding to calculate error
            current = samples[0]
            total_error = 0
            max_error = 0
            
            for sample in samples[1:]:
                diff = sample - current
                abs_diff = abs(diff)
                
                # Find step used
                step_used = min(steps, key=lambda s: abs(s - abs_diff))
                error = abs(abs_diff - step_used)
                total_error += error
                max_error = max(max_error, error)
                
                # Update current (simulate)
                if diff < 0:
                    current -= step_used
                else:
                    current += step_used
                current = max(0, min(current, 255))
            
            results[multiplier] = {
                'mean_error': total_error / len(samples),
                'max_error': max_error,
                'steps': steps
            }
        
        return results

# Example usage with comparison
if __name__ == "__main__":
    # Test samples (sine wave)
    test_samples = []
    for i in range(256):
        val = int(128 + 100 * math.sin(i * 2 * math.pi / 32))
        test_samples.append(val)
    
    codec = CompleteFurADPCM()
    
    print("=== F2 Multiplier Analysis ===")
    analysis = codec.analyze_multiplier_effectiveness(test_samples)
    
    for mult, stats in analysis.items():
        print(f"Multiplier {mult}: Mean Error = {stats['mean_error']:.2f}, "
              f"Max Error = {stats['max_error']}")
    
    print("\n=== Encoding Comparison ===")
    
    # Test different strategies
    for strategy in StepSizeStrategy:
        encoded, multiplier, init = codec.encode_block_f2(
            test_samples, 
            is_16bit=False,
            strategy=strategy
        )
        print(f"{strategy.value:10} -> multiplier = {multiplier}, "
              f"compressed to {len(encoded)} bytes (ratio: {len(test_samples)/len(encoded):.1f}:1)")
    
    # Test F1
    encoded_f1, init_f1 = codec.encode_block_f1(test_samples, is_16bit=False)
    print(f"F1{' ' * 10} -> compressed to {len(encoded_f1)} bytes "
          f"(ratio: {len(test_samples)/len(encoded_f1):.1f}:1)")