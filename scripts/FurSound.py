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
import FurWave

class Channel:
    def __init__(self,
    type_:         str         = "square",
    width:         float | int = 0,    # pulse width for the pulse wave
    length:        int         = 256,  # the length of the preset waves
    wavetable:     list[int]   = None,
    sample_rate:   int         = 44100,
    phase:         float | int = 0,
    panning:       float | int = 0,
    volume:        float | int = 1,
    interpolation: str         = "none"
    ):
        # constants

        # wave types
        self.square     = "square";    self.pulse    = "pulse"
        self.sine       = "sine";      self.sawtooth = "sawtooth"
        self.sample     = "pcm";       self.pcm      = self.sample
        self.noise_1bit = "n1b";       self.noise    = "n"
        self.wt         = "wavetable"; self.triangle = "triangle"

        # coming: more types; replaced with the closest ones by sound
        self.fm = self.sine
        self.xor_triangle = self.pulse
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
        self.length = abs(length)
        
        self.finish_setup() # validate some stuff so it doesn't die
        
        # internal stuff
        self._freq = 0  # would be funny if this causes a div by 0 error somewhere
        
    def finish_setup(self):
        if isinstance(self.c_type, str):
            match self.c_type:
                case self.square:
                    self.wavetable = [-1 if _ < self.length // 2 else 1 for _ in range(self.length)] # the most basic waveform
                case self.pulse:
                    self.wavetable = []
                case self.sine:
                    self.wavetable = [sin(tau / self.length * _) for _ in range(self.length)]
                case self.sawtooth:
                    self.wavetable = [(_ / self.length) * 2 - 1 for _ in range(self.length)]
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] += (1-max(self.wavetable))/2
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] *= 1/max(self.wavetable)
                case self.triangle:  # unfortunately it was too troublesome for me to get triangle working properly so instead i opted for a saw generator extended by itself reversed
                    self.wavetable = [(_ / self.length) * 2 - 1 for _ in range(self.length)]
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] += (1-max(self.wavetable))/2
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] *= 1/max(self.wavetable)
                    self.wavetable.extend(self.wavetable[::-1])
                case self.sample:
                    pass  # assume already valid wavetable
                case self.wt:
                    if self.wavetable:
                        pass
                    else:
                        self.c_type = self.square
                        self.finish_setup()
                case _:
                    self.c_type = self.square
                    self.finish_setup()
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
        phase = self.phase * len(self.wavetable)
        match self.i_type:
            case self.i_none:
                out = self.wavetable[floor(phase)]
            case self.i_lin:
                out = (
                    self.wavetable[floor(phase) % len(self.wavetable)] - 
                    (
                        (self.wavetable[floor(phase) % len(self.wavetable)] - self.wavetable[ceil(phase) % len(self.wavetable)]) * (phase - floor(phase))
                    )
                )
        self.phase = (self.phase + (self._freq / self.sample_rate)) % 1  # modulo so that it automatically wraps around at 1
        
        # debug output
        #print(f"output:  {out}\n"
        #      f"wt:      {self.wavetable[floor(self.phase) % len(self.wavetable)]}\n"
        #      f"wt+1:    {self.wavetable[ceil(self.phase) % len(self.wavetable)]}\n"
        #      f"phase:   {self.phase}\n"
        #      f"phase*l: {self.phase * len(self.wavetable)}\n"
        #)
        return out
                



if __name__ == "__main__":  # test
    sr = 44100
    Channel = Channel(
        type_ = "wavetable",
        sample_rate = sr,
        interpolation = "linear",
        wavetable = [0, .75, 1, .75],
        length=1024,
        )
    # print(pulseChannel.wavetable)
    Channel._freq = 65.256
    arr = []
    for _ in range(sr*20):
        arr.append(Channel.update())
        Channel.wavetable = [ (((_*64)>>24)&255)/255, (((_*64)>>16)&255)/255, (((_*64)>>8)&255)/255, (((_*64)>>0)&255)/255]
    with FurWave.WaveWriter(channels=1,
                    samplerate=88200,
                    bitdepth=32.,
                    data=arr,
                    packed=True,
                    ) as Wave:
        Wave.write_file(f"fursound_test.wav")
        