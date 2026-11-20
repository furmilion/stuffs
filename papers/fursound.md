# What is Fursound?
Fursound is my sound engine. Initially written in Python, and later ported to C (with the help of AI, obviously, I barely know any C).

It can do some basic wavetable/sample and 8-operator FM synthesis.

It has a few default shapes to choose from for FM, apart from samples:
- Square
- Pulse (yeah they are different waves internally)
- Sine (OPL3 wave 1)
- Sawtooth
- "Sample" (leftover, produces no sound by itself and an actual sample is used internally)
- "Wavetable" (leftover, produces no sound by itself and an actual sample is used internally)
- Triangle
- None (produces no sound and only ticks phase, unlike any wave with volume 0)
- Half Sine (OPL3 wave 2)
- Absolute Sine (OPL3 wave 3)
- Quarter Sine (OPL3 wave 4)
- Even Sine (OPL3 wave 5)
- Even Absolute Sine (OPL3 wave 6)
- Log Saw/Accumulator (Sawtooth passed through OPL's log table, also OPL3 wave 7)

Additional waves pending:
- Quarter Sine Alt
- Quarter Sine True
- Half Accum
- Abs Accum
- CQM variations of all OPL waves; the difference is really subtle but noticeable: sine waves sound a *liiiittle* bit square-ish; also all the waves have inverted output
- OPZ Triangle (wave 2)
- OPZ Cut Triangle (wave 4)
- OPZ Even Triangle (wave 6)
- OPZ Even Absolute Triangle (wave 8)
- OPZ Absolute Triangle (not present on actual chip)
- OPZ Quarter Triangle (not present on actual chip)
- MA7 and SY77/99 waves
- Half, Absolute, Quarter, Quarter Alt, Quarter True, and all of those with Even Period variant variations of all waves

The only reason for these to be pending is because the engine allows, and the bank format too.

Why was the sound engine made? Why not?
If it can make sound, I will fuck with it.

# Features

Fursound supports Wavetable/Sample and 8-operator FM synthesis, this includes FM with samples.

"FM synthesis" here refers to Yamaha terminology. Yamaha patented Phase Modulation synthesis as Frequency Modulation one.
An odd move, at least to me. Well, can't complain, they made a bunch of *reeally* powerful FM chips.

Phase Modulation is basically when one operator alters the phase of the other one.
Frequency Modulation is similar in that the modulated parameter is frequency.
They both produce similar results with sine wave, but they start to differ with other waves.

Fursound additionally features 5-stage envelope: Attack, Decay 1, Sustain, Decay 2, Release.
The idea of that was taken from YMW258-F "MultiPCM", a 28-channel sample synthesis chip that
features a hardware envelope in this specific combination. It also can be seen in OPM, OPZ and OPN chip families.

Fursound also supports stereo output, and with a bit of modification can also output multi-channel audio, which
will not be a feature here.

A single unit of sound output in Fursound is referred to as a Channel, of which there are 3 types:
- Wavetable/Operator
- Sample/Operator
- FM (a collection of operators)

## Close look at FM

FM here has all the basic Yamaha FM business: carriers, modulators, feedback, allat.

It can have up to 8 operators, with a configurable modulation matrix.
An FM channel has these elements:
- FM Modulation matrix

... aaaand thats it for now.

A single operator has these elements:
- Waveform (either a builtin one or a sample)
- Multiplier (multiplies channel frequency by the given value for this operator)
- Frequency
- Feedback (previous operator output is multiplied by this and sent back to the operator input)
- Modulation Input Multiplier (all values sent as modulation input are multiplied by this before being applied)
- Pulse Width, for the Pulse wave
- Modulation Output Volume (known as just "volume" in the code, multiplier for modulation output)
- Output Volume (multiplier for general output)
- Half-cycle Length (half cycle because of how Triangle was made by producing a Saw of length and slapping a reversed copy of it at the end)
- Pan (panning for output)

I additionally planned "stereo FM", that is panning affecting carrier operators'
channels separately, but that would technically mean 16 operators.

Pending additions:
- Ring Mod Matrix, Output and Input multipliers
- Hard Sync Matrix
- Envelope Hard Sync Matrix
- Key-scaled modulation parameters
- Velocity-scaled modulation parameters

These additions will ramp up already complex patch creation process up into the sky,
but will also allow for more insane flexibility in sound.

## Close look at Sample Synthesis

Nothing fancy is going on here.
It has:
- A sample reference
- Frequency
- Phase step
- Phase
- Volume
- Pan

Pending additions:
- Key-scaled Volume and Pan
- Velocity-scaled Pan

# MIDI

Fursound is being currently tested via MIDI and thus also needs a MIDI driver so that it can even produce sound.
The driver has a couple layers of abstraction:
- Channels are not addressed directly and are instead called voices, and are assigned sounds dynamically.
- There are now MIDI channels
- Due to this, there is also a patch bank that contains all the sounds, and correlates its patches with MIDI Program Changes
  - Samples included separately
- MIDI channels keep a list of their sounding voices to apply Controller Changes to
- Due to limited amount of voices there is also a voice stealing technique

## SysEx

Fursound accepts a couple of SysEx messages:
- System Resets (GM1/2. GS, XG, own)
- Roland Drum Setup SysEx
- Own unique messages

### Unique SysEx

Fursound has the following unique set of SysEx messages:
- FS RESET      (`F0 7A dd 00 01 F7`)
- FS DRUM       (`F0 7A dd 01 0n cd F7`), where `n` is *MIDI* channel, `cd` is `0` for melodic or `1` for drum
- FS INST PARAM (`F0 7A dd 02 0n ph pm pl vh vm vm vl F7`), where `n` is *MIDI* channel, `ph pm pl` is a 21-bit parameter ID (see parameter table), `vh vm vm vl` 28-bit is parameter value

TODO: parameter alteration for drum instruments

For any SysEx messages Fursound receives, it does not check the checksum.

## Instrument parameters

All instrument parameters can be controlled via both NRPN and SysEx.

PARAMETER TABLE
Operator indexes are 1-indexed.
All values are represented in hexadecimal.

| SysEx ID      | NRPN MSB/LSB | Parameter                        | Description |
|:--------------|:-------------|:---------------------------------|:------------|
| `00 00 00 0n` | `00` / `0n`  | FM Mod Matrix OP`n` Receive      | Configures operators Operator `n` receives mdoulation from.          |
| `00 00 00 1n` | `00` / `1n`  |    Mod Matrix OP`n` Receive Sync | Configures operators Operator `n` receives hard sync from.           |
| `00 00 00 2n` | `00` / `2n`  | RM Mod Matrix OP`n` Receive Ring | Configures operators Operator `n` receives ring modulation from.     |
| `00 00 00 3n` | `00` / `3n`  |    Mod Matrix OP`n` Receive EnvS | Configures operators Operator `n` receives envelope hard sync from.  |
| `00 00 00 40` | `00` / `40`  | Fixed freq                       | Configures whether operators are in Fixed Frequency mode. |
|      ---      |     ---      |                ---               | --- |
| `00 0n 00 00` | `0n` / `00`  | Operator `n` Pulse Width         | Pulse width of N'th operator, if it has Pulse Wave selected. Mapped 0..1, float |
| `00 0n 00 01` | `0n` / `01`  | Operator `n` Wave                | Wave of N'th operator. Mapped according to wave map. |
| `00 0n 00 02` | `0n` / `02`  | Operator `n` Multiplier Coarse   | Multiplier of N'th operator. NRPN carries 4 bits of coarse multiplier (0..15) and 10 bits of fine multiplier (within 1 coarse value). SysEx carries 7 bits of coarse multiplier (0..127) and 21 bits of fine multiplier (within 1 coarse value), allowing for sky-high precision |
| ---           | `0n` / `03`  | Operator `n` Multiplier Fine     | Fine Multiplier of N'th operator, applied on top of regular one. 1/16384th of one coarse value. |
| `00 0n 00 04` | `0n` / `04`  | Operator `n` Wave Length         | Half-cycle length of N'th operator's wave. SysEx only uses 14 bits. The value always has 1 added to it. Wave length change is heard immediately. |
| `00 0n 00 05` | `0n` / `05`  | Operator `n` Feedback            | Feedback of N'th operator. NRPN carries 1 sign bit and 13 value bits, converted to `-1..1` range in float. SysEx carries 1 bit of sign, 6 bits of coarse and 14 bits of fine, converted to `-64..64` range in float. |
| `00 0n 00 06` | `0n` / `06`  | Operator `n` ModIn   Multiplier  | ModIn  Multiplier of N'th operator. Works identically to feedback. |
| `00 0n 00 07` | `0n` / `07`  | Operator `n` ModOut  Multiplier  | ModOut Multiplier of N'th operator. Works identically to feedback. |
| `00 0n 00 08` | `0n` / `08`  | Operator `n` Output  Multiplier  | Output Multiplier of N'th operator. Works identically to feedback. |
| `00 0n 00 09` | `0n` / `09`  | Operator `n` Output  Pan         | Output Pan of N'th operator. NRPN carries 1 sign bit and 13 value bits. SysEx carries 1 bit of sign and 26 bits of Pan Position, squished into `-1..1` range in float, with `-1` being the leftmost, `0` being the center and `1` being the rightmost. Bit 27 sets whether the position is random each key. |
| `00 0n 00 0A` | `0n` / `0A`  | Operator `n` RingIn  Multiplier  | RingIn  Multiplier of N'th operator. Always converted to `-1..1` range. |
| `00 0n 00 0B` | `0n` / `0B`  | Operator `n` RingOut Multiplier  | RingOut Multiplier of N'th operator. Always converted to `-1..1` range. |
| `00 0n 00 0C` | `0n` / `0C`  | Operator `n` Fixed Frequency     | Used when the bit set, stored otherwise. NRPN selects a key instead. MSB selects a key, LSB tunes it in 1/128 steps. SysEx can either set the frequency directly (8.20 fixed point), or a key and a fine tune in 1/1048576 if bit 28 is set. |
| `00 0n 00 0D` | `0n` / `0D`  | Operator `n` Note On Phase       | Default phase operator starts with on a note-on. Always converted to `0..1` range. |
|      ---      |     ---      |                ---               | --- |
| `00 0n 00 10` | `0n` / `10`  | Operator `n` Key to Multiplier   | Adds/subtracts the given value from Multiplier based on offset from center key. Works identically to feedback. |
| `00 0n 00 11` | `0n` / `11`  | Operator `n` Key to Feedback     | Adds/subtracts the given value from Feedback based on offset from center key. Works identically to feedback. |
| `00 0n 00 12` | `0n` / `12`  | Operator `n` Key to ModIn        | Adds/subtracts the given value from ModIn  Multiplier based on offset from center key. Works identically to feedback. |
| `00 0n 00 13` | `0n` / `13`  | Operator `n` Key to ModOut       | Adds/subtracts the given value from ModOut Multiplier based on offset from center key. Works identically to feedback. |
| `00 0n 00 14` | `0n` / `14`  | Operator `n` Key to Output       | Adds/subtracts the given value from Output Multiplier based on offset from center key. Works identically to feedback. Clamps to the range of `0..64` instead and preserves sign. |
| `00 0n 00 15` | `0n` / `15`  | Operator `n` Key to Output Pan   | Adds/subtracts the given value from Output Pan based on offset from center key. NRPN works identically to feedback. SysEx carries 1 bit of sign and 27 bit of value, `-1..1` float range. Clamped if out of range. |
| `00 0n 00 16` | `0n` / `16`  | Operator `n` Key to RingIn       | Adds/subtracts the given value from RingIn based on offset from center key. NRPN works identically to feedback. SysEx carries 1 bit of sign and 27 bit of value, `-1..1` float range. Clamped if out of range. |
| `00 0n 00 17` | `0n` / `17`  | Operator `n` Key to RingOut      | Adds/subtracts the given value from RingOut based on offset from center key. NRPN works identically to feedback. SysEx carries 1 bit of sign and 27 bit of value, `-1..1` float range. Clamped if out of range. |
| `00 0n 00 18` | `0n` / `18`  | Operator `n` Key to NoteOnPhase  | Adds/subtracts the given value from Note On Phase based on offset from center key. Always converted to `0..1` range. |
| `00 0n 00 20` | `0n` / `20`  | Operator `n` KeyMult     Center Key | Center key. `-128..256`. |
| `00 0n 00 21` | `0n` / `21`  | Operator `n` KeyFbck     Center Key | Center key. `-128..256`. |
| `00 0n 00 22` | `0n` / `22`  | Operator `n` KeyMdIn     Center Key | Center key. `-128..256`. |
| `00 0n 00 23` | `0n` / `23`  | Operator `n` KeyVolm     Center Key | Center key. `-128..256`. |
| `00 0n 00 24` | `0n` / `24`  | Operator `n` KeyOut      Center Key | Center key. `-128..256`. |
| `00 0n 00 25` | `0n` / `25`  | Operator `n` KeyPan      Center Key | Center key. `-128..256`. |
| `00 0n 00 26` | `0n` / `26`  | Operator `n` RingIn      Center Key | Center key. `-128..256`. |
| `00 0n 00 27` | `0n` / `27`  | Operator `n` RingOut     Center Key | Center key. `-128..256`. |
| `00 0n 00 28` | `0n` / `28`  | Operator `n` NoteOnPhase Center Key | Center key. `-128..256`. |
|      ---      |     ---      |                ---               | --- |
| `00 0n 00 30` | `0n` / `30`  | Operator `n` Vel to Multiplier   | Adds/subtracts the given value from Multiplier based on offset from center velocity. Works identically to feedback. |
| `00 0n 00 31` | `0n` / `31`  | Operator `n` Vel to Feedback     | Adds/subtracts the given value from Feedback based on offset from center velocity. Works identically to feedback. |
| `00 0n 00 32` | `0n` / `32`  | Operator `n` Vel to ModIn        | Adds/subtracts the given value from ModIn  Multiplier based on offset from center velocity. Works identically to feedback. |
| `00 0n 00 33` | `0n` / `33`  | Operator `n` Vel to ModOut       | Adds/subtracts the given value from ModOut Multiplier based on offset from center velocity. Works identically to feedback. |
| `00 0n 00 35` | `0n` / `35`  | Operator `n` Vel to Output Pan   | Adds/subtracts the given value from Output Pan based on offset from center velocity. NRPN works identically to feedback. SysEx carries 1 bit of sign and 27 bit of value, `-1..1` float range. Pan is clamped if out of range. |
| `00 0n 00 36` | `0n` / `36`  | Operator `n` Vel to RingIn       | Adds/subtracts the given value from RingIn based on offset from center key. NRPN works identically to feedback. SysEx carries 1 bit of sign and 27 bit of value, `-1..1` float range. Clamped if out of range. |
| `00 0n 00 37` | `0n` / `37`  | Operator `n` Vel to RingOut      | Adds/subtracts the given value from RingOut based on offset from center key. NRPN works identically to feedback. SysEx carries 1 bit of sign and 27 bit of value, `-1..1` float range. Clamped if out of range. |
| `00 0n 00 38` | `0n` / `38`  | Operator `n` Vel to NoteOnPhase  | Adds/subtracts the given value from Note On Phase based on offset from center key. Always converted to `0..1` range. |
| `00 0n 00 40` | `0n` / `40`  | Operator `n` VelMult     Center Vel | Center velocity. `0..127`. |
| `00 0n 00 41` | `0n` / `41`  | Operator `n` VelFbck     Center Vel | Center velocity. `0..127`. |
| `00 0n 00 42` | `0n` / `42`  | Operator `n` VelMdIn     Center Vel | Center velocity. `0..127`. |
| `00 0n 00 43` | `0n` / `43`  | Operator `n` VelVolm     Center Vel | Center velocity. `0..127`. |
| `00 0n 00 45` | `0n` / `45`  | Operator `n` VelPan      Center Vel | Center velocity. `0..127`. |
| `00 0n 00 46` | `0n` / `46`  | Operator `n` RingIn      Center Vel | Center velocity. `0..127`. |
| `00 0n 00 47` | `0n` / `47`  | Operator `n` RingOut     Center Vel | Center velocity. `0..127`. |
| `00 0n 00 48` | `0n` / `48`  | Operator `n` NoteOnPhase Center Vel | Center velocity. `0..127`. |
|      ---      |     ---      |                ---               | --- |
| `00 0n 00 50` | `0n` / `50`  | Operator `n` Envelope Attack     | Enelope attack time. MSB: `0..16` = 0..1s, `16..32` = 1..3s, `32..64` = 3..7s, `64..80` = 7..15s, `80..96` = 15..31s, `96..112` = 31..63s, `112..126` = 63..127s, `127` = inf; LSB is fine step. SysEx is 9.19 fixed point |
| `00 0n 00 51` | `0n` / `51`  | Operator `n` Envelope Decay 1    | Enelope decay 1 time. |
| `00 0n 00 52` | `0n` / `52`  | Operator `n` Envelope Decay 2    | Enelope decay 2 time. |
| `00 0n 00 53` | `0n` / `53`  | Operator `n` Envelope Release    | Enelope release time. |
| `00 0n 00 54` | `0n` / `54`  | Operator `n` Envelope Sustain    | Enelope sustain value. |
