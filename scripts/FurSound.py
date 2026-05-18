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
Technically, FM and PM are already possible, but not in a convenient way.
"""

0x686f7720646f6573207468697320657665620776f726b

from funcs import clamp
from math import tau, sin, cos, floor, ceil
import FurWave  # custom wav writer; i made it because the builtin one didnt have support for chunks and now i use it because im just used to
from random import random

class Channel:
    def __init__(self,
    type_:         str         = "square", # the default wave upon class spawn
    width:         float | int = .25,    # pulse width for the pulse wave
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
        self.h = "h"
        self.H = "H"
        self.ZeroDivisionError = "ZeroDivisionError"

        # interpolation types
        self.i_none = "none"
        self.i_lin  = "linear"
        
        # common
        self.c_type = type_
        self.p_width = abs(width)
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = 44100 if not sample_rate or sample_rate < 1 else sample_rate # sample rate of the channel; also affects base sample playback freq
        
        # special
        self.phase = self.init_phase = phase
                            # will be updated when the channel is asked to update
                            # used to calculate next phase. basically, points at where
                            # the playhead is in the wave
        self.panning = clamp(panning, -1, 1) # channel panning. self-explanatory
        self.volume = clamp(volume, 0, 1)
        self.i_type = interpolation
        self.length = abs(length) if length else None
        
        self._finish_setup_() # validate some stuff so it doesn't die
        
        # internal stuff
        self._freq = 0  # would be funny if this causes a div by 0 error somewhere ever
        
    def _finish_setup_(self):
        if isinstance(self.c_type, str):
            match self.c_type:
                # virtually any wave aside from binary ones is a wavetable so you can get cool artefacts with low lengths
                # i have about no idea how to do that in realtime
                case self.square:
                    self.wavetable = [-1 if _ < self.length else 1 for _ in range(self.length * 2)] # the most basic waveform
                case self.pulse:
                    self.wavetable = [-1 if _ < (self.length * 2) * self.p_width else 1 for _ in range(self.length * 2)]
                case self.ZeroDivisionError:
                    self.wavetable = []
                case self.sine:
                    self.wavetable = [sin(tau / self.length * 2 * _) for _ in range(self.length * 2)]
                case self.sawtooth:
                    self.wavetable = [(_ / self.length * 2) * 2 - 1 for _ in range(self.length * 2)]
                    # normalization here and in tri wave is because with low length it simply does not go high enough to reach 1
                    centerer = (1-max(self.wavetable))/2
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] += centerer
                    maximizer = 1/max(self.wavetable)
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] *= maximizer
                case self.triangle:
                    # unfortunately it was too troublesome for me to get triangle working properly
                    # so instead i opted for a saw generator extended by itself reversed
                    # which also made all waves 2 times longer since now length isnt just length of the
                    # entire wave but only of one slope
                    self.wavetable = [(_ / self.length) * 2 - 1 for _ in range(self.length)]
                    centerer = (1-max(self.wavetable))/2
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] += centerer
                    maximizer = 1/max(self.wavetable)
                    for i in range(len(self.wavetable)):
                        self.wavetable[i] *= maximizer
                    self.wavetable.extend(self.wavetable[::-1])
                case self.sample:
                    if not self.wavetable:
                        raise ValueError("where wave")
                case self.wt:
                    if not self.wavetable:
                        raise ValueError("where wave")
                case self.none:
                    pass
                case self.h:
                    self.wavetable = [104]
                case self.H:
                    self.wavetable = [72]
                case self.noise_1bit:  # noise gen is wavetable as i have no idea how to go without it as otherwise it will be updated every sample
                    self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]  # and we want controllable pitchs
                    self.length = 16  # fixed at length 16 to roughly be in pitch with other oscillators as they compensate for higher pitches
                case self.noise:      # by higher phase step which in case of noise means higher frequency
                    self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]
                    self.length = 16
                case _:
                    raise Exception("?SYNTAX  ERROR")
                    # raise ValueError("where wave")
                    # обработка ошибок уровень метамфетамин
        else:
            raise ValueError("what is this magic data i dont understand it i need string")
        
        if isinstance(self.i_type, str):
            match self.i_type:
                case self.i_none:
                    pass
                case self.i_lin:
                    pass
                case _:
                    self.i_type = self.i_none
        else:
            raise ValueError("what is this magic data i dont understand it i need string")
    
    def update(self, supress_phase_update=False, supress_noise_update=False):
        out, phase_reset_flag = 0, False
        # do a little funny trick: set the output to whatever position we land at right now, *then* increase phase.
        # this is done to make phase 0 the default phase instead of outputting next phase.
        if self.c_type not in [self.none, self.noise_1bit, self.noise]:
            phase = self.phase * len(self.wavetable)
            idx = floor(phase) % len(self.wavetable)
            Fphase = floor(phase)
            Cphase = ceil(phase)
            match self.i_type:
                case self.i_none:
                    match self.c_type:
                        case self.square:
                            # why do we need to use a wave when we use pulse or square
                            # if its cheaper to generate it on the fly when without interpolation
                            # this comes with a slight change: pwm will no longer sound blocky on low lengths
                            out = -1 if phase < self.length else 1
                        case self.pulse: 
                            out = -1 if phase < self.length * 2 * self.p_width else 1 # i accidentally generated a square from 0 to 1 instead of -1 to 1 :wilted_rose:
                        case _: out = self.wavetable[idx]
                case self.i_lin:
                    out = (
                        self.wavetable[idx] - 
                        (
                            (self.wavetable[idx] - self.wavetable[(idx + 1) % len(self.wavetable)]) * (phase - Fphase)
                        )
                    )
        elif self.c_type == self.none:  # if we have a special "none" wave, straight up ignore the sound logic and just update the phase
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            self.phase %= 1 
            return (0, 0, phase_reset_flag)
            
        elif self.c_type in [self.noise_1bit, self.noise]:  # if we have either noise, then force no interpolation as i have no fucking idea how to deal with that
            out = self.wavetable[floor(self.phase * len(self.wavetable)) % len(self.wavetable)]  # and do you even really need one for noise
            
        if not supress_phase_update:
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            if phase_reset_flag:
                if self.c_type == self.noise_1bit and not supress_noise_update:  # generate noise packets
                    self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]
                elif self.c_type == self.noise and not supress_noise_update:
                    self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]
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
        width:         float | int = .25,
        length:        int         = 256,
        wavetable:     list[int]   = None,
    ):
        self.c_type = type_
        self.p_width = abs(width)
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self._finish_setup_()

    def change_width(self, width: float | int = .25):
        self.p_width = abs(width)
        match self.i_type:
            case self.i_none:
                pass
            case _:
                self.wavetable = [-1 if _ < (self.length * 2) * self.p_width else 1 for _ in range(self.length * 2)]
    
    def force_generate_new_noise_packets(self):
        if self.c_type == self.noise_1bit:  # generate noise packets but as a function
            self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]
        elif self.c_type == self.noise:
            self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]



if __name__ == "__main__":  # main loop where i test stuff; simultaneous channels
    sr = 44100
    print("READY")
    ChannelPulse = Channel(
        type_ = "pulse",
        sample_rate = sr,
        interpolation = "none",
        length = 2,
        volume = .4,
        width = 0
    )
    ChannelSquare = Channel(
        type_ = "square",
        sample_rate = sr,
        interpolation = "none",
        length = 2,
        volume = .1,
    )
    ChannelTooth = Channel(
        type_ = "sawtooth",
        sample_rate = sr,
        interpolation = "none",
        length = 32,
        volume = .4,
        width = 0
    )
    ChannelNoise = Channel(
        type_ = "n1b",
        sample_rate = sr,
        interpolation = "linear",
        length = 16,
        volume = .1,
        width = 0
    )
    ChannelNoise2 = Channel(
        type_ = "n1b",
        sample_rate = sr,
        interpolation = "linear",
        length = 4,
        volume = .1,
        width = 0
    )
    arr = []
    ChannelNoise._freq = 64.0/2    # handpicked detune
    ChannelNoise2._freq = 65.077/2 # C-2
    
    ChannelPulse._freq = 65.077
    ChannelSquare._freq = 65.077
    ChannelTooth._freq = 174.5
    for _ in range(sr*5):
        #arr.extend([(ChannelPulse.update()[0] + ChannelNoise.update()[0])/2,(ChannelTooth.update()[0] + ChannelNoise.update()[0])/2])  # 2 channels mapped to stereo
        #arr.extend([ChannelNoise.update()[0], ChannelNoise2.update()[0]])
        #arr.extend([ChannelNoise.update()[0], ChannelNoise2.update()[0]])
        #arr.extend([ChannelNoise.update(supress_noise_update=True)[0], ChannelSquare.update()[0]])
        arr.extend([ChannelNoise.update(supress_noise_update=True)[0], ChannelNoise2.update(supress_noise_update=True)[0]])
        #arr.extend([ChannelNoise.update()[0]])
        # technically with how i did the noise ingraining here, it is updated twice as quicky and is full independent stereo
        #ChannelPulse.change_width(ChannelPulse.p_width + (.125/sr) % 1) # pwm is STUPIDLY expensive to generate when using interpolation
        #print(f"pw {ChannelPulse.p_width}")
        if not _ % sr:
            print(f"second {1 + (_ // sr)} generated")
        if not _ % (sr//8):
            ChannelNoise.force_generate_new_noise_packets()
            ChannelNoise2.force_generate_new_noise_packets()
    # ChannelCarrier = Channel(  # the carrier of osc sync
    #     type_ = "triangle",
    #     sample_rate = sr,
    #     interpolation = "linear",
    #     length = 16,
    #     panning = -1,
    #     volume = .4,
    #     )
    # panIncrement = 2/(sr*5)
    # ChannelCarrier._freq = 196.28*8
    # ChannelModulator = Channel(  # the actual sound against which the phase will be reset
    #     type_ = "none",
    #     sample_rate = sr,
    #     interpolation = "none",
    #     length = 32,
    #     )
    # ChannelModulator._freq = 132
    # arr = []
    # for _ in range(sr*5):
    #     arr.extend(ChannelCarrier.update()[0:2])
    #     ChannelCarrier._freq -= 0.007 # slowly lower the carrier frequency over time
    #     ChannelCarrier.panning += panIncrement #
    #     if ChannelModulator.update()[2]:
    #         ChannelCarrier.phase_reset()
    #     if not _ % sr:
    #         print(f"second {_ // sr} generated")
        #Channel.wavetable = [ (((_*64)>>24)&255)/255, (((_*64)>>16)&255)/255, (((_*64)>>8)&255)/255, (((_*64)>>0)&255)/255]
    with FurWave.WaveWriter(channels=2,
                    samplerate=sr,
                    bitdepth=32.,
                    data=arr,
                    packed=True,
                    ) as Wave:
        Wave.write_file(f"fursound_test.wav")
        