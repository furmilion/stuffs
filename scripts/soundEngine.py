"""
FurSound
This is my custom sound engine.
The concept is as simple as it gets: iterate over a wave form at sample rate.

Currently, only a single core thing has been partially implemented: a Channel.

A channel is the sound producing unit of the engine.
It has the following properties:
    - Waveform (i.e. square, wavetable etc.)
    - Pulse width for pulse wave
    - Wavetable for wavetable and sample waves
    - Sample rate, which also controls root frequency of a sample
    - Panpot
    - Volume
    - FM: (completely unimplemented right now)
        Per-operator ADSR
        Per-operator frequency control
        Operator matrix
        Operator ADSR
"""

import funcs  # later use
from math import tau, pi, sin, cos, sinh, cosh, tan, tanh, asin, asinh, acos, acosh, atan, atan2, atanh, floor, ceil

class Channel:
    def __init__(self,
    type_:         str         = "square",
    width:         float | int = 0,
    wavetable:     list[int]   = None,
    sample_rate:   int         = 44100,
    phase:         float | int = 0,
    panning:       float | int = 0,
    volume:        float | int = 1,
    interpolation: str         = "none"
    ):
        # constants

        # wave types
        self.square     = "square";  self.pulse    = "pulse"
        self.sine       = "sine";    self.sawtooth = "sawtooth"
        self.sample     = "pcm";     self.pcm      = self.sample
        self.noise_1bit = "n1b";     self.noise    = "n"

        # coming: more types; replaced with the closest ones by sound
        self.fm = self.sine
        self.triangle = self.square; self.xor_triangle = self.pulse
        self.xor_sine = self.sine;   self.xor_sawtooth = self.sawtooth

        # special
        self.test = self.square
        self.unimplemented = self.sine

        # interpolation types
        self.i_none = "none"
        self.i_lin  = "linear"
        
        # common
        self.c_type = type_
        self.p_width = round(width, 5) # round to 5 decimal digits
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = sample_rate # sample rate of the channel; also affects base sample playback freq
        
        # special
        self.phase = phase  # will be updated when the channel is asked to update
                            # used to calculate next phase. basically, points at where
                            # the playhead is in the wave
        self.panning = panning # channel panning. self-explanatory; not used right now, might implement later
        self.volume = volume
        self.i_type = interpolation
        
        self.finish_setup() # validate some stuff so it doesn't die
        
        # internal stuff
        self._freq = 0  # would be funny if this causes a div by 0 error somewhere
        
    def finish_setup(self):
        if isinstance(self.c_type, str):
            match self.c_type:
                case self.square:
                    self.wavetable = [0 if _ < 128 else 255 for _ in range(256)] # the most basic waveform
                case self.pulse:
                    self.wavetable = []
                case self.sine:
                    self.wavetable = []
                case self.sawtooth:
                    self.wavetable = [_ for _ in range(256)]
                case self.sample:
                    pass  # assume already valid wavetable
                case _:
                    self.wavetable = [0 if _ < 128 else 255 for _ in range(256)] # square fallback
        else:
            raise ValueError("'type' must be a string!")
        
        if isinstance(self.i_type, str):
            match self.i_type:
                case self.i_none:
                    pass
                case self.i_lin:
                    pass
                case _:
                    self.i_type = self.i_none
        else:
            raise ValueError("'type' must be a string!")
    
    def update(self):
        # do a little funny trick: set the output to whatever position we land at right now, *then* increase phase.
        # this is done to make phase 0 the default phase instead of outputting next phase.
        # print(f"phase {self.phase}\n"
        #       f"wave access at: {floor(self.phase * len(self.wavetable))}, value: {self.wavetable[floor(self.phase * len(self.wavetable))]}\n"
        #       f"phase % 1: {self.phase % 1}\n")
        match self.i_type:
            case self.i_none:
                out = self.wavetable[floor(self.phase * len(self.wavetable))]
            case self.i_lin:
                out = floor(
                               (
                                   self.wavetable[floor(self.phase * len(self.wavetable))] +
                                   self.wavetable[(floor(self.phase * len(self.wavetable)) + 1) % len(self.wavetable)] # modulo to avoid OOB access exception
                               ) / 2
                           ) # doesnt work as intended rn but ill fix it later
        self.phase = (self.phase + (self._freq / self.sample_rate)) % 1  # modulo so that it automatically wraps around at 1
        return out
                



if __name__ == "__main__":  # test
    sr = 44100
    pulseChannel = Channel(
        type_ = "sawtooth",
        sample_rate = sr,
        interpolation = "linear"
        )
    # print(pulseChannel.wavetable)
    pulseChannel._freq = 22.5
    fs_test = open("fursound_test.raw", "wb")
    fs_test.write(bytes([pulseChannel.update() for _ in range(sr*5)]))
        