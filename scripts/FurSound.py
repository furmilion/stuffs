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
    - ADSD2R
    - FM: (completely unimplemented right now)
        Per-operator ADSR
        Per-operator frequency control
        Operator matrix
Technically, FM and PM are already possible, but not in a convenient way.

I might implement a toggle that disables higher playback
rate for longer wavetables
"""

# FURSOUND -- started on 05/09/26
# crazy how in about a week i went from a blank
# file to some fancy math that generates sounds
#                                       - Furmilion
# огибающая писалась за две минуты хуем на коленке и
# поэтому из всего говнокода она наиговнокоднейшая 

0x686f7720646f6573207468697320657665620776f726b


WAVE_SQUARE   = 0
WAVE_PULSE    = 1
WAVE_SINE     = 2
WAVE_SAWTOOTH = 3
WAVE_SAMPLE   = 4
WAVE_NOISE1B  = 5
WAVE_NOISE    = 6
WAVE_TABLE    = 7
WAVE_TRIANGLE = 8
WAVE_NONE     = 9
WAVE_ZERODIV  = 10
WAVE_h        = 11
WAVE_H        = 12

WAVE_MAP = { # prepare for better wave system
"square": WAVE_SQUARE,
"pulse": WAVE_PULSE,
"sine": WAVE_SINE,
"sawtooth": WAVE_SAWTOOTH,
"sample": WAVE_SAMPLE,
"n1b": WAVE_NOISE1B,
"n": WAVE_NOISE,
"wavetable": WAVE_TABLE,
"triangle": WAVE_TRIANGLE,
"none": WAVE_NONE,
"ZeroDivisionError": WAVE_ZERODIV,
"h": WAVE_h,
"H": WAVE_H,
}

INTERP_NONE = 0
INTERP_LIN  = 1 # TODO: add gaussian?

INTERP_MAP = {
"none": INTERP_NONE,
"linear": INTERP_LIN
}



def clamp(val=0, mn=0, mx=9):
    return min(mx, max(mn, val))

from math import pi, tau, sin, floor, ceil
import FurWave  # custom wav writer; i made it because the builtin one didnt have support for chunks and now i use it because im just used to
from random import random
try:
    import numpy as np
except ImportError:
    raise ModuleNotFoundError("NumPy required because everything else here requires it.")

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
        #self.square     = "square";    self.pulse    = "pulse"
        #self.sine       = "sine";      self.sawtooth = "sawtooth"
        #self.sample     = "pcm"
        #self.noise_1bit = "n1b";       self.noise    = "n"
        #self.wt         = "wavetable"; self.triangle = "triangle"

        # coming: more types; replaced with the closest ones by sound
        # self.fm = self.sine  # fm will likely instead become alive in own Operator class
        #self.xor_triangle = self.pulse
        #self.xor_sine = self.sine;   self.xor_sawtooth = self.sawtooth

        # special
        #self.test = self.square
        #self.unimplemented = self.sine
        #self.none = "none"
        #self.h = "h"
        #self.H = "H"
        #self.ZeroDivisionError = "ZeroDivisionError"  # i dare you use it.

        # interpolation types
        self.i_none = "none"
        self.i_lin  = "linear"
        
        # common
        self.c_type = WAVE_MAP.get(type_, WAVE_SQUARE)
        self.p_width = abs(width)
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = 44100 if not sample_rate or sample_rate < 1 else sample_rate # sample rate of the channel; also affects base sample playback freq
        
        self.adsr = np.array([.125, 1, .5, 2, 1.2], np.float32)  # Attack, Decay, Sustain, Decay 2, Release
        self.env_state = 0  # envelope state
                            # 0: attack
                            # 1: decay1
                            # 2: sustained
                            # 3: decay2
                            # 4: released
                            # 5: no sound
        self.env_y = 0  # envelope vol multiplier
        self.env_acc = ((1 / (self.sample_rate * self.adsr[0])) * (1 - self.env_y)) if self.adsr[0] > 0 else 1  # rate accumulator
        
        # special
        self.phase = self.init_phase = phase
                            # will be updated when the channel is asked to update
                            # used to calculate next phase. basically, points at where
                            # the playhead is in the wave
        self.panning = clamp(panning, -1, 1) # channel panning. self-explanatory
        self.volume = clamp(volume, 0, 1)
        self.i_type = interpolation
        self.length = abs(length) if length else 16
        self.skip_sound = False  # similar to None wave but is used when another wave is in use
        
        self._finish_setup_() # validate some stuff so it doesn't die
        
        # internal stuff
        self._freq = 0  # would be funny if this causes a div by 0 error somewhere ever
        
    def _finish_setup_(self):
                    
        if isinstance(self.c_type, int):
            # virtually any wave aside from binary ones is a wavetable so you can get cool artefacts with low lengths
            # i have about no idea how to do that in realtime
            if self.c_type == WAVE_SQUARE:
                self.wavetable = [-1 if _ < self.length else 1 for _ in range(self.length * 2)] # the most basic waveform
            elif self.c_type == WAVE_PULSE:
                self.wavetable = [-1 if _ < (self.length * 2) * self.p_width else 1 for _ in range(self.length * 2)]
            elif self.c_type == WAVE_SINE:
                self.wavetable = [sin(pi / self.length * _) for _ in range(self.length * 2)]
            elif self.c_type == WAVE_SAWTOOTH:
                self.wavetable = [(_ / self.length * 2) * 2 - 1 for _ in range(self.length * 2)]
                # normalization here and in tri wave is because with low length it simply does not go high enough to reach 1
                centerer = (1-max(self.wavetable))/2
                for i in range(len(self.wavetable)):
                    self.wavetable[i] += centerer
                maximizer = 1/max(self.wavetable)
                for i in range(len(self.wavetable)):
                    self.wavetable[i] *= maximizer
            elif self.c_type == WAVE_TRIANGLE:
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
            elif self.c_type == WAVE_SAMPLE:
                if not self.wavetable:
                    raise ValueError("where wave")
                self.length = len(self.wavetable)
            elif self.c_type == WAVE_TABLE:
                if not self.wavetable:
                   raise ValueError("where wave")
                self.length = len(self.wavetable)
            elif self.c_type == WAVE_NONE:
                pass
            elif self.c_type == WAVE_NOISE1B:  # noise gen is wavetable as i have no idea how to go without it as otherwise it will be updated every sample
                self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]  # and we want controllable pitchs
                self.length = 16  # fixed at length 16 to roughly be in pitch with other oscillators as they compensate for higher pitches
            elif self.c_type == WAVE_NOISE:      # by higher phase step which in case of noise means higher frequency
                self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]  # since it is stuck at 16, it might be unsuitable for
                self.length = 16  # unique timbres like classic atari basses so you might want to opt for wavetable
            elif self.c_type == WAVE_h:
                self.wavetable = [104]
            elif self.c_type == WAVE_H:
                self.wavetable = [72]
            elif self.c_type == WAVE_ZERODIV:
                self.wavetable = []
            else:
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
    
    def update(self, suppress_phase_update=False, suppress_noise_update=False):
        out, phase_reset_flag = 0, False
        
        WAVE_LEN = self.length * 2
        #if WAVE_LEN != len(self.wavetable):
        #    WAVE_LEN = len(self.wavetable)
        #    self.length = WAVE_LEN
            # костыль костылём, но будет работатт хоть как-то
        #print("what")
        if self.c_type != WAVE_NONE:
            # envelope update logic
            #print(f"acc {self.env_acc}\n"
            #      f"sta {self.env_state}\n"
            #      f"env {self.env_y}"
            #      )
            match self.env_state:
                case 0:
                    self.env_y += self.env_acc
                    if self.env_y >= 1:
                        #print("advance")
                        self.env_y = 1
                        self.__update_envelope__(1)
                case 1:
                    self.env_y -= self.env_acc
                    if self.env_y <= self.adsr[2]:
                        #print("advance")
                        self.__update_envelope__(2)
                case 2:
                    if not self.adsr[3] < 0:
                        #print("advance")
                        self.__update_envelope__(3)
                case 3:
                    self.env_y -= self.env_acc
                    if self.env_y <= 0:
                        #print("advance")
                        self.__update_envelope__(5)
                case 4:
                    self.env_y -= self.env_acc
                    if self.env_y <= 0:
                        self.__update_envelope__(5)
                    
        # do a little funny trick: set the output to whatever position we land at right now, *then* increase phase.
        # this is done to make phase 0 the default phase instead of outputting next phase.
        if self.c_type not in [WAVE_NONE, WAVE_NOISE1B, WAVE_NOISE] and not self.skip_sound:
            phase = self.phase * WAVE_LEN
            WAVE_LEN_H = WAVE_LEN / 2
            #print(phase)
            idx = floor(phase) % WAVE_LEN
            Fphase = floor(phase)
            Cphase = ceil(phase)
            match self.i_type:
                case self.i_none:
                    if self.c_type == WAVE_SQUARE:
                        #print(-1 if phase < WAVE_LEN_H else 1)
                        # why do we need to use a wave when we use pulse or square
                        # if its cheaper to generate it on the fly when without interpolation
                        # this comes with a slight change: pwm will no longer sound blocky on low lengths
                        out = -1 if phase < WAVE_LEN_H else 1
                    elif self.c_type == WAVE_PULSE: 
                        out = -1 if phase < WAVE_LEN * 2 * self.p_width else 1 # i accidentally generated a square from 0 to 1 instead of -1 to 1 :wilted_rose:
                    else: out = self.wavetable[idx]
                case self.i_lin:
                    out = (
                        self.wavetable[idx] - 
                        (
                            (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (phase - Fphase)
                        )
                    )
        elif self.c_type == WAVE_NONE or self.skip_sound:  # if we have a special "none" wave, straight up ignore the sound logic and just
            self.phase = (self.phase + (self._freq / self.sample_rate))  # update the phase; also when skipping sound, obviously
            phase_reset_flag = self.phase > 1
            self.phase %= 1 
            return (0, 0, phase_reset_flag)
            
        elif self.c_type in [WAVE_NOISE1B, WAVE_NOISE]:  # if we have either noise, then force no interpolation as i have no fucking idea how to deal with that
            out = self.wavetable[floor(self.phase * WAVE_LEN) % WAVE_LEN]  # and do you even really need one for noise
            
        if not suppress_phase_update:
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            if phase_reset_flag:
                if self.c_type == WAVE_NOISE1B and not suppress_noise_update:  # generate noise packets
                    self.wavetable = [(round(random()) -.5) * 2 for _ in range(WAVE_LEN * 2)]
                elif self.c_type == WAVE_NOISE and not suppress_noise_update:
                    self.wavetable = [(random() -.5) * 2 for _ in range(WAVE_LEN * 2)]
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
        return (out * lMult * self.volume * self.env_y, out * rMult * self.volume * self.env_y, phase_reset_flag)
    
    def phase_reset(self):
        self.phase = self.init_phase
    
    def change_wave(self,  # this is basically a copy of some init stuff, except as a separate function.
        type_:         str         = "square",
        width:         float | int = .25,
        length:        int         = 256,
        wavetable:     list[int]   = None,
    ):
        self.c_type = WAVE_MAP.get(type_, WAVE_SQUARE)
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
        if self.c_type == WAVE_NOISE1B:  # generate noise packets but as a function
            self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]
        elif self.c_type == WAVE_NOISE:
            self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]
    
    def release_channel(self):  # release adsr
        self.env_acc = (1 / (self.sample_rate * self.adsr[4])) * self.env_y  # same as below but lower speed for lower volumes
        self.env_state = 4
        #print("key off")
    def cut_channel(self):      # what this flag does i pretty much told you already
        self.env_state = 5      # but in envelope context it is cheaper to do this as
        self.skip_sound = True  # if you change the wave, you'll have to manually change it back
        #print("key cut")
    def press_channel(self, force_reset=True): # press adsr
        if force_reset:  # reset current envelope multiplier
            self.env_y = 0
        self.env_acc = ((1 / (self.sample_rate * self.adsr[0])) * (1 - self.env_y)) if self.adsr[0] > 0 else 1  # account for not fully decayed sound by lowering speed
        self.env_state = 0
        self.skip_sound = False
        #print("key on")
    def set_attack(self, attack = 0.):
        """
        Set attack time, in seconds
        """
        self.adsr[0] = attack
        self.__update_envelope__(self.env_state)
    def set_decay1(self, decay = 1.):
        """
        Set decay 1 time, in seconds
        """
        self.adsr[1] = decay
        self.__update_envelope__(self.env_state)
    def set_sustain(self, level = 1.):
        """
        Set sustain level, %
        """
        self.adsr[2] = level
        self.__update_envelope__(self.env_state)
    def set_decay2(self, decay = .25):
        """
        Set decay 2 time, in seconds
        """
        self.adsr[3] = decay
        self.__update_envelope__(self.env_state)
    def set_release(self, release = .125):
        """
        Set release time, in seconds
        """
        self.adsr[4] = release
        self.__update_envelope__(self.env_state)
    
    # prelimary envelope support
    def __update_envelope__(self, state = 5):
        """
        __update_envelope__ help
        """
        #print(f"envelope updated: {state}")
        match state:
            case 0:
                self.skip_sound = False
                self.env_state = 0
                if self.adsr[0] > 0:
                    self.env_acc = ((1 / (self.sample_rate * self.adsr[0])) * (1 - self.env_y))
                else:
                    self.env_acc = 1
            case 1:
                self.env_state = 1
                if self.adsr[1] > 0:
                    self.env_acc = ((1 / (self.sample_rate * self.adsr[1])) * self.env_y)
                else:
                    self.env_acc = 1
            case 2:
                if self.adsr[3] > 0:
                    self.__update_envelope__(3)
                else:
                    self.env_y = self.adsr[2]
            case 3:
                self.env_state = 3
                if self.adsr[3] > 0:
                    self.env_acc = ((1 / (self.sample_rate * self.adsr[3])) * self.env_y)
                else:
                    self.env_acc = 1
            case 4:
                self.env_state = 4
                if self.adsr[4] > 0:
                    self.env_acc = ((1 / (self.sample_rate * self.adsr[4])) * self.env_y)
                else:
                    self.env_acc = 1
            case 5:
                self.env_state = 5
                self.env_acc = 0
                self.env_y = 0
                self.skip_sound = True
                
    def __toggle_envelope__(self):
        if self.env_state < 6:
            self.env_state = 5 * self.env_state
            #print("env pause")
        else:
            self.env_state //= 5
            #print("env resume")
    def __force_advance_envelope_state__(self):
        self.__update_envelope__((self.env_state + 1) % 5)
        #print(f"env state forced to {self.env_state}")
    def __force_envelope_state__(self, state):
        self.__update_envelope__(state % 5)
        #print(f"env state set to {self.env_state}")
    
##############################
##############################
class ChannelGroup:
    
    def __init__(self,
        detune: int | float = 0
    ):
        self.channels = []  # channels to walk through
        self.detune = detune  # optional parameter that can be used to produce superwaves
                              # detunes in 100th of a hertz
        self.center_chan = 0
        
        # the settings of this class by default are quite limiting
        # but you can access the channel array and therefore
        # make advanced edits to contained channels if you need
    
    def add_channel(self,
        type = "sawtooth",
        sample_rate = 44100,
        volume = .5,
        length = 16,
    ):
        self.channels.append(Channel(type_=type,sample_rate=sample_rate,volume=volume,length=length))
        self.center_chan = len(self.channels) // 2
    
    def set_base_freq(self, freq = 440):
        if self.detune != 0:
            for _, ch in enumerate(self.channels):
                if _ < self.center_chan:
                    ch._freq = freq - ((self.detune / 100) * (self.center_chan - _))
                else:
                    ch._freq = freq + ((self.detune / 100) * (_ - self.center_chan))
        else:
            for _ in self.channels:
                _._freq = freq
    
    def update(self, suppress_phase_update=False, suppress_noise_update=False):
         out = np.array([0, 0], np.float32)
         for _ in self.channels:
             out += _.update(suppress_phase_update, suppress_noise_update)[:2]
         out /= len(self.channels)
         return out
     
    def randomize_phase(self):
        for _ in self.channels:
            _.phase = random()
##############################
##############################

def freq_from_key(key = 60, tune = 440): # for some tests
    return (2 ** ((-57 + key) / 12)) * tune

def key_from_note(note = "c-5"):
    dat = list(note.lower().split("-"))  # TODO: suppoet negatine octaves
    dat[1] = int(dat[1])
    notes = {"c": 0, "c#": 1,
             "d": 2, "d#": 3,
             "e": 4,
             "f": 5, "f#": 6,
             "g": 7, "g#": 8,
             "a": 9, "a#": 10,
             "b": 11, }
    return (12 * dat[1]) + notes.get(dat[0], 0)


if __name__ == "__main__":
    # main loop where i test stuff; advanced stuff
    # i really thought i had to do everything manually and
    # now i realized i can just slam shit into an array
    # and call it a day lol
    
    sr = 30000 # literally everything depends on the sample rate, including bpm since its all in a for loop
    length = 6.4 * 2 #length
    print("READY")
    ChannelNoise1 = Channel(
        type_ = "square",
        sample_rate = sr,
        interpolation = "none",
        length = 8,
        panning = 0,
        volume = .1 ,
        width = 0
    )
    ChannelNoise2 = Channel(
        type_ = "square",
        sample_rate = sr,
        interpolation = "none",
        length = 8,
        panning = .7,
        volume = .1,
        width = 0
    )
    ChannelNoise3 = Channel(
        type_ = "square",
        sample_rate = sr,
        interpolation = "none",
        panning = -.7,
        length = 8,
        volume = .1,
        width = 0
    )

    ChannelNoise1.set_attack(.0); ChannelNoise1.set_decay1(.06);ChannelNoise1.set_sustain(.3);ChannelNoise1.set_decay2(.1);ChannelNoise1.set_release(0)
    ChannelNoise2.set_attack(1/16);ChannelNoise2.set_decay1(.06);ChannelNoise2.set_sustain(.3);ChannelNoise2.set_decay2(.1);ChannelNoise2.set_release(0)
    ChannelNoise3.set_attack(2/16);ChannelNoise3.set_decay1(.06);ChannelNoise3.set_sustain(.3);ChannelNoise3.set_decay2(.1);ChannelNoise3.set_release(0)
    
    #Supersaw = ChannelGroup(detune=120)
    #for _ in range(8):
    #    Supersaw.add_channel(length=7) # adds 8 channels
    #Supersaw.set_base_freq(65.077 * 8)
    #Supersaw.randomize_phase()
    f = freq_from_key
    k = key_from_note
    
    master_tune = 450
    notes_pre = [
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "b-4", "a-4", "d-5",
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "d-5", "e-5", "b-4",
        
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "b-4", "a-4", "d-5",
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "f#-4","a-4", "d-5", "f#-5","d-5", "e-5",
        
    ]
    notes = [f(k(_), master_tune) for _ in notes_pre]
    
    gates = [ 1,]
    vols =  [ .1,]
    seq = 0
    
    render = []
    curSample = np.array([0,0], np.float32)  # current sample
    
    import time
    start = time.perf_counter()
    for _ in range(floor(sr*length)):
        # this thing works at the peak of its performance and takes
        # about 10 seconds to generate 10 seconds of audio on my phone
        # could also be because i have python 3.11 on my phone rather than 3.14
        # which supposedly has optimizations and is generally faster
        # takes about quarter to a third the required time on my laptop
        
        #arr.extend([Supersaw.update()[0]])
        #arr.extend([(ChannelPulse.update()[0] + ChannelNoise.update()[0])/2,(ChannelTooth.update()[0] + ChannelNoise.update()[0])/2])  # 2 channels mapped to stereo
        #arr.extend([ChannelNoise.update()[0], ChannelNoise2.update()[0]])
        #arr.extend([ChannelNoise.update()[0], ChannelNoise2.update()[0]])
        #arr.extend([ChannelNoise.update(suppress_noise_update=True)[0], ChannelSquare.update()[0]])
        curSample  = ChannelNoise1.update(suppress_noise_update=True)[:2]
        curSample += ChannelNoise2.update(suppress_noise_update=True)[:2]
        curSample += ChannelNoise3.update(suppress_noise_update=True)[:2]
        #curSample /= 1
        render.extend(curSample)
        # technically with how i did the noise ingraining here, it is updated twice as quicky and is full independent stereo
        #ChannelPulse.change_width(ChannelPulse.p_width + (.125/sr) % 1) # pwm is STUPIDLY expensive to generate when using interpolation
        #print(f"pw {ChannelPulse.p_width}")
        #print("alive")
        if not _ % sr:
            print(f"second {1 + (_ // sr)} generated")
        if not _ % (sr//10):
            #ChannelNoise.force_generate_new_noise_packets()
            #ChannelNoise2.force_generate_new_noise_packets()
        #if not _ % (sr//10):
            ChannelNoise1._freq = notes[seq]
            ChannelNoise1.volume = vols[seq % len(vols)] * 2
            ChannelNoise2._freq = notes[seq - 3] - (notes[seq]/128)
            ChannelNoise2.volume = vols[seq % len(vols)] * .5
            ChannelNoise3._freq = notes[seq - 6] + (notes[seq]/128)
            ChannelNoise3.volume = vols[seq % len(vols)] * .25
            if not gates[seq % len(gates)]:
                pass
            else:
                ChannelNoise1.press_channel(0)
                ChannelNoise2.press_channel(0)
                ChannelNoise3.press_channel(0)
            #print(note, notes[note])
            seq = (seq + 1) % len(notes)

        #ChannelNoise.volume = .25 + (.75 * ((1 / (sr // 2)) * (_ % (sr // 2))))
        #ChannelNoise2.volume = .25 + (.75 * ((1 / (sr // 2)) * (_ % (sr // 2))))
        #if _ == sr * 2:
        #    ChannelNoise.press_channel(False)  # whats funny is that the skeleton for the adsr
        #    ChannelNoise2.press_channel()      # was made in about 2 (!) minutes
        #if _ == sr * 3:
        #    ChannelNoise.release_channel()
        #    ChannelNoise2.release_channel()
        #if _ == sr * 3.5:
        #    ChannelNoise.press_channel()
        #    ChannelNoise2.press_channel()
        #if _ == sr * 4:
        #    ChannelNoise.cut_channel()
        #    ChannelNoise2.cut_channel()
        #if _ == sr * 4.5:
        #    ChannelNoise.set_attack(.125)
        #    ChannelNoise2.set_attack(0.125)
        #    ChannelNoise.press_channel()
        #    ChannelNoise2.press_channel()
        #if _ == sr * 4.75:
            #ChannelNoise.__force_envelope_state__(4)
            #ChannelNoise2.__force_envelope_state__(4)
        #    ChannelNoise.__force_advance_envelope_state__()
        #    ChannelNoise2.__force_advance_envelope_state__()
    elapsed = time.perf_counter() - start
    print(f"{elapsed:.3f}/{length}s")
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
    with FurWave.WaveWriter(
                    channels=2,
                    samplerate=sr*3,
                    bitdepth=32.,
                    data=render,
                    packed=True,
                    ) as Wave:
        Wave.write_file(f"fursound_test.wav")
        