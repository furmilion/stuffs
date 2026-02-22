"""
Use monospace font for proper spacing

Custom bank tool for YM2609.

YM2609 "OPNA2" is a fictional chip that sits between YM2608 OPNA and YM2610 OPNB.
In short, YM2609 has just way too many features, including:
- Arbitrary operator routing on a channel
- Custom FM waveforms
- Per-operator feedback
- Coarse Detune inherited from YM2151 OPM
- 12 "SSG2" channels
- Default OPNA drums
- 6 ADPCM-A channels sharing a 16mbyte sample ROM
- 3 ADPCM-B channels:
  - ADPCM-B 1 with 256kbyte sample ROM
  - ADPCM-B 2 and 3 each having a 16mbyte sample ROM
SSG2:
- 3 wave channels
- 16 waves:
  - 0: Square
  - 1..8: x/8 pulse wave
  - 9: Triangle
  - 10: Sawtooth
  - 11..15: user
Channel effects:
- Distortion -> (LPF -> HPF) -> Channel Compressor -> System
System effects:
- Reverb (with per-channel send and toggle)
- Chorus (with per-channel send and toggle)
- Compressor
- 3-band EQ

This tool was built by me just so I could safely close custom
Furnace fork by LTVA with YM2609 and later recreate instruments.
The custom fork in question is located on GitHub at LTVA1/Furnace/tree/YM2609/ and
furmilion/furnace-fur/tree/ym2609/ for building via GitHub actions.

Format:

 size, bytes | data | description
-------------+------+-----------------------
      4      | 2609 | format magic
      1      |      | instrument amount (0..255) + 1
      2      |      | wavetable amount  (0..32767) + 1
     16      |      | bank name
-------------+------+-----------------------
      4      | INST | instrument block
  2Ah each   |      | instrument block data
-------------+------+-----------------------
      2      | WAVE | wavetable block
      2      |      | wavetable size (0..1023) + 1
   1..3FFh   |      | wavetable samples


Instrument block format:
 Byte |     Bits      | Description
------+---------------+---------------------------------------------------------------------------
    0 |   _111 _222   | OP1/2 FB
    1 |   _333 _444   | OP3/4 FB
    2 |  11 22 33 44  | OP1/2/3/4 Coarse Detune
    3 |  11 22 33 44  | OP1/2/3/4 Envelope Scale              +----+----+----+---+---+---+---+---+
    4 | A1 111 A2 222 | OP1/2 (A)M toggle / OP1/2 Detune      | -3 | -2 | -1 | 0 | 1 | 2 | 3 | 4 |
    5 | A3 333 A4 444 | OP3/4 (A)M toggle / OP3/4 Detune      |  7 |  6 |  5 | 0 | 1 | 2 | 3 | 4 |
    6 |   1111 2222   | OP1/2 Multiplier                      +----+----+----+---+---+---+---+---+
    7 |   3333 4444   | OP3/4 Multiplier
    8 |   C1 1111111  | OP1 (C)ustom wave toggle / High 7 bits of wave index
    9 |    11111111   | Low 8 bits of wave index
    A |   C2 2222222  | OP2 (C)ustom wave toggle / High 7 bits of wave index
    B |    22222222   | Low 8 bits of wave index
    C |   C3 3333333  | OP3 (C)ustom wave toggle / High 7 bits of wave index
    D |    33333333   | Low 8 bits of wave index
    E |   C4 4444444  | OP4 (C)ustom wave toggle / High 7 bits of wave index
    F |    44444444   | Low 8 bits of wave index
   10 |  M1111 M2222  | OP1/2 modulated by: OP1/2/3/4
   11 |  M3333 M4444  | OP4/3 modulated by: OP1/2/3/4
   12 |  __ C ALG LF  | (C)ustom algorithm toggle / (ALG)orithm | (LF)o to Amp control
   13 |  1234 E BLK   | OP1/2/3/4 Phase reset / Fixed octave (E)nable / Fixed octave
   14 |   _LFO 1234   | (LFO) to freq control / OP1/2/3/4 SSG-EG Enable
   15 |   _111 _222   | OP1/2 SSG-EG Shape
   16 |   _333 _444   | OP3/4 SSG-EG Shape
   17 |   E 1111111   | OP1 (E)nable / OP1 TL
   18 |   E 2222222   | OP2 (E)nable / OP2 TL
   19 |   E 3333333   | OP3 (E)nable / OP3 TL
   1A |   E 4444444   | OP4 (E)nable / OP4 TL
   1B |   ___ ATTK1   | OP1 Attack Rate
   1C |   ___ DEC11   | OP1 Decay 1 Rate
   1D |   ___ DEC21   | OP1 Decay 2 Rate
   1E |   SUS1 REL1   | OP1 Sustain Level / Release Rate
   1F |   ___ ATTK2   | OP2 Attack Rate
   20 |   ___ DEC12   | OP2 Decay 1 Rate
   21 |   ___ DEC22   | OP2 Decay 2 Rate
   22 |   SUS2 REL2   | OP1 Sustain Level / Release Rate
   23 |   ___ ATTK3   | OP3 Attack Rate
   24 |   ___ DEC13   | OP3 Decay 1 Rate
   25 |   ___ DEC23   | OP3 Decay 2 Rate
   26 |   SUS3 REL3   | OP3 Sustain Level / Release Rate
   27 |   ___ ATTK4   | OP4 Attack Rate
   28 |   ___ DEC14   | OP4 Decay 1 Rate
   29 |   ___ DEC24   | OP4 Decay 2 Rate
   2A |   SUS4 REL4   | OP4 Sustain Level / Release Rate
   2B |    NNNNNNNN   | Instrument name
   2C |    NNNNNNNN   | Instrument name
   2D |    NNNNNNNN   | Instrument name
   2E |    NNNNNNNN   | Instrument name
   2F |    NNNNNNNN   | Instrument name
   30 |    NNNNNNNN   | Instrument name
   31 |    NNNNNNNN   | Instrument name
   32 |    NNNNNNNN   | Instrument name
   33 |    NNNNNNNN   | Instrument name
   34 |    NNNNNNNN   | Instrument name
   35 |    NNNNNNNN   | Instrument name
   36 |    NNNNNNNN   | Instrument name
   37 |    NNNNNNNN   | Instrument name
   38 |    NNNNNNNN   | Instrument name
   39 |    NNNNNNNN   | Instrument name
   3A |    NNNNNNNN   | Instrument name
   3B |    NNNNNNNN   | Instrument name
   3C |    NNNNNNNN   | Instrument name
   3D |    NNNNNNNN   | Instrument name
   3E |    NNNNNNNN   | Instrument name
   3F |    NNNNNNNN   | Instrument name
------+---------------+---------------------------------------------------------------------------

Wavetable block format:
------+------------------+-------------+
 Byte |       Bits       | Description |
  ??  | ____SSSSSSSSSSSS | Sample      |
------+------------------+-------------+




Current status:

  Bank saving:
  - Works(?)
  Bank loading:
  - Broken at ~20 instruments/waves

  Instrument saving:
  - Works
  Instrument loading:
  - Works
"""
from funcs import _ as no
no = no()
from funcs import clamp
import zlib

def explode_16bits(val):
    # always big endian.
    return [(val >> 8) & 0xFF, val & 0xFF]

class BankTool:
    """
    class for managing ym2609 instrument banks.

    does not provide a direct interface to alter instruments,
    use get_instrument() to get an instrument and modify it and modify_instrument() to replace it in the bank,
    ditto for waves.
    """
    class InstrumentError(Exception):
        pass
    class WaveError(Exception):
        pass
    class YM2609Instrument:
        """
        the instrument class
        """
        def __init__(this):
            this.mod_matrices = [  # mod matrices for opn algorithms
                [  # algorithm 0
                    [0, 0, 0, 0],  # OP1
                    [1, 0, 0, 0],  # OP2
                    [0, 1, 0, 0],  # OP3
                    [0, 0, 1, 0],  # OP4
                    # OP1 -> OP2 -> OP3 -> OP4
                ],
                [  # algoritm 1
                    [0, 0, 0, 0],  # OP1
                    [0, 0, 0, 0],  # OP2
                    [1, 1, 0, 0],  # OP3
                    [0, 0, 1, 0],  # OP4
                    # (OP1 + OP2) -> OP3 -> OP4
                ],
                [  # algorithm 2
                    [0, 0, 0, 0],  # OP1
                    [0, 0, 0, 0],  # OP2
                    [0, 1, 0, 0],  # OP3
                    [1, 0, 1, 0],  # OP4
                    # (OP1 + (OP2 -> OP3)) -> OP4
                ],
                [  # algorithm 3; mirrored version of alg2
                    [0, 0, 0, 0],  # OP1
                    [1, 0, 0, 0],  # OP2
                    [0, 0, 0, 0],  # OP3
                    [0, 1, 1, 0],  # OP4
                    # ((OP1 -> OP2) + OP3) -> OP4
                ],
                [  # algorithm 4
                    [0, 0, 0, 0],  # OP1
                    [1, 0, 0, 0],  # OP2
                    [0, 0, 0, 0],  # OP3
                    [0, 0, 1, 0],  # OP4
                    # (OP1 -> OP2) + (OP3 -> OP4)
                ],
                [  # algorithm 5
                    [0, 0, 0, 0],  # OP1
                    [1, 0, 0, 0],  # OP2
                    [1, 0, 0, 0],  # OP3
                    [1, 0, 0, 0],  # OP4
                    # OP1 modulates every other OP
                ],
                [  # algorithm 6
                    [0, 0, 0, 0],  # OP1
                    [1, 0, 0, 0],  # OP2
                    [0, 0, 0, 0],  # OP3
                    [0, 0, 0, 0],  # OP4
                    # (OP1 -> OP2) + OP3 + OP4
                ],
                [  # algorithm 7
                    [0, 0, 0, 0],  # OP1
                    [0, 0, 0, 0],  # OP2
                    [0, 0, 0, 0],  # OP3
                    [0, 0, 0, 0],  # OP4
                    # every operator outputs independently
                ]
            ]
            this.detune_lookup = {-3: 7, -2: 6, -1: 5,  # lookup for detune signed and unsigned values
                                  0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
            this.name = ''
            this.set_name('NEW INSTRUMENT')

            # booleans
            this.lfo_pitch = 0                 # LFO -> Pitch, applies to the entire channel
            this.lfo_am    = 0                 # LFO -> AM, applies to the entire channel but has per-op toggle
            this.AM        = [0, 0, 0, 0]      # operators' AM toggles
            this.PR        = [0, 0, 0, 0]      # operators' phase reset toggles
            this.op_enable = [0, 0, 0, 0]      # operators' enable toggles

            # the rest
            this.feedback  = [0, 0, 0, 0]      # operators' feedback levels, 0..7
            this.detune1   = [0, 0, 0, 0]      # operators' detune 1
            this.detune2   = [0, 0, 0, 0]      # operators' detune 2
            this.tl        = [0, 0, 0, 0]      # TL attenuation level
            this.egs       = [0, 0, 0, 0]      # operators' EG scalings
            this.mults     = [0, 0, 0, 0]      # operators' multipliers
            this.op_waves  = [-1, -1, -1, -1]  # operators' custom wave indices, -1 for no custom wave
            this.block     = -1                # fixed block. -1 for auto. caps at 7
            this.c_algo    = 0                 # algorithm. > 7 for custom
            this.ssg_eg    = [-1, -1, -1, -1]  # SSG-EG shape. -1 for disable
            this.attack    = [31, 31, 31, 31]  # operators' attack rates
            this.decay1    = [0, 0, 0, 0]      # operators' attack decay 1 rates
            this.sustain   = [15, 15, 15, 15]  # operators' sustain attenuation levels
            this.decay2    = [0, 0, 0, 0]      # operators' attack decay 2 rates
            this.release   = [15, 15, 15, 15]  # operators' release rates

            # custom algorithm
            this.mod_op1   = [0, 0, 0, 0]  # OP1 modulated by: Self, OP2, OP3, OP4
            this.mod_op2   = [1, 0, 0, 0]   # OP2 modulated by: OP1, Self, OP3, OP4
            this.mod_op3   = [0, 1, 0, 0]   # OP3 modulated by: OP1, OP2, Self, OP4
            this.mod_op4   = [0, 0, 1, 0]   # OP4 modulated by: OP1, OP2, OP3, Self

            # constructed data
            this.constructed = this.construct_instrument()

        # set globals
        def set_name(this, name):
            while len(name) < 0x16:
                name += ' '
            this.name = name[:0x16]
        def set_lfo_pitch(this, strength):
            this.lfo_pitch = clamp(strength, 0, 7)
        def set_lfo_am(this, strength):
            this.lfo_am = clamp(strength, 0, 3)
        def set_fixed_block(this, block = None):
            if not block:
                block = -1
                return
            this.block = clamp(block, -1, 7)
        def set_algorithm(this, algo):
            this.c_algo = clamp(algo, 0, 8)
            if algo < 8:
                this.mod_op1 = this.mod_matrices[algo][0]
                this.mod_op2 = this.mod_matrices[algo][1]
                this.mod_op3 = this.mod_matrices[algo][2]
                this.mod_op4 = this.mod_matrices[algo][3]
        def set_matrix_op1(this, matrix):
            this.mod_op1 = matrix
        def set_matrix_op2(this, matrix):
            this.mod_op2 = matrix
        def set_matrix_op3(this, matrix):
            this.mod_op3 = matrix
        def set_matrix_op4(this, matrix):
            this.mod_op4 = matrix

        # set operators
        def set_feedback(this, op = 0, feedback = 0):
            this.feedback[clamp(op, 0, 3)] = clamp(feedback, 0, 7)
        def set_attack(this, op, val):
            this.attack[clamp(op, 0, 3)] = clamp(val, 0, 31)
        def set_decay1(this, op, val):
            this.decay1[clamp(op, 0, 3)] = clamp(val, 0, 31)
        def set_sustain(this, op, val):
            this.sustain[clamp(op, 0, 3)] = clamp(val, 0, 15)
        def set_decay2(this, op, val):
            this.decay2[clamp(op, 0, 3)] = clamp(val, 0, 31)
        def set_release(this, op, val):
            this.release[clamp(op, 0, 3)] = clamp(val, 0, 15)
        def set_ssgeg(this, op, shape):
            this.op_waves[clamp(op, 0, 3)] = clamp(shape, -1, 7)
        def set_op_wave(this, op, wave):
            this.op_waves[clamp(op, 0, 3)] = clamp(wave, -1, 32767)
        def set_tl(this, op = 0, tl = 0):
            this.tl[clamp(op, 0, 3)] = clamp(tl, 0, 127)
        def set_egs(this, op, scale):
            this.egs[clamp(op, 0, 3)] = clamp(scale, 0, 3)
        def set_op_mult(this, op, mult):
            this.mults[clamp(op, 0, 3)] = clamp(mult, 0, 15)
        def set_detunes(this, op = 0, dt1 = 0, dt2 = 0):
            dt1 = this.detune_lookup[clamp(dt1, -3, 7)]
            this.detune1[clamp(op, 0, 3)] = dt1
            this.detune2[clamp(op, 0, 3)] = clamp(dt2, 0, 3)
        def set_op_enable(this, op, status):
            this.op_enable[clamp(op, 0, 3)] = clamp(status, 0, 1)
        def set_op_am(this, op, status):
            this.AM[clamp(op, 0, 3)] = clamp(status, 0, 1)
        def set_op_pr(this, op, status):
            this.PR[clamp(op, 0, 3)] = clamp(status, 0, 1)

        # get globals
        def get_name(this):
            return this.name
        def get_algorithm(this):
            matrices = this.mod_matrices
            matrices.append([
                this.mod_op1,
                this.mod_op2,
                this.mod_op3,
                this.mod_op4,
            ])
            alg = clamp(this.c_algo, 0, 8)
            # printable =\
            #     (   # maybe ill use this elsewhere
            #         f"     | OP1 | OP2 | OP3 | OP4 |"
            #         f"-----+-----+-----+-----+-----+"
            #         f" OP1 |  {'T' if matrices[alg][0][0] else ' '}  |  {'T' if matrices[alg][0][1] else ' '}  |  {'T' if matrices[alg][0][2] else ' '}  |  {'T' if matrices[alg][0][3] else ' '}  |"
            #         f"-----+-----+-----+-----+-----+"
            #         f" OP2 |  {'T' if matrices[alg][1][0] else ' '}  |  {'T' if matrices[alg][1][1] else ' '}  |  {'T' if matrices[alg][1][2] else ' '}  |  {'T' if matrices[alg][1][3] else ' '}  |"
            #         f"-----+-----+-----+-----+-----+"
            #         f" OP3 |  {'T' if matrices[alg][2][0] else ' '}  |  {'T' if matrices[alg][2][1] else ' '}  |  {'T' if matrices[alg][2][2] else ' '}  |  {'T' if matrices[alg][2][3] else ' '}  |"
            #         f"-----+-----+-----+-----+-----+"
            #         f" OP4 |  {'T' if matrices[alg][3][0] else ' '}  |  {'T' if matrices[alg][3][1] else ' '}  |  {'T' if matrices[alg][3][2] else ' '}  |  {'T' if matrices[alg][3][3] else ' '}  |"
            #         f"-----+-----+-----+-----+-----+"
            #     )
            return matrices[alg] if this.c_algo > 7 else this.c_algo
        def get_fixed_block(this):
            return this.block
        def get_lfo_pitch(this):
            return this.lfo_pitch
        def get_lfo_am(this):
            return this.lfo_am
        # get operators
        def get_feedback(this, op):
            return this.feedback[clamp(op, 0, 3)]
        def get_attack(this, op):
            return this.attack[clamp(op, 0, 3)]
        def get_decay1(this, op):
            return this.decay1[clamp(op, 0, 3)]
        def get_sustain(this, op):
            return this.sustain[clamp(op, 0, 3)]
        def get_decay2(this, op):
            return this.decay2[clamp(op, 0, 3)]
        def get_release(this, op):
            return this.release[clamp(op, 0, 3)]
        def get_ssgeg(this, op):
            return this.ssg_eg[clamp(op, 0, 3)]
        def get_wave_id(this, op):
            return this.op_waves[clamp(op, 0, 3)]
        def get_tl(this, op):
            return this.tl[clamp(op, 0, 3)]
        def get_egs(this, op):
            return this.egs[clamp(op, 0, 3)]
        def get_mult(this, op):
            return this.mults[clamp(op, 0, 3)]
        def get_detunes(this, op):
            return this.detune1[clamp(op, 0, 3)], this.detune2[clamp(op, 0, 3)]
        def get_op_enable(this, op):
            return this.op_enable[clamp(op, 0, 3)]
        def get_op_am(this, op):
            return this.AM[clamp(op, 0, 3)]
        def get_op_pr(this, op):
            return this.PR[clamp(op, 0, 3)]

        # very epic: constructor and deconstructor
        def construct_instrument(this):
            name = bytes(this.name, 'utf8')
            this.constructed = [
                (this.feedback[0] << 4) | (this.feedback[1]), # feedback op1/2
                (this.feedback[2] << 4) | (this.feedback[3]), # feedback op3/4

                (this.detune2[0] << 6) | (this.detune2[1] << 4) | (this.detune2[2] << 2) | (this.detune2[3] << 0), # coarse detunes

                (this.egs[0] << 6) | (this.egs[1] << 4) | (this.egs[2] << 2) | (this.egs[3] << 0), # egs

                (this.AM[0] << 7) | (this.detune1[0] << 4) | (this.AM[1] << 3) | (this.detune1[1] << 0), # detune/am op1/2
                (this.AM[2] << 7) | (this.detune1[2] << 4) | (this.AM[3] << 3) | (this.detune1[3] << 0), # detune/am op3/4

                (this.mults[0] << 4) | (this.mults[1] << 0), # mults
                (this.mults[2] << 4) | (this.mults[3] << 0), # mults

                ((1 << 7) if this.op_waves[0] >= 0 else (0 << 7)) | (((this.op_waves[0] >> 8) & 0b1111111) if this.op_waves[0] >= 0 else 0), # wave op1
                (this.op_waves[0] & 0xFF) if this.op_waves[0] >= 0 else 0,
                ((1 << 7) if this.op_waves[1] >= 0 else (0 << 7)) | (((this.op_waves[1] >> 8) & 0b1111111) if this.op_waves[1] >= 0 else 0), # wave op2
                (this.op_waves[1] & 0xFF) if this.op_waves[1] >= 0 else 0,
                ((1 << 7) if this.op_waves[2] >= 0 else (0 << 7)) | (((this.op_waves[2] >> 8) & 0b1111111) if this.op_waves[2] >= 0 else 0), # wave op3
                (this.op_waves[2] & 0xFF) if this.op_waves[2] >= 0 else 0,
                ((1 << 7) if this.op_waves[3] >= 0 else (0 << 7)) | (((this.op_waves[3] >> 8) & 0b1111111) if this.op_waves[3] >= 0 else 0), # wave op4
                (this.op_waves[3] & 0xFF) if this.op_waves[3] >= 0 else 0,

                (this.mod_op1[0] << 7) | (this.mod_op1[1] << 6) | (this.mod_op1[2] << 5) | (this.mod_op1[3] << 4) | (this.mod_op2[0] << 3) | (this.mod_op2[1] << 2) | (this.mod_op2[2] << 1) | (this.mod_op2[3] << 0), # op1/2 mod
                (this.mod_op3[0] << 7) | (this.mod_op3[1] << 6) | (this.mod_op3[2] << 5) | (this.mod_op3[3] << 4) | (this.mod_op4[0] << 3) | (this.mod_op4[1] << 2) | (this.mod_op4[2] << 1) | (this.mod_op4[3] << 0), # op3/4 mod
                ((1 << 5) if this.c_algo > 7 else (0 << 5)) | ((this.c_algo << 3) if this.c_algo < 8 else (0 << 3)) | (this.lfo_am & 4), # alg & lfo
                (this.PR[0] << 7) | (this.PR[1] << 6) | (this.PR[2] << 5) | (this.PR[3] << 4) | ((1 << 3) if this.block >= 0 else (0 << 3)) | (this.block if this.block >= 0 else 0), # phase reset and block
                (this.lfo_pitch << 4) | ((1 << 3) if this.ssg_eg[0] >= 0 else (0 << 3)) | ((1 << 2) if this.ssg_eg[1] >= 0 else (0 << 2)) | ((1 << 1) if this.ssg_eg[2] >= 0 else (0 << 1)) | ((1 << 0) if this.ssg_eg[3] >= 0 else (0 << 0)),

                ((this.ssg_eg[0] << 4) if this.ssg_eg[0] >= 0 else 0) | ((this.ssg_eg[1] << 0) if this.ssg_eg[1] >= 0 else 0),
                ((this.ssg_eg[2] << 4) if this.ssg_eg[2] >= 0 else 0) | ((this.ssg_eg[3] << 0) if this.ssg_eg[3] >= 0 else 0),

                (this.op_enable[0] << 7) | this.tl[0], # op1 tl&enable
                (this.op_enable[1] << 7) | this.tl[1], # op2 tl&enable
                (this.op_enable[2] << 7) | this.tl[2], # op3 tl&enable
                (this.op_enable[3] << 7) | this.tl[3], # op4 tl&enable

                # la anvalope
                this.attack[0],
                this.decay1[0],
                this.decay2[0],
                (this.sustain[0] << 4) | this.release[0],

                this.attack[1],
                this.decay1[1],
                this.decay2[1],
                (this.sustain[1] << 4) | this.release[1],

                this.attack[2],
                this.decay1[2],
                this.decay2[2],
                (this.sustain[2] << 4) | this.release[2],

                this.attack[3],
                this.decay1[3],
                this.decay2[3],
                (this.sustain[3] << 4) | this.release[3],

                # THE NAME
                name[0x00],
                name[0x01],
                name[0x02],
                name[0x03],
                name[0x04],
                name[0x05],
                name[0x06],
                name[0x07],
                name[0x08],
                name[0x09],
                name[0x0A],
                name[0x0B],
                name[0x0C],
                name[0x0D],
                name[0x0E],
                name[0x0F],
                name[0x10],
                name[0x11],
                name[0x12],
                name[0x13],
                name[0x14],
                name[0x15],
            ]
            return this.constructed
        def deconstruct_instrument(this, data):
            this.feedback[0] = data[0] >> 4      # load feedbacks
            this.feedback[1] = data[0] & 0b1111
            this.feedback[2] = data[1] >> 4
            this.feedback[3] = data[1] & 0b1111

            this.detune2[0] = (data[2] >> 6) & 4  # load coarse detune
            this.detune2[1] = (data[2] >> 4) & 4
            this.detune2[2] = (data[2] >> 2) & 4
            this.detune2[3] = (data[2] >> 0) & 4

            this.egs[0] = (data[3] >> 6) & 4  # load envelope scale
            this.egs[1] = (data[3] >> 4) & 4
            this.egs[2] = (data[3] >> 2) & 4
            this.egs[3] = (data[3] >> 0) & 4

            this.AM[0] = (data[4] >> 7)               # load operator am enable and fidetune
            this.detune1[0] = (data[4] >> 4) & 0b111
            this.AM[1] = (data[4] >> 3)
            this.detune1[1] = (data[4] >> 0) & 0b111
            this.AM[2] = (data[5] >> 7)
            this.detune1[2] = (data[5] >> 4) & 0b111
            this.AM[3] = (data[5] >> 0)
            this.detune1[3] = (data[5] >> 3) & 0b111

            this.mults[0] = (data[6] >> 4) & 0b1111  # multipliers are those
            this.mults[1] = (data[6] >> 0) & 0b1111
            this.mults[2] = (data[7] >> 4) & 0b1111
            this.mults[3] = (data[7] >> 0) & 0b1111

            this.op_waves[0] = (((data[8] & 0b1111111) << 7) | data[9]) if (data[8] >> 7) else -1     # custom waves
            this.op_waves[1] = (((data[10] & 0b1111111) << 7) | data[11]) if (data[10] >> 7) else -1
            this.op_waves[2] = (((data[12] & 0b1111111) << 7) | data[13]) if (data[12] >> 7) else -1
            this.op_waves[3] = (((data[14] & 0b1111111) << 7) | data[15]) if (data[14] >> 7) else -1

            this.mod_op1 = [(data[16] >> 7) & 1, (data[16] >> 6) & 1, (data[16] >> 5) & 1, (data[16] >> 4) & 1]  # modulation matrix
            this.mod_op2 = [(data[16] >> 3) & 1, (data[16] >> 2) & 1, (data[16] >> 1) & 1, (data[16] >> 0) & 1]
            this.mod_op3 = [(data[17] >> 7) & 1, (data[17] >> 6) & 1, (data[17] >> 5) & 1, (data[17] >> 4) & 1]
            this.mod_op4 = [(data[17] >> 3) & 1, (data[17] >> 2) & 1, (data[17] >> 1) & 1, (data[17] >> 0) & 1]

            this.block = (data[18] & 0b111) if (data[18] >> 3) & 1 else -1  # patch fixed block

            this.PR[0] = (data[18] >> 7) & 1  # operator phase reset status
            this.PR[1] = (data[18] >> 6) & 1
            this.PR[2] = (data[18] >> 5) & 1
            this.PR[3] = (data[18] >> 4) & 1

            this.c_algo = data[19] >> 2  # algorithm

            this.lfo_am = data[19] & 0b11   # lfo
            this.lfo_pitch = data[20] >> 4

            this.ssg_eg[0] = ((data[21] >> 4) & 0b111) if (data[20] >> 3) & 1 else -1
            this.ssg_eg[1] = ((data[21] >> 0) & 0b111) if (data[20] >> 2) & 1 else -1
            this.ssg_eg[2] = ((data[22] >> 4) & 0b111) if (data[20] >> 1) & 1 else -1
            this.ssg_eg[3] = ((data[22] >> 0) & 0b111) if (data[20] >> 0) & 1 else -1

            this.op_enable[0] = data[23] >> 7
            this.tl[0] = data[23] & 127
            this.op_enable[0] = data[24] >> 7
            this.tl[1] = data[24] & 127
            this.op_enable[1] = data[25] >> 7
            this.tl[2] = data[25] & 127
            this.op_enable[2] = data[26] >> 7
            this.tl[3] = data[26] & 127
            this.attack[0] = data[27]
            this.decay1[0] = data[28]
            this.decay2[0] = data[29]
            this.sustain[0] = data[30] >> 4
            this.release[0] = data[30] & 0b1111
            this.attack[1] = data[31]
            this.decay1[1] = data[32]
            this.decay2[1] = data[33]
            this.sustain[1] = data[34] >> 4
            this.release[1] = data[34] & 0b1111
            this.attack[2] = data[35]
            this.decay1[2] = data[36]
            this.decay2[2] = data[37]
            this.sustain[2] = data[38] >> 4
            this.release[2] = data[38] & 0b1111
            this.attack[3] = data[39]
            this.decay1[3] = data[40]
            this.decay2[3] = data[41]
            this.sustain[3] = data[42] >> 4
            this.release[3] = data[42] & 0b1111
            name = ''
            for i in range(22):
                name += chr(data[43 + i])
            this.name = name

        # debug
        def print_instrument(this):
            print(
                f"======== GLOBAL ========\n"
                f"Name:         {this.name}\n"
                f"Algorithm:    {this.c_algo if this.c_algo < 8 else 'custom'}\n"
                f"Mod matrix:\n"
                f"   OP1 {this.mod_op1}\n"
                f"   OP2 {this.mod_op2}\n"
                f"   OP3 {this.mod_op3}\n"
                f"   OP4 {this.mod_op4}\n"
                f"Fixed block:  {this.block if this.block >= 0 else None}\n"
                f"LFO to Pitch: {this.lfo_pitch}\n"
                f"LFO to AM:    {this.lfo_am}\n"
                f"===== PER-OPERATOR =====\n"
                f"OP1:\n"
                f"   Feedback:           {this.feedback[0]}\n"
                f"   Attack:             {this.attack[0]}\n"
                f"   Decay 1:            {this.decay1[0]}\n"
                f"   Sustain:            {this.sustain[0]}\n"
                f"   Decay 2:            {this.decay2[0]}\n"
                f"   Release:            {this.release[0]}\n"
                f"   Envelope Ecale:     {this.egs[0]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[0] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[0] == -1 else this.ssg_eg[0]}\n"
                f"   Wave:               {'Sine' if this.op_waves[0] == -1 else f'custom, {this.op_waves[0]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[0]}\n"
                f"   Total Level:        {this.tl[0]}\n"
                f"   Multiplier:         {this.mults[0]}\n"
                f"   Detune 1 (Fine):    {this.detune1[0]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[0]}\n"
                f"   Phase Reset on KON: {this.PR[0]}\n"
                f"   Operator AM:        {this.AM[0]}\n"
                
                f"OP2:\n"
                f"   Feedback:           {this.feedback[1]}\n"
                f"   Attack:             {this.attack[1]}\n"
                f"   Decay 1:            {this.decay1[1]}\n"
                f"   Sustain:            {this.sustain[1]}\n"
                f"   Decay 2:            {this.decay2[1]}\n"
                f"   Release:            {this.release[1]}\n"
                f"   Envelope Ecale:     {this.egs[1]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[1] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[1] == -1 else this.ssg_eg[1]}\n"
                f"   Wave:               {'Sine' if this.op_waves[1] == -1 else f'custom, {this.op_waves[1]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[1]}\n"
                f"   Total Level:        {this.tl[1]}\n"
                f"   Multiplier:         {this.mults[1]}\n"
                f"   Detune 1 (Fine):    {this.detune1[1]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[1]}\n"
                f"   Phase Reset on KON: {this.PR[1]}\n"
                f"   Operator AM:        {this.AM[1]}\n"
                
                f"OP3:\n"
                f"   Feedback:           {this.feedback[2]}\n"
                f"   Attack:             {this.attack[2]}\n"
                f"   Decay 1:            {this.decay1[2]}\n"
                f"   Sustain:            {this.sustain[2]}\n"
                f"   Decay 2:            {this.decay2[2]}\n"
                f"   Release:            {this.release[2]}\n"
                f"   Envelope Ecale:     {this.egs[2]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[2] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[2] == -1 else this.ssg_eg[2]}\n"
                f"   Wave:               {'Sine' if this.op_waves[2] == -1 else f'custom, {this.op_waves[2]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[2]}\n"
                f"   Total Level:        {this.tl[2]}\n"
                f"   Multiplier:         {this.mults[2]}\n"
                f"   Detune 1 (Fine):    {this.detune1[2]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[2]}\n"
                f"   Phase Reset on KON: {this.PR[2]}\n"
                f"   Operator AM:        {this.AM[2]}\n"
                
                f"OP4:\n"
                f"   Feedback:           {this.feedback[3]}\n"
                f"   Attack:             {this.attack[3]}\n"
                f"   Decay 1:            {this.decay1[3]}\n"
                f"   Sustain:            {this.sustain[3]}\n"
                f"   Decay 2:            {this.decay2[3]}\n"
                f"   Release:            {this.release[3]}\n"
                f"   Envelope Ecale:     {this.egs[3]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[3] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[3] == -1 else this.ssg_eg[3]}\n"
                f"   Wave:               {'Sine' if this.op_waves[3] == -1 else f'custom, {this.op_waves[3]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[3]}\n"
                f"   Total Level:        {this.tl[3]}\n"
                f"   Multiplier:         {this.mults[3]}\n"
                f"   Detune 1 (Fine):    {this.detune1[3]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[3]}\n"
                f"   Phase Reset on KON: {this.PR[3]}\n"
                f"   Operator AM:        {this.AM[3]}\n"
            )
        def get_instrument(this):
            return (
                f"======== GLOBAL ========\n"
                f"Name:         {this.name}\n"
                f"Algorithm:    {this.c_algo if this.c_algo < 8 else 'custom'}\n"
                f"Mod matrix:\n"
                f"   OP1 {this.mod_op1}\n"
                f"   OP2 {this.mod_op2}\n"
                f"   OP3 {this.mod_op3}\n"
                f"   OP4 {this.mod_op4}\n"
                f"Fixed block:  {this.block if this.block >= 0 else None}\n"
                f"LFO to Pitch: {this.lfo_pitch}\n"
                f"LFO to AM:    {this.lfo_am}\n"
                f"===== PER-OPERATOR =====\n"
                f"OP1:\n"
                f"   Feedback:           {this.feedback[0]}\n"
                f"   Attack:             {this.attack[0]}\n"
                f"   Decay 1:            {this.decay1[0]}\n"
                f"   Sustain:            {this.sustain[0]}\n"
                f"   Decay 2:            {this.decay2[0]}\n"
                f"   Release:            {this.release[0]}\n"
                f"   Envelope Ecale:     {this.egs[0]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[0] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[0] == -1 else this.ssg_eg[0]}\n"
                f"   Wave:               {'Sine' if this.op_waves[0] == -1 else f'custom, {this.op_waves[0]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[0]}\n"
                f"   Total Level:        {this.tl[0]}\n"
                f"   Multiplier:         {this.mults[0]}\n"
                f"   Detune 1 (Fine):    {this.detune1[0]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[0]}\n"
                f"   Phase Reset on KON: {this.PR[0]}\n"
                f"   Operator AM:        {this.AM[0]}\n"
                
                f"OP2:\n"
                f"   Feedback:           {this.feedback[1]}\n"
                f"   Attack:             {this.attack[1]}\n"
                f"   Decay 1:            {this.decay1[1]}\n"
                f"   Sustain:            {this.sustain[1]}\n"
                f"   Decay 2:            {this.decay2[1]}\n"
                f"   Release:            {this.release[1]}\n"
                f"   Envelope Ecale:     {this.egs[1]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[1] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[1] == -1 else this.ssg_eg[1]}\n"
                f"   Wave:               {'Sine' if this.op_waves[1] == -1 else f'custom, {this.op_waves[1]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[1]}\n"
                f"   Total Level:        {this.tl[1]}\n"
                f"   Multiplier:         {this.mults[1]}\n"
                f"   Detune 1 (Fine):    {this.detune1[1]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[1]}\n"
                f"   Phase Reset on KON: {this.PR[1]}\n"
                f"   Operator AM:        {this.AM[1]}\n"
                
                f"OP3:\n"
                f"   Feedback:           {this.feedback[2]}\n"
                f"   Attack:             {this.attack[2]}\n"
                f"   Decay 1:            {this.decay1[2]}\n"
                f"   Sustain:            {this.sustain[2]}\n"
                f"   Decay 2:            {this.decay2[2]}\n"
                f"   Release:            {this.release[2]}\n"
                f"   Envelope Ecale:     {this.egs[2]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[2] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[2] == -1 else this.ssg_eg[2]}\n"
                f"   Wave:               {'Sine' if this.op_waves[2] == -1 else f'custom, {this.op_waves[2]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[2]}\n"
                f"   Total Level:        {this.tl[2]}\n"
                f"   Multiplier:         {this.mults[2]}\n"
                f"   Detune 1 (Fine):    {this.detune1[2]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[2]}\n"
                f"   Phase Reset on KON: {this.PR[2]}\n"
                f"   Operator AM:        {this.AM[2]}\n"
                
                f"OP4:\n"
                f"   Feedback:           {this.feedback[3]}\n"
                f"   Attack:             {this.attack[3]}\n"
                f"   Decay 1:            {this.decay1[3]}\n"
                f"   Sustain:            {this.sustain[3]}\n"
                f"   Decay 2:            {this.decay2[3]}\n"
                f"   Release:            {this.release[3]}\n"
                f"   Envelope Ecale:     {this.egs[3]}\n"
                f"   SSG-EG Enabled:     {'Yes' if this.ssg_eg[3] >= 0 else 'No'}\n"
                f"   SSG-EG Shape:       {'Disabled' if this.ssg_eg[3] == -1 else this.ssg_eg[3]}\n"
                f"   Wave:               {'Sine' if this.op_waves[3] == -1 else f'custom, {this.op_waves[3]}'}\n"  # lmao nesting f-strings
                f"   Enabled:            {this.op_enable[3]}\n"
                f"   Total Level:        {this.tl[3]}\n"
                f"   Multiplier:         {this.mults[3]}\n"
                f"   Detune 1 (Fine):    {this.detune1[3]}\n"
                f"   Detune 2 (Coarse):  {this.detune2[3]}\n"
                f"   Phase Reset on KON: {this.PR[3]}\n"
                f"   Operator AM:        {this.AM[3]}\n"
            )

        # what if we were able to save instruments separately?
        def save_instrument(this, compress = False, name = None):
            if not name:
                name = this.name
            try:
                inst = open(f'{name}.09IN', 'xb')
            except FileExistsError:
                inst = open(f'{name}.09IN', 'wb')
            data = bytes('INST', 'utf8')
            data += bytes(this.construct_instrument())
            inst.write(data) if not compress else inst.write(zlib.compress(data, 2))
            inst.close()
        def load_instrument(this, name):
            try:
                ins = open(f'{name}.09IN', 'rb').read()
            except FileNotFoundError:
                print('File not found')
                return
            if ins[:4] != b"INST":
                ins = zlib.decompress(ins)
                if ins[:4] != b"INST":
                    print('invalid shit')
                    return
            this.deconstruct_instrument(ins[4:])

        # wow! a whole new way to edit operator parameters
        def edit_op(this, op = 0,
                    feedback = 0,
                    attack = 31,
                    decay1 = 0,
                    sustain = 15,
                    decay2 = 0,
                    release = 15,
                    mult = 1,
                    egs = 0,
                    ssgeg = -1,
                    wave = -1,
                    enabled = 1,
                    tl = 0,
                    detune1 = 0,
                    detune2 = 0,
                    pr = 1,
                    am = 0,
                    ):
            this.set_feedback(op, feedback)
            this.set_attack(op, attack)
            this.set_decay1(op, decay1)
            this.set_sustain(op, sustain)
            this.set_decay2(op, decay2)
            this.set_release(op, release)
            this.set_op_mult(op, mult)
            this.set_egs(op, egs)
            this.set_ssgeg(op, ssgeg)
            this.set_op_wave(op, wave)
            this.set_op_enable(op, enabled)
            this.set_tl(op, tl)
            this.set_detunes(op, detune1, detune2)
            this.set_op_pr(op, pr)
            this.set_op_am(op, am)





    def __init__(this):
        this.instruments = []
        this.waves = []
        this.name = ''
        this.set_name('NEW BANK')
    def add_instrument(this, name):
        if len(this.instruments) > 255:
            raise this.WaveError("There can't be more that 256 instruments.")
        inst = this.YM2609Instrument()
        inst.set_name(name)
        this.instruments.append(inst)
        return this.instruments[this.instruments.index(inst)]
    def get_instrument(this, index):
        return this.instruments[index]
    def modify_instrument(this, index, instrument):
        this.instruments[index] = instrument
    def remove_instrument(this, index):
        return this.instruments.pop(index)

    def add_wave(this, wave):
        if len(this.waves) > 32767:
            raise this.WaveError("There can't be more that 32768 waves.")
        localwave = []
        for i in range(len(wave)):
            bytes_ = explode_16bits(wave[i])
            localwave.append(bytes_[0])
            localwave.append(bytes_[1])
        this.waves.append(localwave)
    def get_wave(this, index):
        return this.waves[index]
    def modify_wave(this, index, wave):
        this.waves[index] = wave
    def remove_wave(this, index):
        return this.waves.pop(index)
    def save_bank(this, compress = False, name = None):
        if not name:
            name = this.name
        if not len(this.instruments):
            raise this.InstrumentError("There must be at least one instrument!")
        if not len(this.waves):
            raise this.WaveError("There must be at least one wavetable!")
        try:
            bank = open(f"./{name}.2609", "xb")
        except FileExistsError:
            bank = open(f"./{name}.2609", "wb")
        data = b'2609'
        data += bytes([len(this.instruments) - 1]) # instruments
        data += bytes([((len(this.waves) - 1) >> 8), ((len(this.waves) - 1) & 255)]) # waves
        data += bytes(this.name, 'utf8')
        for i in range(len(this.instruments)):
            data += b'INST'
            data += bytes(this.instruments[i].construct_instrument())
        for i in range(len(this.waves)):
            data += b'WAVE'
            data += bytes( explode_16bits( (len(this.waves[i]) // 2) - 1) )
            data += bytes(this.waves[i])
        bank.write(data) if not compress else bank.write(zlib.compress(data, 2))
        bank.close()
    def load_bank(this, name):
        try:
            bank = open(f"{name}.2609", 'rb').read()
        except FileNotFoundError:
            print('bank not found :sob:')
            return
        if bank[:4] != b'2609':
            bank = zlib.decompress(bank)
            if bank[:4] != b'2609':
                print('invalid bank :sob:')
                return
        name = bank[7:23]
        this.name = ''
        for i in name:
            this.name += chr(i)
        inst_amnt = bank[4] + 1
        wave_amnt = ((bank[5] << 8) | bank[6]) + 1
        data = bank[23:]
        print(f"bank: {bank}\n"
              f"data: {data}\n"
              f"insts: {inst_amnt}\n"
              f"waves: {wave_amnt}")
        pointer = 0
        for i in range(inst_amnt + wave_amnt):
            data = data[pointer:]
            try:
                if data[:4] == b'INST':
                    print("instrument block")
                    inst = this.YM2609Instrument()
                    inst.deconstruct_instrument(data[4:])
                    this.instruments.append(inst)
                    pointer += 69
                elif data[:4] == b'WAVE':
                    print(f"wavetable block\n"
                          f"{data}")
                    wave_len = ((data[4] << 8) | data[5]) + 1
                    wave = []
                    for i in range(wave_len):
                        wave.append(data[6 + (i * 2)])
                        wave.append(data[6 + (i * 2) + 1])
                    this.waves.append(wave)
                    pointer += (wave_len * 2) + 6
                else:
                    print(
                        f"hit no data\n"
                        f"{data[:16]}"
                        )
            except IndexError:
                print("hit index error")
                break

    def set_name(this, name):
        while len(name) < 16:
            name += ' '
        this.name = name
    def get_name(this):
        return this.name



