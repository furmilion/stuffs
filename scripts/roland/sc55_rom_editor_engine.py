"""
A GUI editor tool for editing Roland SC-55 ROMs
This is the "engine"
"""
import typing

# BEHOLD! The SC-55 control ROM constants

LFO_WAVES: dict[int, str] = {
    0: "Sine",        1: "Square",       2: "Sawtooth",  3: "Triangle",
    4: "Unknown",     5: "Unknown",      6: "Unknown",   7: "Unknown",
    8: "Noise (S&H)", 9: "Noise (S&G)", 10: "Noise (S&G)",
    11: "Unknown",   12: "Unknown",     13: "Unknown",  14: "Unknown", 15: "Unknown"
}  # wave 10 (Sample & Glide) was supposed to have
   # steeper slope size compared to wave 9 (Sample & Glide),
   # judging by the code remnants in the CPU ROM of SC-55mk, firmware version 1.21
   # Instead it ended up being the same as wave 9
LFO_PHASE_SHIFT: dict[int, str] = {
    0:    "0°",  1:   "0°",  2:   "0°",  3:   "0°",
    4:   "90°",  5:  "90°",  6:  "90°",  7:  "90°",
    8:  "180°",  9: "180°", 10: "180°", 11: "180°",
    12: "270°", 13: "270°", 14: "270°", 15: "270°"
}  # Shift value added to phase accumulator.
   # I actually have no idea whether its 90° steps or finer.


class SC55_Instrument_Partial:
    """
    Represents a single partial of an SC-55 instrument.
    """
    def __init__(self, ):
        self.root_key_offset = 0x0040  # root key offset for this partial

        self.partial = 0               # actual partial ID

        self.lfo2_data = 0             # LFO shares the structure with instrument LFO 1
        self.lfo2_rate = 0
        self.lfo2_delay = 0
        self.lfo2_fade = 0

        self.panpot = 0x40  # partial panpot position. -63 (0x01) = left, 63 (0x7F) = right. -64 (0x00) = random

        self.coarse_tune  = 0x40  # coarse tune. from -64 (0x00) to 63 (0x7F)
        self.fine_tune    = 0x40  # fine tune in cents. from -64 (0x00) to 63 (0x7F)
        self.random_tune  = 0x00  # random pitch offset at note on event. from 0 to 100
        self.pitch_follow = 0x4a  # pitch follow. adjusts how note pitch sounds across the keys. ranges from -10 (0x40) to 0 (0x4a).
                                  # value of 0x4a gives natural pitch follow behavior (equal temperament)
                                  # value of 0x40 gives fixed pitch that will not change with key position

        self.lfo1_pitch_depth = 0x00  # LFO 1 pitch modulation depth. Ranges from 0 to 127, pitch depth calculated from a lookup table in the ROM
        self.lfo2_pitch_depth = 0x00  # LFO 2 pitch modulation depth. Ranges from 0 to 127, pitch depth calculated from a lookup table in the ROM

        self.pitch_env_depth = 0x00  # Pitch envelope depth. A coefficient that output from the pitch envelope gets multiplied by

        self.pitch_envelope_level_0 = 0  # value of pitch envelope at the start of attack 1
        self.pitch_envelope_level_1 = 0  # value of pitch envelope at the start of attack 2
        self.pitch_envelope_level_2 = 0  # value of pitch envelope at the start of decay 1
        self.pitch_envelope_level_3 = 0  # value of pitch envelope at the start of decay 2
        self.pitch_envelope_level_4 = 0  # value of pitch envelope at the end of release
        self.pitch_envelope_time_1  = 0  # duration of attack 1
        self.pitch_envelope_time_2  = 0  # duration of attack 2
        self.pitch_envelope_time_3  = 0  # duration of decay 1
        self.pitch_envelope_time_4  = 0  # duration of decay 2
        self.pitch_envelope_time_5  = 0  # duration of release

        self.pitch_env_time_key_scaling_1 = 0x40  # scales pitch envelope times 1..4
                                                  # positive values scale envelope times down for keys < 64 and up for keys >= 64
                                                  # negative values have the opposite effect
        self.pitch_env_time_key_scaling_2 = 0x40  # scales pitch envelope time 5
                                                  # positive values scale envelope times down for keys < 64 and up for keys >= 64
                                                  # negative values have the opposite effect
        self.pitch_env_velocity_scaling = 0x40    # range: -10 (0x36) .. 10 (0x4A).
                                                  # values from 0 (0x40) in either direction flatten the envelope, negative values also invert it
                                                  # calculated using the following formula: y = abs(pitch) * 2.4 * (127 - velocity)

        self.tvf_cutoff_velocity_curve = 0  # selects the TVF cutoff velocity curve, from 0 to 9.
                                            # the curves are defined in the ROM, and curve 0 is linear.
                                            # key velocity is the index for the curve, and the output is the frequency value
        self.tvf_cutoff_base_frequency = 0  # base frequency for the TVF cutoff, from 0 to 127.
                                            # the frequency is calculated via a lookup table

class SC55_Instrument:
    """
    Represents an SC-55 instrument.
    """
    def __init__(self, ):
        self.attenuaton = 1   # instrument attenuation; range: 1..127
        # LFO 1. Global for the entire instrument.
        self.lfo1_data  = 0   # LFO 1 data: low nibble is wave, high nibble is phase shift
        self.lfo1_rate  = 0   # LFO 1 rate. Ranges from 0 to 127, actual rate calculated from lookup table in the ROM
        self.lfo1_delay = 0   # LFO 1 delay. Range: 0..127, non-linear delay until lfo fades in. Also calculated from a lookup table in the ROM
        self.lfo1_fade  = 0   # LFO 1 fade rate. Range: 0..127, non-linear fade rate. Shares lookup table with LFO 1 delay.

        self.partials_used = 0   # Bitfield indicating which partials are used by the instrument. Bit 0 = partial 1, bit 1 = partial 2. Unfortunately, thats all, the instrument only supports 2 partials.

        self.pitch_correction_curve = 0 # Pitch correction curve to use, if any. 0 - do not use, 1 or 2: use curve 1 or 2 from the ROM

    def decode(self, data: bytes | bytearray | list[int] | None = None):
        if not data:
            return
