

class Channel:
    
    # wave types
    square     = "square"; pulse    = "pulse"
    sine       = "sine";   sawtooth = "sawtooth"
    sample     = "pcm";    pcm      = sample
    noise_1bit = "n1b";    noise    = "n"
    
    # coming: more types; replaced with closest ones by sound
    fm = sine;           
    triangle = square;     xor_triangle = pulse
    xor_sine = sine;       xor_sawtooth = sawtooth
    
    # special
    test          = square
    unimplemented = sine
    
    
    
    
    def __init__(self,
    type:        str         = "square",
    width:       float | int = 0,
    wavetable:   list[int]   = None,
    sample_rate: int         = 44100,
    phase:       float | int = 0,
    panning:     float | int = 0,
    volume:      float | int = 1,
    ):
        self.c_type = type
        self.p_width = round(width, 5) # round to 5 decimal digits
        self.wavetable = wavetable if wavetable else None # set channel wavetable if one is passed; will be overwritten if not wave type
        self.sample_rate = sample_rate # sample rate of the channel; also affects base sample playback freq
        
        # special
        self.phase = 0 # will be updated when the chabnel is asked to update
                       # used to calculate next phase. basically, points at where the playhead is in the wave
        self.panning = panning # channel panning. self-explanatory; not used right now, might implement later
        self.volume = volume
        self.finish_setup() # validate some stuff so it doesnt die
    def finish_setup():
        match self.c_type:
            case square:
                self.wavetable = [0 if _ < 64 else 255 for _ in range(256)] # the most basic waveform
            case pulse:
                



if __name__ == "__main__":
    ...