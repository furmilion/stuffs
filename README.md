# stuffs
here are my various funny things i made
midis, tracker modules, other stuff, maybe code
that one might possibly find useful in some way

Currently contains:

- MIDI Files (alongside eith Domino MIDI Editor's `.dms` projects)
- SC-55 Utilities (2):
  - Image/Text to Display SysEx converter (awaiting fixing)
  - [Unfinished] ROM Decompressor
- FurADPCM custom codec encoder/decoder written in python (currently in a terrible state, a rewrite is pending)
- [funcs](scripts/funcs.py) general purpose function library providing some small functions.
- FurWAVE Microsoft Wave read/write library (write-only currently), supporting both Integer and IEEE Float bit depths, 
  unlike [`save_riff()`](scripts/funcs.py) from [funcs.py](scripts/funcs.py) which provides only a basic Integer writer
- Sega MultiPCM/Yamaha OPL4 sample ROM decompressor. Pending expansions:
  - Yamaha S-YXG50/S-YXG2006LE Software synthesizer sample and instrument tables decryption
  - Yamaha MU Series Sample ROM decryption (MU100 and later are yet to be considered)
  - SC-55 ROM decompression (which would make the other utility obsolete)
  - SC-88 ROM decompression? 
  - TODO: YMW270-F GEW7
- (Not the best) Console HEX Editor written in python
- [FurSound](scripts/FurSound.py): customizable (and slow due to how it works) audio engine. (Currently WIPs)

Some status rundown:
- FurADPCM: stable in all cases I tested it in, but I'll rewrite it someday
- FurWAVE: stable; solid as is
- Sample ROM decompressor: pretty much stable; wip
- FurSound: stable; wip
- Console HEX Editor: stable; wip