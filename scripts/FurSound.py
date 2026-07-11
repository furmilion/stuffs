"""
FurSound
This is my custom sound engine.
The concept is as simple as it gets: iterate over a wave form at sample rate.

There is a concept of a "channel".
A channel is the sound producing unit of the engine.

The following types of channels are available:
    
# Channel
The base channel class.
Has the following properties:
    - Volume
    - Panpot
    - Coarse tune
    - A-4 tune
    - Sample rate, which I bet is self-explanatory.
    - Interpolation type
    - Waveform (i.e. square, wavetable etc.)
    - Pulse width for pulse wave
    - Wavetable for wavetable and sample waves
    - ADSD2R
## OperatorChannel
Inherits Channel's properties,
with the addition of a single parameter
to the update() function
### CHANGES
    - update() now takes an additional argument: modulation input
    - update() now outputs an additional value: raw sample value
    - update() now outputs phase reset flag at 4th position, with raw sample value taking the 3rd place
    - new class attribute last_output: holds the last raw sample value of the update() function, useful for feedback

# FMChannel
The FM channel class.
Does not inherit the base class
and instead has its own properties
due to the fact that it is a collection
of OperatorChannels, and thus having
no envelope by itself.
Has the following properties:
    - Volume
    - Panpot
    - Coarse tune
    - A-4 tune
    - Sample rate
    - Amount of operators (static)
    - Operator connection matrix (not corrected at init time, so be careful not to fuck it up)
    - Operator base frequency multipliers
    - Operator direct output volumess
    - Operator modulation volumes
    - Operator feedback multipliers
    - Operator modulation input multipliers
    - Operator waveforms
    - (TODO) Operator default waveform lengths

TODO:
# SampleChannel
Inherits most of the Channel's properties
Has the following properties:
    - Volume
    - Panpot
    - Coarse tune
    - A-4 tune
    - Wavetable for sample waves
    - Sample rate
    - Sample A-4 tune
    - Sample loop type (none, forward, backward, bi)
    - Sample loop start point
    - Sample loop end point
### CHANGES
    - phase now represents current sample position in range(0, len(sample))
    - sample is automatically truncated to the loop end point, if a loop type is not 'none'
    - Frequency is calculated as a ratio of requested frequency to A-4 tune and then multiplied by sample tune
    - update() no longer checks the waveform type as it always is supposed to be sample
    - update() sends phase reset flag upon crossing the loop end point



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
def opl_approximate_curve_1(value: float = 127):
    """approximates yamaha's fm volume curve using a badass formula"""
    return ((value**10)/127)/(127**9)
def opl_approximate_curve_2(value: float = 127, table_resolution=127):
    """same as above except more accurate"""
    return 1/(10**(((table_resolution - value)*.75)/20))

def freq_from_key(key = 60, tune = 440): # for some tests
    if isinstance(key, int):
        return (2 ** ((-57 + key) / 12)) * tune
    else:
        return key

def key_from_note(note = "c-5"):
    #print(note)
    if note[2].isnumeric():
        dat = [note[:2].lower(), note[2]]
        dat[1] = int(dat[1])
    else:
        dat = [note[:3].lower()]
    #print(dat)
    notes = {"c-": 0, "c#": 1,
             "d-": 2, "d#": 3,
             "e-": 4,
             "f-": 5, "f#": 6,
             "g-": 7, "g#": 8,
             "a-": 9, "a#": 10,
             "b-": 11, 
             "c_": 0, "c+": 1,
             "d_": 2, "d+": 3,
             "e_": 4,
             "f_": 5, "f+": 6,
             "g_": 7, "g+": 8,
             "a_": 9, "a+": 10,
             "b_": 11,
             
             "rel": "rel",
             "cut": "cut",
             "...": "...",
             }
    if notes[dat[0]] in [notes["rel"], notes["cut"], notes["..."],]:
        return notes[dat[0]]
    if dat[0] in notes and list(notes.keys()).index(dat[0]) > 12:
        return (-12 * dat[1]) + notes.get(dat[0], 0)
    return (12 * dat[1]) + notes.get(dat[0], 0)

WAVE_SQUARE      = 0   # OPL #6
WAVE_PULSE       = 1   #
WAVE_SINE        = 2   # OPL #0
WAVE_SAWTOOTH    = 3   #
WAVE_SAMPLE      = 4   # TODO
WAVE_NOISE1B     = 5   #
WAVE_NOISE       = 6   #
WAVE_TABLE       = 7   #
WAVE_TRIANGLE    = 8   #
WAVE_NONE        = 9   #
WAVE_HALFSINE    = 10  # OPL #1
WAVE_ABSSINE     = 11  # OPL #2
WAVE_QRTSINE     = 12  # OPL #3
WAVE_EVENSINE    = 13  # OPL #4
WAVE_EABSSINE    = 14  # OPL #5
WAVE_ACCUMULATOR = 15  # OPL #7
#WAVE_ZERODIV     = 16
#WAVE_h           = 17
#WAVE_H           = 18

WAVE_MAP = { # prepare for better wave system
"sine": WAVE_SINE,
"half_sine": WAVE_HALFSINE,
"abs_sine": WAVE_ABSSINE,
"quarter_sine": WAVE_QRTSINE,
"even_sine": WAVE_EVENSINE,
"even_abs_sine": WAVE_EABSSINE,
"square": WAVE_SQUARE,
"pulse": WAVE_PULSE,
"opl_accumulator": WAVE_ACCUMULATOR, "log_sawtooth": WAVE_ACCUMULATOR,
"sawtooth": WAVE_SAWTOOTH,
"sample": WAVE_SAMPLE,
"n1b": WAVE_NOISE1B,
"n": WAVE_NOISE,
"wavetable": WAVE_TABLE,
"triangle": WAVE_TRIANGLE,
"none": WAVE_NONE,
#"ZeroDivisionError": WAVE_ZERODIV,
#"h": WAVE_h,
#"H": WAVE_H,
}

INTERP_NONE = 0
INTERP_LIN  = 1
#INTERP_GAUSSIAN = 2  # TODO: gaussian?
INTERP_RECTSINE = 2
INTERP_SINE = 3

INTERP_MAP = {
"none": INTERP_NONE,
"linear": INTERP_LIN,
#"gauss": INTERP_GAUSSIAN,
"rectsine": INTERP_RECTSINE,
"sine": INTERP_SINE,
}

LOOP_NONE = 0
LOOP_FORWARD = 1
LOOP_BACKWARD = 2
LOOP_PINGPONG = 3

LOOP_TYPES = {
"none": LOOP_NONE,
"forward": LOOP_FORWARD,
"backward": LOOP_BACKWARD,
"bi": LOOP_PINGPONG,
}



def clamp(val=0, mn=0, mx=9):
    return min(mx, max(mn, val))

from math import pi, tau, sin, floor, ceil, e as math_e
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
                 length:        int         = 512,  # the length of the preset waves
                 wavetable:     list[int]   = None, # wavetable
                 sample_rate:   int         = 44100, # default sample rate...
                 phase:         float | int = 0, # ...phase...
                 panning:       float | int = 0, #...pan...
                 volume:        float | int = 1, #...and volume.
                 interpolation: str         = "none",
                 tune = 440,
                 coarse_tune = 0,
                 ):
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
        self.last_output = 0
        self.phase = self.init_phase = phase
                            # will be updated when the channel is asked to update
                            # used to calculate next phase. basically, points at where
                            # the playhead is in the wave
        self.panning = np.float16(clamp(panning, -1, 1)) # channel panning. self-explanatory
        self.__volume__ = np.float16(clamp(volume, 0, 1))
        self.i_type = INTERP_MAP.get(interpolation, INTERP_NONE)
        self.length = np.ushort(abs(length) if length else 16)
        self.skip_sound = False  # similar to None wave but is used when another wave is in use
        
        self._finish_setup_() # validate some stuff so it doesn't die
        
        # internal stuff
        self.channel_tune = tune
        self.channel_coarse_tune = coarse_tune
        self._freq = 0  # would be funny if this causes a div by 0 error somewhere ever     
    def _finish_setup_(self):
                    
        if isinstance(self.c_type, int):
            # virtually any wave aside from binary ones is a wavetable so you can get cool artefacts with low lengths
            # i have about no idea how to do that in realtime
            if self.c_type == WAVE_SQUARE:        # 6
                self.wavetable = [-1 if _ < self.length else 1 for _ in range(self.length * 2)] # the most basic waveform
            elif self.c_type == WAVE_PULSE:
                self.wavetable = [-1 if _ < (self.length * 2) * self.p_width else 1 for _ in range(self.length * 2)]
            
            elif self.c_type == WAVE_SINE:        # 0
                self.wavetable = [sin(pi / self.length * _) for _ in range(self.length * 2)]
            elif self.c_type == WAVE_HALFSINE:    # 1
                self.wavetable = [abs(sin(pi / self.length * _)) if not _//self.length else 0 for _ in range(self.length * 2)]
            elif self.c_type == WAVE_ABSSINE:     # 2
                self.wavetable = [abs(sin(pi / self.length * _)) for _ in range(self.length * 2)]
            elif self.c_type == WAVE_QRTSINE:     # 3
                self.wavetable = [abs(sin(pi / self.length * _)) if not (_%self.length)//(self.length//2) else 0 for _ in range(self.length * 2)]
            elif self.c_type == WAVE_EVENSINE:    # 4
                self.wavetable = [sin(pi / self.length * _ * 2) if _ < self.length else 0 for _ in range(self.length * 2)]
            elif self.c_type == WAVE_EABSSINE:    # 5
                self.wavetable = [abs(sin(pi / self.length * _ * 2)) if _ < self.length else 0 for _ in range(self.length * 2)]     
            elif self.c_type == WAVE_ACCUMULATOR:  # 7
                self.wavetable = np.array([(_ / self.length * 2) - 1 for _ in range(self.length * 2)], np.float16)
                self.wavetable += (1-max(self.wavetable))/2
                self.wavetable *= -(1/max(self.wavetable))
                self.wavetable **= 9
                
            elif self.c_type == WAVE_SAWTOOTH:
                self.wavetable = np.array([(_ / self.length * 2) * 2 - 1 for _ in range(self.length * 2)], np.float16)
                # normalization here and in tri wave is because with low length it simply does not go high enough to reach 1
                self.wavetable += (1-max(self.wavetable))/2
                self.wavetable *= 1/max(self.wavetable)
            elif self.c_type == WAVE_TRIANGLE:
                # unfortunately it was too troublesome for me to get triangle working properly
                # so instead i opted for a saw generator extended by itself reversed
                # which also made all waves 2 times longer since now length isnt just length of the
                # entire wave but only of one slope
                self.wavetable = np.array([(_ / self.length) * 2 - 1 for _ in range(self.length)], np.float16)
                self.wavetable += (1-max(self.wavetable))/2
                self.wavetable *= 1/max(self.wavetable)
                #self.wavetable.extend(self.wavetable[::-1])
            elif self.c_type == WAVE_SAMPLE:
                if not self.wavetable:  # todo: parameters (loop points etc)
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

        self.wavetable = np.array(self.wavetable, np.float16)   
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
            #Cphase = ceil(phase)
            if self.i_type == INTERP_NONE:
                if self.c_type == WAVE_SQUARE:
                    #print(-1 if phase < WAVE_LEN_H else 1)
                    # why do we need to use a wave when we use pulse or square
                    # if its cheaper to generate it on the fly when without interpolation
                    # this comes with a slight change: pwm will no longer sound blocky on low lengths
                    out = -1 if phase < WAVE_LEN_H else 1
                elif self.c_type == WAVE_PULSE:
                    out = -1 if phase < WAVE_LEN * self.p_width else 1 # i accidentally generated a square from 0 to 1 instead of -1 to 1 :wilted_rose:
                else: out = self.wavetable[idx]
            elif self.i_type == INTERP_LIN:
                out = (
                    self.wavetable[idx] -
                    (
                        (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (phase - Fphase)
                    )
                )
            elif self.i_type == INTERP_RECTSINE:
                out = (
                    self.wavetable[idx] -
                    (
                        (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * sin((pi * (phase - Fphase)) / 2)
                    )
                )
            elif self.i_type == INTERP_SINE:
                out = (
                    self.wavetable[idx] -
                    (
                        (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (sin((pi * ((phase - Fphase) * 2 - 1)) / 2) / 2 + .5)
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
        self.last_output = out
        return (out * lMult * self.__volume__ * self.env_y, out * rMult * self.__volume__ * self.env_y, phase_reset_flag)
    def phase_reset(self):
        self.phase = self.init_phase
    def change_wave(self):
        self.c_type = WAVE_MAP.get(type_, WAVE_SQUARE)
        self.p_width = abs(width)
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self._finish_setup_()
    def change_width(self, width: float | int = .25):
        self.p_width = abs(width) % 1

        if self.i_type != INTERP_NONE and self.c_type == WAVE_PULSE:
            self.wavetable = np.array([-1 if _ < (self.length * 2) * self.p_width else 1 for _ in range(self.length * 2)], np.float16)
    def set_volume(self, volume: float = 1.):
        self.__volume__ = np.float16(volume)
    def force_generate_new_noise_packets(self):
        if self.c_type == WAVE_NOISE1B:  # generate noise packets but as a function
            self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]
        elif self.c_type == WAVE_NOISE:
            self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]
    def parse_key(itisi, key, legato=False): 
        if key == "cut":
            self.cut_channel()
        elif key == "rel":
            self.release_channel()
        elif key == "...":
            pass
        else:
            self._freq = freq_from_key(key + self.channel_coarse_tune, self.channel_tune)
            if not legato:
                self.press_channel(1, 1)
    def release_channel(self):  # release adsr
        #print("key off")
        self.env_acc = (1 / (self.sample_rate * self.adsr[4])) * self.env_y  # same as below but lower speed for lower volumes
        self.env_state = 4
    def cut_channel(self):      # what this flag does i pretty much told you already
        #print("key cut")
        self.env_state = 5      # but in envelope context it is cheaper to do this as
        self.skip_sound = True  # if you change the wave, you'll have to manually change it back
    def press_channel(self, force_reset=True, phase_reset=False): # press adsr
        #print("key on")
        if force_reset:  # reset current envelope multiplier
            self.env_y = 0
        if phase_reset:
            self.phase_reset()
        self.env_acc = ((1 / (self.sample_rate * self.adsr[0])) * (1 - self.env_y)) if self.adsr[0] > 0 else 1  # account for not fully decayed sound by lowering speed
        self.env_state = 0
        self.skip_sound = False
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
            #print("env pause")
            self.env_state += 6
        else:
            #print("env resume")
            self.env_state -= 6
    def __force_advance_envelope_state__(self):
        #print(f"env state forced to {self.env_state}")
        self.__update_envelope__((self.env_state + 1) % 5)
    def __force_envelope_state__(self, state):
        #print(f"env state set to {self.env_state}")
        self.__update_envelope__(state % 5)

class OperatorChannel(Channel):
    def __init__(self,
                 type_:         str         = "square", # the default wave upon class spawn
                 width:         float | int = .25,    # pulse width for the pulse wave
                 length:        int         = 512,  # the length of the preset waves
                 wavetable:     list[int]   = None, # wavetable
                 sample_rate:   int         = 44100, # default sample rate...
                 phase:         float | int = 0, # ...phase...
                 panning:       float | int = 0, #...pan...
                 volume:        float | int = 1, #...and volume.
                 interpolation: str         = "none"
                 ):
        super().__init__(type_, width, length, wavetable, sample_rate, phase, panning, volume, interpolation,)
    def update(self,
               suppress_phase_update=False,
               suppress_noise_update=False,
               modulation: float = 0,  # additional value added to phase during calculation
               ):
        out, phase_reset_flag = 0, False

        WAVE_LEN = self.length * 2
        if self.c_type != WAVE_NONE:
            match self.env_state:
                case 0:
                    self.env_y += self.env_acc
                    if self.env_y >= 1:
                        # print("advance")
                        self.env_y = 1
                        self.__update_envelope__(1)
                case 1:
                    self.env_y -= self.env_acc
                    if self.env_y <= self.adsr[2]:
                        # print("advance")
                        self.__update_envelope__(2)
                case 2:
                    if not self.adsr[3] < 0:
                        # print("advance")
                        self.__update_envelope__(3)
                case 3:
                    self.env_y -= self.env_acc
                    if self.env_y <= 0:
                        # print("advance")
                        self.__update_envelope__(5)
                case 4:
                    self.env_y -= self.env_acc
                    if self.env_y <= 0:
                        self.__update_envelope__(5)

        if self.c_type not in [WAVE_NONE, WAVE_NOISE1B, WAVE_NOISE] and not self.skip_sound:
            phase = ((self.phase + modulation) % 1) * WAVE_LEN
            WAVE_LEN_H = WAVE_LEN / 2
            idx = floor(phase) % WAVE_LEN
            Fphase = floor(phase)
            # Cphase = ceil(phase)
            if self.i_type == INTERP_NONE:
                if self.c_type == WAVE_SQUARE:
                    out = -1 if phase < WAVE_LEN_H else 1
                elif self.c_type == WAVE_PULSE:
                    out = -1 if phase < WAVE_LEN * self.p_width else 1
                else:
                    out = self.wavetable[idx]
            elif self.i_type == INTERP_LIN:
                out = (
                        self.wavetable[idx] -
                        (
                                (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (phase - Fphase)
                        )
                )
            elif self.i_type == INTERP_RECTSINE:
                out = (
                        self.wavetable[idx] -
                        (
                                (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * sin(
                            (pi * (phase - Fphase)) / 2
                            )
                        )
                )
            elif self.i_type == INTERP_SINE:
                out = (
                        self.wavetable[idx] -
                        (
                                (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (
                                    sin((pi * ((phase - Fphase) * 2 - 1)) / 2) / 2 + .5)
                        )
                )


        elif self.c_type == WAVE_NONE or self.skip_sound:
            self.phase = (self.phase + (
                        self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            self.phase %= 1
            return (0, 0, phase_reset_flag)

        elif self.c_type in [WAVE_NOISE1B,
                             WAVE_NOISE]:
            out = self.wavetable[floor(self.phase * WAVE_LEN) % WAVE_LEN]

        if not suppress_phase_update:
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            if phase_reset_flag:
                if self.c_type == WAVE_NOISE1B and not suppress_noise_update:
                    self.wavetable = [(round(random()) - .5) * 2 for _ in range(WAVE_LEN * 2)]
                elif self.c_type == WAVE_NOISE and not suppress_noise_update:
                    self.wavetable = [(random() - .5) * 2 for _ in range(WAVE_LEN * 2)]
            self.phase %= 1
        lMult = 1 - abs(self.panning) if self.panning > 0 else 1
        rMult = 1 - abs(self.panning) if self.panning < 0 else 1
        self.last_output = out * self.__volume__ * self.env_y
        return (
                out * lMult * self.__volume__ * self.env_y,
                out * rMult * self.__volume__ * self.env_y,
                out * self.__volume__ * self.env_y,  # raw unpanned output
                phase_reset_flag
        )

class FMChannel:  
    def __init__(itisi,
                 operators =  2,
                 volume =     1,
                 panning =    0,
                 op_matrix =  [[1, 1],
                               [0, 1],],
                 op_mults =   [1, 1],
                 op_outputs = [0, 1],
                 op_volumes = [0, 1],
                 op_waves =   ["sine", "sine"],
                 op_tables =  [[0], [0]],
                 op_fb_mults =  [.2, 0],
                 op_mod_in_mults = [0, 1],
                 sample_rate = 44100,
                 tune = 440,
                 coarse_tune = 0,
                 ):
        itisi.operators = [OperatorChannel(panning=panning,
                                           volume=         op_volumes[_ % len(op_volumes)],
                                           type_=          op_waves[_ % len(op_waves)],
                                           wavetable=      op_tables[_ % len(op_tables)],
                                           sample_rate = sample_rate,
                                           ) for _ in range(operators)  # i probably shouldnt have the values wrap around but im nor sure yet
        ]
        itisi.op_count = operators
        itisi.op_matrix = op_matrix
        itisi.op_mults = op_mults
        itisi.op_outputs = op_outputs
        itisi.modulation_buffer = np.array([0 for _ in range(operators)], np.float16)
        
        itisi.op_fb_mults = op_fb_mults
        itisi.op_mod_in_mults = op_mod_in_mults
        itisi.master_volume = volume
        itisi.channel_tune = tune
        itisi.channel_coarse_tune = coarse_tune
        itisi._base_freq = 0
        
        itisi.last_output = 0
    def update(itisi,):  # this is gonna be very slow, you know the reason. 
        sample_buffer = np.array([0,0], np.float32)
        modulation_buffer = itisi.modulation_buffer.copy()
        itisi.modulation_buffer -= itisi.modulation_buffer
        
        for op, op_obj in enumerate(itisi.operators):
            op_feedback = (op_obj.last_output if itisi.op_matrix[op][op] else 0) * itisi.op_fb_mults[op]
            op_obj._freq = (itisi._base_freq * itisi.op_mults[op]) if itisi.op_mults[op] > 0 else (itisi._base_freq ** itisi.op_mults[op]) # if this raises an IndexError, it's *your* problem.
            output_buffer = op_obj.update(modulation=op_feedback + (modulation_buffer[op] * itisi.op_mod_in_mults[op]))
            # ^^^^
            # definetly your fault here becuse you *have* to do something shady to get it to spit an IndexError.
            # channel operator count is *not* dynamic, go figure
            # you are free to juggle the matrix but not the amount of the operators. this aint SCSP.
            # even SCSP can be considered just as a single 32-op channel, just with independent operator frequencies
            
            # print(
            # f"op                 {op}                  \n"
            # f"phase              {op_obj.phase}        \n"
            # f"fb_buf             {feedback_buffer   }        \n"
            # f"fb_buf_op          {feedback_buffer[op]}        \n"
            # f"fb_mul_op          {itisi.op_fb_mults[op]}        \n"
            # f"fb_buf_op_post     {feedback_buffer[op] * itisi.op_fb_mults[op]}        \n"
            # f"mod_buf_op         {modulation_buffer[op]}        \n"
            # f"lastout            {op_obj.last_output}  \n"
            # f"outbuf             {output_buffer}       \n"
            # f"opouts             {itisi.op_outputs}       \n"
            # f"opout              {itisi.op_outputs[op]}       \n"
            # f"sampbuf_expect     {sample_buffer + output_buffer[:2]}       \n"
            # f"sampbuf_expect_att {sample_buffer + (np.array(output_buffer[:2], np.float32) * itisi.op_outputs[op])}       \n",
            # end=""
            # )
            sample_buffer += (np.array(output_buffer[:2], np.float32) * itisi.op_outputs[op])
            # print(
            # f"sampbuf            {sample_buffer}       \n"
            # )
            for carrier in range(itisi.op_count):
                #itisi.feedback_buffer[op]        += output_buffer[2] if itisi.op_matrix[op][op] else 0
                # print(
                # f"OP_MTX      {itisi.op_matrix}\n"
                # f"OP_UPD      {op}\n"
                # f"OP_MOD      {carrier}\n"
                # f"OP_SELFMOD  {op == carrier}\n"
                # f"DO_MODULATE {itisi.op_matrix[op][carrier] if not op == carrier else False}\n"
                # )
                itisi.modulation_buffer[carrier] += output_buffer[2] if itisi.op_matrix[op][carrier] and not op == carrier else 0
            itisi.last_output = (output_buffer[0] + output_buffer[1]) / 2 
        return sample_buffer * itisi.master_volume
    def parse_key(itisi, key, legato=False): 
        if key == "cut":
            itisi.cut_channel()
        elif key == "rel":
            itisi.release_channel()
        elif key == "...":
            pass
        else:
            itisi._base_freq = freq_from_key(key + itisi.channel_coarse_tune, itisi.channel_tune)
            if not legato:
                itisi.press_channel(1, 1)
    def press_channel(itisi, force_reset=False, phase_reset=False): # TODO: individul operator envelope toggles for if you want to control them OPN-ExtCh3-style
        for operator in itisi.operators:
            operator.press_channel(force_reset, phase_reset)
    def release_channel(itisi,):
        for operator in itisi.operators:
            operator.release_channel()
    def cut_channel(itisi,):
        for operator in itisi.operators:
            operator.cut_channel()
    def set_attack(itisi,*attacks):
        for aid, attack in enumerate(attacks):
            itisi.operators[aid % itisi.op_count].set_attack(attack)
    def set_decay1(itisi,*decay1s):
        for did, decay1 in enumerate(decay1s):
            itisi.operators[did % itisi.op_count].set_decay1(decay1)
    def set_sustain(itisi,*sustains):
        for sid, sustain in enumerate(sustains):
            itisi.operators[sid % itisi.op_count].set_sustain(sustain)
    def set_decay2(itisi,*decay2s):
        for did, decay2 in enumerate(decay2s):
            itisi.operators[did % itisi.op_count].set_decay2(decay2)
    def set_release(itisi,*releases):
        for rid, release in enumerate(releases):
            itisi.operators[rid % itisi.op_count].set_release(release)

class SampleChannel(Channel):
    def __init__(self,
        sample:        list[int]   = [0],      # sample
        sample_rate:   int         = 44100,    # channel sample rate
        sample_tune:   int         = 28129,    # a-4 of sample
        sample_loop:   str         = "none",   # loop type
        loop_start:    int         = 0,        #
        loop_end:      int         = 0,        #
        
        panning:       float | int = 0,
        volume:        float | int = 1,
        interpolation: str         = "none",
        tune:          float = 440,
        coarse_tune = 0,
        ):
        super().__init__(type_="sample",
                         wavetable=sample,
                         sample_rate=sample_rate,
                         panning=panning,
                         volume=volume,
                         interpolation=interpolation,
                         tune = tune,
                         coarse_tune = coarse_tune)
        self.sample_tune   = sample_tune
        self.loop_type     = LOOP_TYPES.get(sample_loop, LOOP_NONE)
        self.loop_start    = loop_start
        self.loop_end      = loop_end
        #self.wavetable     = self.wavetable[:loop_end + 1] if loop_end and self.loop_type else self.wavetable
        #self.wavetable[-1] = self.wavetable[loop_start]
        self.wavetable     = self.wavetable[:loop_end] if loop_end and self.loop_type else self.wavetable
    def update(self, suppress_phase_update=False):
        out, phase_reset_flag = 0, False
        phase = self.phase
        WAVE_LEN = len(self.wavetable)
        Fphase = floor(phase)
        idx = Fphase % len(self.wavetable)
        loop_start = self.loop_start
        loop_end = self.loop_end
        loop_start = min(loop_start, loop_end)
        
        # print(self.loop_type)
        match self.loop_type:
            case 0:
                # print("help")
                # print(self.phase > (WAVE_LEN - 1))
                # print(self.phase, WAVE_LEN - 1)
                if phase >= (WAVE_LEN - 1):
                    self.phase = WAVE_LEN - 1
                    self._freq = 0
                    #print("end")
                phase_reset_flag = self.phase > WAVE_LEN
            case 1:
                phase_reset_flag = self.phase > self.loop_end
                if phase >= (WAVE_LEN - 1) or  phase >= self.loop_end:
                    self.phase = phase - WAVE_LEN + self.loop_start
                #print("loop lol")
            # case 2:
                # self.phase %= self.loop_end if loop_end else len(self.wavetable)
        
        # print(
        # f"idx   {idx}\n"
        # f"phase {phase}\n"
        # f"freq  {self._freq}\n"
        # )
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

        if self.i_type == INTERP_NONE:
            out = self.wavetable[idx]
        elif self.i_type == INTERP_LIN:
            out = (
                self.wavetable[idx] -
                (
                    (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (phase - Fphase)
                )
            )
        elif self.i_type == INTERP_RECTSINE:
            out = (
                self.wavetable[idx] -
                (
                    (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * sin((pi * (phase - Fphase)) / 2)
                )
            )
        elif self.i_type == INTERP_SINE:
            #print("sine")
            out = (
                self.wavetable[idx] -
                (
                    (self.wavetable[idx] - self.wavetable[(idx + 1) % WAVE_LEN]) * (sin((pi * ((phase - Fphase) * 2 - 1)) / 2) / 2 + .5)
                )
            )
        else:
            #print("else")
            out = self.wavetable[idx]
        if not suppress_phase_update:
            self.phase += self._freq
        lMult = 1 - abs(self.panning) if self.panning > 0 else 1
        rMult = 1 - abs(self.panning) if self.panning < 0 else 1
        self.last_output = out
        
        # print(
        # f"phase  {self.phase}\n"
        # f"phase2 {phase}\n"
        # f"freq   {self._freq}\n"
        # f"val    {self.wavetable[idx]}\n"
        # f"out    {out}\n"
        # )
        return (out * lMult * self.__volume__ * self.env_y, out * rMult * self.__volume__ * self.env_y, phase_reset_flag)
    def parse_key(self, key, legato=False): 
        if key == "cut":
            self.cut_channel()
        elif key == "rel":
            self.release_channel()
        elif key == "...":
            pass
        else:
            self._freq = (((freq_from_key(key + self.channel_coarse_tune, self.channel_tune) / 440) * self.sample_tune)) / self.sample_rate
            # TODO: refine
            # print(
            # f"freq   {self._freq}\n"
            # f"key    {key}\n"
            # f"freqc  {freq_from_key(key + self.channel_coarse_tune, self.channel_tune)}\n"
            # f"freq4  {freq_from_key(key + self.channel_coarse_tune, 440)}\n"
            # f"freq42 {(((freq_from_key(key + self.channel_coarse_tune, 440) / 440) * self.sample_tune)) / self.sample_rate}\n"
            # f"tune   {self.channel_tune}\n"
            # ) 
            if not legato:
                self.press_channel(1, 1)

class SampleMapChannel:
    def __init__(self,
                 wavetables:    list[list[int]]   = None, # wavetable
                 sample_rate:   int               = 44100, # default sample rate...
                 panning:       float | int = 0, #...pan...
                 volume:        float | int = 1, #...and volume.
                 # interpolation: str         = "none",
                 tune = 440,
                 coarse_tune = 0,
                 ):
        pass  # потом когда-нибудь (вероятно в ближайшие 100 лет)

if __name__ == "__main__":
    # 
    f = freq_from_key
    k = key_from_note
    o = opl_approximate_curve_2
    sr = 30000 # literally everything depends on the sample rate, including bpm since its all in a for loop
    #length = (64 * .1) * 2 #length
    length = 64 * .1 #length
    #length = (4 * .1) * 2 #length
    print("READY")
    master_tune = 450

    ChannelFeedback = OperatorChannel(
        type_ = "opl_accumulator",
        sample_rate = sr,
        interpolation = "sine", #"rectsine", #"linear",
        panning = 0,
        length = 256,
        volume = 1,
        width = .25,)
    SquarePluck = FMChannel(
        tune = master_tune,
        sample_rate = sr,
        volume = 1,
        panning = 0,
        #type_ = "sine",
        operators = 2,
        op_matrix =  [
                      [1, 1],
                      [0, 1],
                      ],
        op_mults =   [1, 1],
        op_volumes = [.25, 1],#[.2, 1],
        op_outputs = [0, 2],
        op_fb_mults = [0, 0],
        op_mod_in_mults = [0, 1],
        op_waves =   ["abs_sine", "sine"],
        op_tables =  [[0], [0]],)
    PadLeft = FMChannel(
        tune = master_tune,
        coarse_tune = 1,
        sample_rate = sr,
        volume = 1,
        panning = -1,
        #type_ = "sine",
        operators = 2,
        op_matrix =  [
                      [1, 1],
                      [0, 0],
                      ],
        op_mults =   [15, .5],  # = [15, .5]
        op_volumes = [o(63-4,63), 1],#[.2, 1],
        op_outputs = [0, 2],
        op_fb_mults = [0.03, 0],
        op_mod_in_mults = [0, 1],
        op_waves =   ["sine", "even_sine"],
        op_tables =  [[0], [0]],)
    PadRight = FMChannel(
        tune = 440,
        coarse_tune = 4,
        sample_rate = sr,
        volume = 1,
        panning = 1,
        #type_ = "sine",
        operators = 2,
        op_matrix =  [
                      [1, 1],
                      [0, 0],
                      ],
        op_mults =   [13, .5],  # = [13, .5]
        op_volumes = [o(63-4,63), 1],#[.2, 1],
        op_outputs = [0, 2],
        op_fb_mults = [0.03, 0],
        op_mod_in_mults = [0, 1],
        op_waves =   ["sine", "even_sine"],
        op_tables =  [[0], [0]],)
    
    PLUCK = open("./crystal_oscillator_pluck.raw", "rb").read()
    PLUCK2 = open("./crystal_oscillator_pluck_2.raw", "rb").read()
    PLUCKCRUSH = open("./crystal_oscillator_pluck_crush.raw", "rb").read()
    AP_YAM_NA_T_048_C_2_ = open("./AP_YAM_NA_T_048_C_2_.raw", "rb").read()
    AP_YAM_NA_T_067_G_3_ = open("./AP_YAM_NA_T_067_G_3_.raw", "rb").read()
    SampleTest1 = SampleChannel(  # TODO: refine how frequency generation works so its consistent
        sample         = list((np.array(list(AP_YAM_NA_T_067_G_3_), np.float16) - 127.5) / 127.5),
       #sample         = list(SPL),
        sample_rate    = sr,
        sample_tune    = 13468 * 2,
        sample_loop    = "forward",
        loop_start     = 22689,
        loop_end       = 33461,
        panning        = 0,
        volume         = 1,
        interpolation  = "none",
        tune           = master_tune,
        coarse_tune    = 12,)
    SampleTest2 = SampleChannel(
        sample         = list((np.array(list(PLUCKCRUSH), np.float16) - 127.5) / 127.5),
       #sample         = list(SPL),
        sample_rate    = sr,
        sample_tune    = 4842,
        sample_loop    = "forward",
        loop_start     = 491,
        loop_end       = 513,
        panning        = 0,
        volume         = 1,
        interpolation  = "none",
        tune           = master_tune,
        coarse_tune    = 12,)
    
    feedbackMult = .1 # .2

    # ChannelFeedback.set_attack(0);ChannelFeedback.set_decay1(.06);ChannelFeedback.set_sustain(.3);ChannelFeedback.set_decay2(.1);ChannelFeedback.set_release(0)
    
    # SquarePluck.set_attack(0,0)
    # SquarePluck.set_decay1(.05,.2)
    # SquarePluck.set_sustain(o(63-24,63),0)
    # SquarePluck.set_decay2(.08,0)
    # SquarePluck.set_release(0,0,)
    # PadLeft.set_attack(0,1/128)
    # PadLeft.set_decay1(-1,-1)
    # PadLeft.set_sustain(-1,-1)
    # PadLeft.set_decay2(-1,-1)
    # PadLeft.set_release(0,1/128)
    # PadRight.set_attack(0,1/128)
    # PadRight.set_decay1(-1,-1)
    # PadRight.set_sustain(-1,-1)
    # PadRight.set_decay2(-1,-1)
    # PadRight.set_release(0,1/128)
    
    SampleTest1.set_attack(0);SampleTest1.set_decay1(.05);SampleTest1.set_sustain(.4);SampleTest1.set_decay2(.1);
    SampleTest2.set_attack(0);SampleTest2.set_decay1(-1);SampleTest2.set_sustain(1);SampleTest2.set_decay2(-1);
    notes_pre = [
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "b-4", "a-4", "d-5",
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "d-5", "e-5", "b-4",
        
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "b-4", "a-4", "d-5",
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "f#4", "a-4", "d-5", "f#5", "d-5", "e-5",

        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "b-4", "a-4", "d-5",
        "e-3", "a-3", "b-3", "g-4", "g-3", "b-3", "d-4", "a-4",
        "e-3", "b-3", "a-4", "b-4", "e-4", "d-5", "e-5", "b-4",

        "a-3", "b-3", "e-4", "b-4", "a-3", "b-4", "a-4", "d-5",
        "a-3", "e-5", "b-4", "a-4", "e-4", "g-5", "f#5", "d-5",
        "a-3", "d-4", "e-4", "a-4", "a-3", "b-4", "d-5", "e-5",
        "e-4", "b-4", "a-4", "b-4", "e-4", "a-4", "f#4", "g-4",]
    notes_pads_pre = [
        "e_2", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        
        "a_3", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",
        "...", "...", "...", "...", "...", "...", "...", "...",]
    
    notes = [k(_) for _ in notes_pre]
    notes_pads = [k(_) for _ in notes_pads_pre]
    
    sample_test = [60, 48, 72, 84]
    SampleTest2.parse_key(0, 0)
    
    seq = 0
    
    render = [0 for _ in range(floor(sr*length) * 2)]
    curSample = np.array([0,0], np.float32)  # current sample
    #SampleBuffer = np.array([0,0,0], np.float32)  # current sample

    import time
    start = time.perf_counter()
    for _ in range(floor(sr*length)):
        curSample -= curSample
        if not _ % sr:
            print(f"second {1 + (_ // sr)} generated")
        if not _ % (sr//10):
        #if not _ % (sr//(5/4)):
            # SquarePluck.parse_key(notes[seq])
            # PadLeft.parse_key(notes_pads[seq])
            # PadRight.parse_key(notes_pads[seq])
            #SampleTest1.parse_key(sample_test[seq % len(sample_test)])
            SampleTest1.parse_key(notes[seq])
            #SampleTest2.parse_key(sample_test[seq % len(sample_test)])
            #SampleTest2.parse_key(notes[seq], 1)
            #SampleTest2.panning = ((_ / (sr * length)) -.5) * 2
            seq = (seq + 1) % len(notes)
        # curSample += SquarePluck.update()
        # curSample += PadLeft.update()
        # curSample += PadRight.update()
        curSample += SampleTest1.update()[:2]
        #curSample += SampleTest2.update()[:2]
        #print(f"curSample {curSample}")
        
        curSample /= 2
        render[_ * 2] += curSample[0]
        render[_ * 2 + 1] += curSample[1]
    elapsed = time.perf_counter() - start
    print(f"{elapsed:.3f}/{length}s")
    with FurWave.WaveWriter(
                    channels=2,
                    samplerate=sr,
                    bitdepth=32.,
                    data=render,
                    packed=True,
                    ) as Wave:
        Wave.write_file(f"fursound_test.wav")
        