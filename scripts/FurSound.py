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

# FURSOUND -- started on 05/09/26
# crazy how in about a week i went from a blank
# file to some fancy math that generates sounds
#                                       - Furmilion
# огибающая писалась за две минуты хуем на коленке и
# поэтому из всего говнокода она наиговнокоднейшая 

0x686f7720646f6573207468697320657665620776f726b

from funcs import clamp
from math import tau, sin, cos, floor, ceil
import FurWave  # custom wav writer; i made it because the builtin one didnt have support for chunks and now i use it because im just used to
from random import random
try:
    import numpy as np
    NUMPY = True
except ImportError:
    print("i guess we're doing some shit manually now")
    NUMPY = False

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
        # self.fm = self.sine  # fm will likely instead become alive in own Operator class
        self.xor_triangle = self.pulse
        self.xor_sine = self.sine;   self.xor_sawtooth = self.sawtooth

        # special
        self.test = self.square
        self.unimplemented = self.sine
        self.none = "none"
        self.h = "h"
        self.H = "H"
        self.ZeroDivisionError = "ZeroDivisionError"  # i dare you use it.

        # interpolation types
        self.i_none = "none"
        self.i_lin  = "linear"
        
        # common
        self.c_type = type_
        self.p_width = abs(width)
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = 44100 if not sample_rate or sample_rate < 1 else sample_rate # sample rate of the channel; also affects base sample playback freq
        
        self.adsr = [.125, 1, .5, 2, 1.2]  # Attack, Decay, Sustain, Decay 2, Release
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
        self.length = abs(length) if length else None
        self.skip_sound = False  # similar to None wave but is used when another wave is in use
        
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
                    self.wavetable = [(random() -.5) * 2 for _ in range(self.length * 2)]  # since it is stuck at 16, it might be unsuitable for
                    self.length = 16  # unique timbres like classic atari basses so you might want to opt for wavetable
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
    
    def update(self, suppress_phase_update=False, suppress_noise_update=False):
        out, phase_reset_flag = 0, False
        
        if self.c_type != self.none:
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
        if self.c_type not in [self.none, self.noise_1bit, self.noise] and not self.skip_sound:
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
        elif self.c_type == self.none or self.skip_sound:  # if we have a special "none" wave, straight up ignore the sound logic and just
            self.phase = (self.phase + (self._freq / self.sample_rate))  # update the phase; also when skipping sound, obviously
            phase_reset_flag = self.phase > 1
            self.phase %= 1 
            return (0, 0, phase_reset_flag)
            
        elif self.c_type in [self.noise_1bit, self.noise]:  # if we have either noise, then force no interpolation as i have no fucking idea how to deal with that
            out = self.wavetable[floor(self.phase * len(self.wavetable)) % len(self.wavetable)]  # and do you even really need one for noise
            
        if not suppress_phase_update:
            self.phase = (self.phase + (self._freq / self.sample_rate))
            phase_reset_flag = self.phase > 1
            if phase_reset_flag:
                if self.c_type == self.noise_1bit and not suppress_noise_update:  # generate noise packets
                    self.wavetable = [(round(random()) -.5) * 2 for _ in range(self.length * 2)]
                elif self.c_type == self.noise and not suppress_noise_update:
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
        return (out * lMult * self.volume * self.env_y, out * rMult * self.volume * self.env_y, phase_reset_flag)
    
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
    
    def release_channel(self):  # release adsr
        self.env_acc = (1 / (self.sample_rate * self.adsr[4])) * self.env_y  # same as below but lower speed for lower volumes
        self.env_state = 4
        print("key off")
    def cut_channel(self):      # what this flag does i pretty much told you already
        self.env_state = 5      # but in envelope context it is cheaper to do this as
        self.skip_sound = True  # if you change the wave, you'll have to manually change it back
        print("key cut")
    def press_channel(self, force_reset=True): # press adsr
        if force_reset:  # reset current envelope multiplier
            self.env_y = 0
        self.env_acc = ((1 / (self.sample_rate * self.adsr[0])) * (1 - self.env_y)) if self.adsr[0] > 0 else 1  # account for not fully decayed sound by lowering speed
        self.env_state = 0
        self.skip_sound = False
        print("key on")
    def set_attack(self, attack = 0):
        """
        Set attack time, in seconds
        """
        self.adsr[0] = attack
        self.__update_envelope__(self.env_state)
    def set_decay1(self, decay = 1):
        """
        Set decay 1 time, in seconds
        """
        self.adsr[1] = decay
        self.__update_envelope__(self.env_state)
    def set_sustain(self, level = 1):
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
        match state:
            case 0:
                self.skip_sound = False
                self.env_state = 0
                self.env_acc = ((1 / (self.sample_rate * self.adsr[0])) * (1 - self.env_y)) if self.adsr[0] > 0 else 1
            case 1:
                self.env_state = 1
                self.env_acc = ((1 / (self.sample_rate * self.adsr[1])) * self.env_y) if self.adsr[1] > 0 else 1
            case 2:
                if self.adsr[3] > 0:
                    self.__update_envelope__(3)
                else:
                    self.env_y = self.adsr[2]
            case 3:
                self.env_state = 3
                self.env_acc = ((1 / (self.sample_rate * self.adsr[3])) * self.env_y) if self.adsr[3] > 0 else 1
            case 4:
                self.env_state = 4
                self.env_acc = ((1 / (self.sample_rate * self.adsr[4])) * self.env_y) if self.adsr[4] > 0 else 1
            case 5:
                self.env_state = 5
                self.env_acc = 0
                self.env_y = 0
                self.skip_sound = True
                
    # TODO: redo envelope logic
    def __toggle_envelope__(self):
        if self.env_state < 6:
            self.env_state = 5 * self.env_state
            print("env pause")
        else:
            self.env_state //= 5
            print("env resume")
    def __force_advance_envelope_state__(self):
        self.__update_envelope__((self.env_state + 1) % 5)
        print(f"env state forced to {self.env_state}")
    def __force_envelope_state__(self, state):
        self.__update_envelope__(state % 5)
        print(f"env state set to {self.env_state}")
    
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
         if NUMPY:
             out = np.array([0, 0], np.float32)
             for _ in self.channels:
                out += _.update(suppress_phase_update, suppress_noise_update)[:2]
             out /= len(self.channels)
         else:
             out = [0, 0]
             for _ in self.channels:
                 out.extend([_.update(suppress_phase_update, suppress_noise_update)[:2]])
             for _ in range(len(out)//2):
                 out[0] += out[_ * 2]/len(self.channels)
                 out[1] += out[_ * 2 + 1]/len(self.channels)
             out = out[:2]
         return out
     
    def randomize_phase(self):
        for _ in self.channels:
            _.phase = random()
##############################
##############################


if __name__ == "__main__":  # main loop where i test stuff; envelopes
    sr = 44100
    length = 10#length
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
        interpolation = "none",
        length = 16,
        volume = .1 ,
        width = 0
    )
    ChannelNoise2 = Channel(
        type_ = "n1b",
        sample_rate = sr,
        interpolation = "none",
        length = 4,
        volume = .1,
        width = 0
    )
    arr = []
    ChannelNoise._freq = 64.0/2    # handpicked detune
    ChannelNoise2._freq = 65.077/2 # C-2
    ChannelNoise.set_release()
    ChannelNoise2.set_release()
    ChannelNoise.set_attack(0); ChannelNoise.set_decay1(.2); ChannelNoise.set_sustain(0); ChannelNoise.set_decay2(-1); ChannelNoise2.set_release(0)
    ChannelNoise2.set_attack(0);ChannelNoise2.set_decay1(.2);ChannelNoise2.set_sustain(0);ChannelNoise2.set_decay2(-1);ChannelNoise2.set_release(0)
    
    
    
    
    ChannelPulse._freq = 65.077
    ChannelSquare._freq = 65.077
    ChannelTooth._freq = 174.5
    
    #Supersaw = ChannelGroup(detune=120)
    #for _ in range(8):
    #    Supersaw.add_channel(length=7) # adds 8 channels
    #Supersaw.set_base_freq(65.077 * 8)
    #Supersaw.randomize_phase()
    
    import time
    start = time.perf_counter()
    for _ in range(sr*length):
        # this thing works at the peak of its performance and takes about 20 seconds to generate 20 seconds of audio on my phone
        # takes about quarter the required time on my laptop
        
        #arr.extend([Supersaw.update()[0]])
        #arr.extend([(ChannelPulse.update()[0] + ChannelNoise.update()[0])/2,(ChannelTooth.update()[0] + ChannelNoise.update()[0])/2])  # 2 channels mapped to stereo
        #arr.extend([ChannelNoise.update()[0], ChannelNoise2.update()[0]])
        #arr.extend([ChannelNoise.update()[0], ChannelNoise2.update()[0]])
        #arr.extend([ChannelNoise.update(suppress_noise_update=True)[0], ChannelSquare.update()[0]])
        arr.extend([ChannelNoise.update(suppress_noise_update=True)[0], ChannelNoise2.update(suppress_noise_update=True)[0]])
        #arr.extend([ChannelNoise.update()[0]])
        # technically with how i did the noise ingraining here, it is updated twice as quicky and is full independent stereo
        #ChannelPulse.change_width(ChannelPulse.p_width + (.125/sr) % 1) # pwm is STUPIDLY expensive to generate when using interpolation
        #print(f"pw {ChannelPulse.p_width}")
        if not _ % sr:
            print(f"second {1 + (_ // sr)} generated")
        if not _ % (sr//8):
            ChannelNoise.force_generate_new_noise_packets()
            ChannelNoise2.force_generate_new_noise_packets()
        if not _ % (sr//8):  # gate at roughly 120 beats, every 16th note
            ChannelNoise.press_channel()
            ChannelNoise2.press_channel()
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
    with FurWave.WaveWriter(channels=2,
                    samplerate=sr,
                    bitdepth=32.,
                    data=arr,
                    packed=True,
                    ) as Wave:
        Wave.write_file(f"fursound_test.wav")
        