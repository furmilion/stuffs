# Yamaha SWPxx series

## What is it?

SWPxx is a series of sound chips made by Yamaha, utilized in
various hardware from MIDI modules to synthesizers.

One of the key features of SWPs is a relatively high amount
of voices and support for sending sound out to a DSP like
their own MEG (Multiple Effect Generator) for additional
sound processing live reverb, chorus or variation (which
itself consists from a bunch of selectable effects).

This doc will also include SWX, SWL and MultiPCM (despite this one already being explained in a subfolder elsewhere).

## Chips

### SWP00 / TC170C120SF-003 / XQ036A00

Used in MU50 MIDI Module, DB50XG and SW60XG daughterboards.

One of the weakest chips in the family, although versatile.

Does not present anything really interesting, besides having
an integrated MEG DSP inside.

Features:
- 32 voices
- Hardware envelopes
- 4 sample formats (8 bit, 12 bit, 16 bit, DPCM)
- 7 total output channels (2 are used for stereo output, other 5 are for intermediate sound exchange between on-chip DSP)
- 24 bits of addressable space; However MU50 only had 4 MB of Wave ROM.
- Integrated MEG DSP
 - 192 steps of program
 - memory access only when program counter is divisible by 3
 - internal ROM is said to be undumpable
 
A low-power variant SWP00M / TC203C060AF-001 / XS724A00 exists, used in QY70 and 2 PSR keyboards.

### SWP20 / YMW275-F / XN346A00

Seemingly just a better version of SWP00, which was based upon this chip. Used in MU80, which supplied it with an 8-megabyte Wave ROM.

Unlike its less powerful sibling, has these differences:
- Does not integrate MEG, and thus has to use a separate chip for that, which obviously is the MEG itself.
- Has filters

### SWP30 / TC203C760HF-001 / XR738A00

An upgrade to SWP20. Features:
- 64 voices
- Hardware envelopes
- Filters (LP and HP)
- 4 sample formats of SWP00
- Supports backwards playback of samples
- MEG, integrated yet again
 - Now 384 steps of program

Used in MU90, MU100, MU128 and their rackmount versions.
MU90 supplies 8 megabytes of wave, MU100 and onwards go for all 16.

Also used in MU500, MU1000 and MU2000. Latter two incorporate two of the sound chip for 128 voice polyphony.
This also doubles the amount of insertion effect units that can be used, making it 4.

### SWP50 / T6TJ3XBG-0001 / X8940A00

Sampler, used in Motif-Rack and Motif-ES.

All I know about it is that it has:
- 64 voices
- possibly 32 bits of addressable space (allowing for a Wave ROM of up to 4 gigabytes); Unit itself supplies the chip with 96 megabytes of waves.
- Has some on-chip DSP

### SWP70 / YMW832-CZ

Used in MODX-6, MODX-7 and MODX-8. Incredibly powerful 128-voice 6-op FM sound processor.
Someday we will get an emlation of it.

### SWX00 / HG73C201FD / XT890A00

Seems to be on par with SWP00, apart from not having an integrated DSP.

Is also a CPU.

### SWL01 / YMW767-V

Not much known about this one, except for:
- Has 32 voices
- Has integrated reverb and chorus unit
- Is also a CPU.

### SWLL / YMW830-V

Seems like it has a lot in common with SWP30 and is based on that.
Used in PSS-A50 keyboard, for which I have yet to find *any* Wave ROM dumps.
I assume the size would be about 2-4MB, as the keyboard is fairly cheap.

### MultiPCM / YMW258-F

A sampler, featured in MU5 and TG100.

Features:
- Possible FM functionality (unlikely; no die shot to either prove or disprove this claim)
- 21 bits of addressable space. Both units supply full 2/2 megabytes of waves to the chip.
- 2 sample formats (8- and 12-bit); curiously enough, the middle byte of 3 in 12-bit sample mode should be nibble-swapped for proper sound: `AA BA BB`
- 28 voices
- Hardware envelopes
- Linear sample interpolation
- Absolutely no effects