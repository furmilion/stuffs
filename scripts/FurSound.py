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
Technically, FM and PM are already possible, but not in a convenient way.
"""

import funcs  # some useful funcations from generic ass library; only uses clamp as of now
from math import tau, sin, cos, floor, ceil
import FurWave  # custom wav writer; i made it because the builtin one didnt have support for chunks and now i use it because im just used to

class Channel:
    def __init__(self,
    type_:         str         = "square", # the default wave upon class spawn
    width:         float | int = 0,    # pulse width for the pulse wave
    length:        int         = 256,  # the length of the preset waves
    wavetable:     list[int]   = None, # wavetable
    sample_rate:   int         = 44100, # default sample rate...
    phase:         float | int = 0, # ...phase...
    panning:       float | int = 0, #...pan...
    volume:        float | int = 1, #...and volume.
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
        self.none = "none"

        # interpolation types
        self.i_none = "none"
        self.i_lin  = "linear"
        
        # common
        self.c_type = type_
        self.p_width = round(abs(width), 5) # round to 5 decimal digits
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = 44100 if not sample_rate or sample_rate < 1 else sample_rate # sample rate of the channel; also affects base sample playback freq
        
        # special
        self.phase = self.init_phase = phase
                            # will be updated when the channel is asked to update
                            # used to calculate next phase. basically, points at where
                            # the playhead is in the wave
        self.panning = funcs.clamp(panning, -1, 1) # channel panning. self-explanatory; not used right now, might implement later
        self.volume = funcs.clamp(volume, 0, 1)
        self.i_type = interpolation
        self.length = abs(length) if length else None
        
        self._finish_setup_() # validate some stuff so it doesn't die
        
        # internal stuff
        self._freq = 0  # would be funny if this causes a div by 0 error somewhere
        
    def _finish_setup_(self):
        if isinstance(self.c_type, str):
            match self.c_type:
                case self.square:
                    self.wavetable = [-1 if _ < self.length else 1 for _ in range(self.length * 2)] # the most basic waveform
                case self.pulse:
                    self.wavetable = []
                case self.sine:
                    self.wavetable = [sin(tau / self.length * 2 * _) for _ in range(self.length * 2)]
                case self.sawtooth:
                    self.wavetable = [(_ / self.length * 2) * 2 - 1 for _ in range(self.length * 2)]
                    centerer = (1-max(self.wavetable))/2
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] += centerer
                    maximizer = 1/max(self.wavetable)
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] *= maximizer
                case self.triangle:  # unfortunately it was too troublesome for me to get triangle working properly so instead i opted for a saw generator extended by itself reversed
                    self.wavetable = [(_ / self.length) * 2 - 1 for _ in range(self.length)]
                    centerer = (1-max(self.wavetable))/2
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] += centerer
                    maximizer = 1/max(self.wavetable)
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] *= maximizer
                    self.wavetable.extend(self.wavetable[::-1])
                case self.sample:
                    pass  # assume already valid wavetable
                case self.wt:
                    if self.wavetable:
                        pass
                    else:
                        self.c_type = self.square
                        self.finish_setup()
                case self.none:
                    pass
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
    
    def update(self, supress_phase_update=False):
        # do a little funny trick: set the output to whatever position we land at right now, *then* increase phase.
        # this is done to make phase 0 the default phase instead of outputting next phase.
        if self.c_type != self.none:
            phase = self.phase * len(self.wavetable)
            match self.i_type:
                case self.i_none:
                    out = self.wavetable[floor(phase) % len(wavetable)]
                case self.i_lin:
                    out = (
                        self.wavetable[floor(phase) % len(self.wavetable)] - 
                        (
                            (self.wavetable[floor(phase) % len(self.wavetable)] - self.wavetable[ceil(phase) % len(self.wavetable)]) * (phase - floor(phase))
                        )
                    )
        else:  # if we have a special "none" wave, straight up ignore the sound logic and just update the phase
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            self.phase %= 1 
            return (0, 0, phase_reset_flag)
        if not supress_phase_update:
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            self.phase %= 1  # modulo so that it automatically wraps around at 1
        
        # debug output
        #print(f"output:  {out}\n"
        #      f"wt:      {self.wavetable[floor(self.phase) % len(self.wavetable)]}\n"
        #      f"wt+1:    {self.wavetable[ceil(self.phase) % len(self.wavetable)]}\n"
        #      f"phase:   {self.phase}\n"
        #      f"phase*l: {self.phase * len(self.wavetable)}\n"
        #)
        lMult = 1 - abs(self.panning) if self.panning > 0 else 1
        rMult = 1 - abs(self.panning) if self.panning < 0 else 1
        return (out * lMult * self.volume, out * rMult * self.volume, phase_reset_flag)
    
    def phase_reset(self):
        self.phase = self.init_phase
    
    def change_wave(self,  # this is basically a copy of some init stuff, except as a separate function.
        type_:         str         = "square",
        width:         float | int = 0,
        length:        int         = 256,
        wavetable:     list[int]   = None,
    ):
        self.c_type = type_
        self.p_width = round(abs(width), 5) # round to 5 decimal digits
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self._finish_setup_()
        



if __name__ == "__main__":  # main loop where i test stuff; currently its osc sync
    sr = 44100
    ChannelCarrier = Channel(
        type_ = "triangle",
        sample_rate = sr,
        interpolation = "linear",
        length = 16,
        panning = -1,
        volume = .4,
        )
    panIncrement = 2/(sr*5)
    ChannelCarrier._freq = 196.28*8
    ChannelModulator = Channel(
        type_ = "none",
        sample_rate = sr,
        interpolation = "none",
        length = 32,
        )
    ChannelModulator._freq = 132
    arr = []
    for _ in range(sr*5):
        arr.extend(ChannelCarrier.update()[0:2])
        ChannelCarrier._freq -= 0.007
        ChannelCarrier.panning += panIncrement
        if ChannelModulator.update()[2]:
            ChannelCarrier.phase_reset()
        if not _ % sr:
            print(f"second {_ // sr} generated")
        #Channel.wavetable = [ (((_*64)>>24)&255)/255, (((_*64)>>16)&255)/255, (((_*64)>>8)&255)/255, (((_*64)>>0)&255)/255]
    with FurWave.WaveWriter(channels=2,
                    samplerate=sr,
                    bitdepth=32.,
                    data=arr,
                    packed=True,
                    ) as Wave:
        Wave.write_file(f"fursound_test.wav")
        