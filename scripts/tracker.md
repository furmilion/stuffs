I have no name for the tracker yet and its all theoretical,
sooooooooooo...

This tracker is kinda supposed to be a way to control the
FurSound sound engine.
I never quite understood why Little Endian is a thing,
so all data is stored in big endian format, or at least should be.

## Head

|     Offset     | Length | Data | Description                                 |     
| -------------: | -----: | :--: | :------------------------------------------ |  
|              0 |      4 | FSUT | Signature                                   |     
|              4 |      1 |      | Amount of channels                          |     
|              5 |      1 |      | Speed (ticks per row)                       |     
|              6 |      1 |      | Tick rate (driver updates/s), integer value |     
|              7 |      1 |      | Speed 2                                     |
|              8 |      4 |      | Integer sample rate                         |
|              C |      1 |      | Name length (up to 255 symbols)             |     
|              D |      ? |      | Name                                        |     
|          D + ? |      1 |      | Author length                               |     
|          E + ? |      ? |      | Author                                      |     
|      E + ? + ? |      ? |      | Channel definition × Channels               |     
| 12 + ? + ? + ? |      ? |      | Orders (up to 256)                          |     


## Channels

A channel definition consists of the following:

All of the values here are initial and are a subject to change mid-song

| Offset | Length |   Data   | Description                                                                    |
| -----: | -----: |:--------:|:-------------------------------------------------------------------------------|
|      0 |      4 |   CHAN   | Block signature                                                                |
|      4 |      1 |          | Volume, 0...255                                                                |
|      5 |      1 |          | Panning, 0.255, 127 and 128 are center                                         |
|      6 |      1 | PPIICCCC | Pulse width 2 hi bits, Interpolation type, Channel type                        |
|      7 |      1 |          | Pulse width, lower 8 bits                                                      |
|      8 |      1 |          | Phase                                                                          |
|      9 |      1 |          | Wave length                                                                    |
|      A |      4 |          | Attack time in seconds, float                                                  |
|      E |      4 |          | Decay 1 time in seconds, float                                                 |
|     12 |      4 |          | Sustain level in %, uint. to get the actual value, divide this by (uint32_t)-1 |
|     16 |      4 |          | Decay 2 time in seconds, float                                                 |
|     1A |      4 |          | Release time in seconds, float                                                 |

## Orders

TODO: Orders format


## Effects

Since I stated that channel parameters
could be altered mid song, I should provide
you with at least some means to make those,
if not with instruments.
If it so happens that I will not implement
instruments, well then welcome to ProTracker 2.

The effects scheme is designed after Furnace,
so a lot, if not all, will overlap

Each effect consists of 2 bytes: the effect byte itself, and the value byte.

|  EFID  | Description                                                                                                                          |
|:------:|:-------------------------------------------------------------------------------------------------------------------------------------|
| `00xy` | Classic 3-note arpeggio. Base > base + `x` > base + `y`                                                                              |
| `01xx` | Slide pitch up by `xx` per tick                                                                                                      |
| `02xx` | Ditto, but in the opposite direction                                                                                                 |
| `03xx` | Glide to note with the speed of `xx` units per tick                                                                                  |
| `04xy` | Vibrato with speed `x` and depth `y` Depth `F` is about quarter semitone in each direction                                           |
| `05xx` |                                                                                                                                      |
| `06xx` |                                                                                                                                      |
| `07xy` | Volume vibrato a.k.a. tremolo. Depth 1 is 1/15th of the channel volume                                                               |
| `08xy` | Set panning (variant 1). `x` - left volume, `y`- right volume                                                                        |
| `09xx` | Set speed 1, or speed 2 if speed 1 is 0                                                                                              |
| `0Axy` | Volume slide, `x0` - down, `0y` - up. Speed `F` is about 15/60th of the channel volume per tick                                      |
| `0Bxx` | Jump to order `xx`                                                                                                                   |
| `0Cxx` |                                                                                                                                      |
| `0Dxx` | Jump to row `xx` of the next order. Can be used in combination with `0Bxx` for both effects                                          |
| `0Exx` |                                                                                                                                      |
| `0Fxx` | Set speed 2, or speed 1 if speed 2 is 0                                                                                              |
| `1xxx` | Set pulse width (0...4095). I have extra 2 bits here so I put them into use for quadruple the PWM depth                              |
| `2xxx` | Set phase offset (0...4095). Same as with the pulse                                                                                  |
| `80xx` | Set panning (variant 2). This variant matches initial channel pan setting. `00` = hard left, `FF` = hard right, `7F` & `80` = center |
| `81xx` | Set panning (left channel)                                                                                                           |
| `82xx` | Set panning (right channel)                                                                                                          |
| `83xx` |                                                                                                                                      |
| `84xx` |                                                                                                                                      |
| `85xx` |                                                                                                                                      |
| `86xx` |                                                                                                                                      |
| `87xx` |                                                                                                                                      |
| `88xx` |                                                                                                                                      |
| `89xx` |                                                                                                                                      |
| `8Axx` |                                                                                                                                      |
| `8Bxx` |                                                                                                                                      |
| `8Cxx` |                                                                                                                                      |
| `8Dxx` |                                                                                                                                      |
| `8Exx` |                                                                                                                                      |
| `8Fxx` |                                                                                                                                      |
| `90xx` | Sample offset, byte 1 (x1)                                                                                                           |
| `91xx` | Sample offset, byte 2 (x256)                                                                                                         |
| `92xx` | Sample offset, byte 3 (x65536)                                                                                                       |
| `93xx` |                                                                                                                                      |
| `94xx` |                                                                                                                                      |
| `95xx` |                                                                                                                                      |
| `96xx` |                                                                                                                                      |
| `97xx` |                                                                                                                                      |
| `98xx` |                                                                                                                                      |
| `99xx` |                                                                                                                                      |
| `9Axx` |                                                                                                                                      |
| `9Bxx` |                                                                                                                                      |
| `9Cxx` |                                                                                                                                      |
| `9Dxx` |                                                                                                                                      |
| `9Exx` |                                                                                                                                      |
| `9Fxx` |                                                                                                                                      |
| `Axxx` | Override attack rate (0...1023). Each step is about 1/16th of a second.                                                              |
| `Axxx` | Override decay 1 rate (1024...2047). Same step size as above                                                                         |
| `Axxx` | Override decay 2 rate (2048...3071). Ditto                                                                                           |
| `Axxx` | Override release rate (3072...4095). Ditto                                                                                           |
| `B0xx` | Override sustain level. (0..255)                                                                                                     |
| `B1xx` | Override wave                                                                                                                        |
| `B2xx` | Override interpolation                                                                                                               |
| `B3xx` |                                                                                                                                      |
| `B4xx` |                                                                                                                                      |
| `B5xx` |                                                                                                                                      |
| `B6xx` |                                                                                                                                      |
| `B7xx` |                                                                                                                                      |
| `B8xx` |                                                                                                                                      |
| `B9xx` |                                                                                                                                      |
| `BAxx` |                                                                                                                                      |
| `BBxx` |                                                                                                                                      |
| `BCxx` |                                                                                                                                      |
| `BDxx` |                                                                                                                                      |
| `BExx` |                                                                                                                                      |
| `BFxx` |                                                                                                                                      |
| `Cxxx` | `C000`...`C3FF` - set tick rate (0...1023)                                                                                           |
| `C4xx` |                                                                                                                                      |
| `C5xx` |                                                                                                                                      |
| `C6xx` |                                                                                                                                      |
| `C7xx` |                                                                                                                                      |
| `C8xx` |                                                                                                                                      |
| `C9xx` |                                                                                                                                      |
| `CAxx` |                                                                                                                                      |
| `CBxx` |                                                                                                                                      |
| `CCxx` |                                                                                                                                      |
| `CDxx` |                                                                                                                                      |
| `CExx` |                                                                                                                                      |
| `CFxx` |                                                                                                                                      |
| `D0xx` |                                                                                                                                      |
| `D1xx` |                                                                                                                                      |
| `D2xx` |                                                                                                                                      |
| `D3xx` |                                                                                                                                      |
| `D4xx` |                                                                                                                                      |
| `D5xx` |                                                                                                                                      |
| `D6xx` |                                                                                                                                      |
| `D7xx` |                                                                                                                                      |
| `D8xx` |                                                                                                                                      |
| `D9xx` |                                                                                                                                      |
| `DAxx` |                                                                                                                                      |
| `DBxx` |                                                                                                                                      |
| `DCxx` |                                                                                                                                      |
| `DDxx` |                                                                                                                                      |
| `DExx` |                                                                                                                                      |
| `DFxx` |                                                                                                                                      |
| `E0xx` |                                                                                                                                      |
| `E1xx` |                                                                                                                                      |
| `E2xx` |                                                                                                                                      |
| `E3xx` |                                                                                                                                      |
| `E4xx` |                                                                                                                                      |
| `E5xx` |                                                                                                                                      |
| `E6xx` |                                                                                                                                      |
| `E7xx` |                                                                                                                                      |
| `E8xx` |                                                                                                                                      |
| `E9xx` |                                                                                                                                      |
| `EAxx` |                                                                                                                                      |
| `EBxx` |                                                                                                                                      |
| `ECxx` |                                                                                                                                      |
| `EDxx` |                                                                                                                                      |
| `EExx` |                                                                                                                                      |
| `EFxx` |                                                                                                                                      |
| `F0xx` |                                                                                                                                      |
| `F1xx` |                                                                                                                                      |
| `F2xx` |                                                                                                                                      |
| `F3xx` |                                                                                                                                      |
| `F4xx` |                                                                                                                                      |
| `F5xx` |                                                                                                                                      |
| `F6xx` |                                                                                                                                      |
| `F7xx` |                                                                                                                                      |
| `F8xx` |                                                                                                                                      |
| `F9xx` |                                                                                                                                      |
| `FAxy` | Fast volume slide (4x speed)                                                                                                         |
| `FBxx` |                                                                                                                                      |
| `FCxx` |                                                                                                                                      |
| `FDxx` |                                                                                                                                      |
| `FExx` |                                                                                                                                      |
| `FFxx` | Stop song                                                                                                                            |