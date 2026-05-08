"""
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

class Channel:
    def __init__(self,
    type:        str         = "square",
    width:       float | int = 0,
    wavetable:   list[int]   = None,
    sample_rate: int         = 44100,
    phase:       float | int = 0,
    panning:     float | int = 0,
    volume:      float | int = 1,
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


        # common
        self.c_type = type
        self.p_width = round(width, 5) # round to 5 decimal digits
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = sample_rate # sample rate of the channel; also affects base sample playback freq
        
        # special
        self.phase = phase  # will be updated when the channel is asked to update
                            # used to calculate next phase. basically, points at where
                            # the playhead is in the wave
        self.panning = panning # channel panning. self-explanatory; not used right now, might implement later
        self.volume = volume
        self.finish_setup() # validate some stuff so it doesn't die
    def finish_setup(self):
        if isinstance(self.c_type, str):
            match self.c_type:
                case self.square:
                    self.wavetable = [0 if _ < 64 else 255 for _ in range(256)] # the most basic waveform
                case self.pulse:
                    self.wavetable = []
                case self.sine:
                    self.wavetable = []
                case self.sawtooth:
                    self.wavetable = [_ for _ in range(256)]
                case self.sample:
                    pass  # assume already valid wavetable.

        else:
            raise ValueError("'type' must be a string!")
                



if __name__ == "__main__":
    ...