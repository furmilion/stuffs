# What is TIunA?

TIunA is a software pitch driver made by Natt Akuma for the Atari TIA.

How does TIunA achieve software pitch? Simple. TIunA rapidly switches
between two different pitches at the right timing. That's the secret.
TIunA operates at approximately 5kHz rate.

TIunA first appeared in "Twin" Atari 2600 music demo of AYCE (All You Can Execute)
group.

### "Twin" song
The song is originally made by Petriform for the "Familial Verses"
GB x VB album.
A cover of this song appears in the "Twin" music demo, arranged by Abstract64.

Currently, Natt Akuma and Abstract64 are both present in AYCE and Otomata Labs demogroups.


## TIunA ending GFX font reference

| Nibble | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
|:------:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|   0    |   | o | r | i | . | p | e | t | f | m | d | v | n | a | b | s |
|   1    | c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |

```asm
font_gfx
    .text x"00000000000000" ; ' '
    .text x"3c66666666663c" ; 'o'
    .text x"6666667c66667c" ; 'r'
    .text x"7e18181818187e" ; 'i'
    .text x"00000000181800" ; '.'
    .text x"6060607c66667c" ; 'p'
    .text x"7e60607e60607e" ; 'e'
    .text x"1818181818187e" ; 't'
    .text x"6060607c60607e" ; 'f'
    .text x"66667676767e66" ; 'm'
    .text x"7c66666666667c" ; 'd'
    .text x"183c3c66666666" ; 'v'
    .text x"66666e6e767666" ; 'n'
    .text x"66667e66663c18" ; 'a'
    .text x"7c66667c66667c" ; 'b'
    .text x"7c06063c60603e" ; 's'
    .text x"3c66606060663c" ; 'c'
```
The text in credits looks approximately like this:
```
   TWIN
 o | d | a
 r | r | r
 i | v | r
 . | . | .
 p | n | a
 e | a | b
 t | t | s
 r | t | t
 i |   | r
 f |   | a
 o |   | c
 r |   | t
 m |   | 
```


## My custom font GFX reference
| Nibble | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
|:------:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|   0    |   | a | b | c | d | e | f | g | h | i | j | k | l | m | n | o |
|   1    | p | q | r | s | t | u | v | w | x | y | z | . | , | : | ; | / |
|   2    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |   |   |   |   |   |   |
|   3    |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |

```asm
font_gfx
    .text x"00000000000000" ; ' '
    .text x"66667e66663c18" ; 'a'
    .text x"7c66667c66667c" ; 'b'
    .text x"3c66606060663c" ; 'c'
    .text x"7c66666666667c" ; 'd'
    .text x"7e60607e60607e" ; 'e'
    .text x"6060607c60607e" ; 'f'
    .text x"3c66666e60663c" ; 'g'
    .text x"6666667e666666" ; 'h'
    .text x"7e18181818187e" ; 'i'
    .text x"3c660606060606" ; 'j'
    .text x"666e6c787c6e66" ; 'k'
    .text x"7e606060606060" ; 'l'
    .text x"66667676767e66" ; 'm'
    .text x"66666e6e767666" ; 'n'
    .text x"3c66666666663c" ; 'o'
    .text x"6060607c66667c" ; 'p'
    .text x"3f6e666666663c" ; 'q'
    .text x"6666667c66667c" ; 'r'
    .text x"7c06063c60603e" ; 's'
    .text x"1818181818187e" ; 't'
    .text x"3c666666666666" ; 'u'
    .text x"183c3c66666666" ; 'v'
    .text x"667e6e6e6e6666" ; 'w'
    .text x"666672381c4e66" ; 'x'
    .text x"1818183c7e6666" ; 'y'
    .text x"7e60703c0e067e" ; 'z'
    .text x"00000000181800" ; '.'
    .text x"00000030181800" ; ','
    .text x"00181800181800" ; ':'
    .text x"30181800181800" ; ';'
    .text x"603030180c0c06" ; '/'
    .text x"00000000000000" ; '0'
    .text x"00000000000000" ; '1'
    .text x"00000000000000" ; '2'
    .text x"00000000000000" ; '3'
    .text x"00000000000000" ; '4'
    .text x"00000000000000" ; '5'
    .text x"00000000000000" ; '6'
    .text x"00000000000000" ; '7'
    .text x"00000000000000" ; '8'
    .text x"00000000000000" ; '9'
```

## Furnace `EExx` effect reference for TIunA

Those are the actions that `EExx` effects perform depending on the value.

How the lines look depends on the pitches of the channels.

Note that hi nibbles past `1` are always flashes and lo nibbles
past 8 are always disable lines, unless stated otherwise.

| `EExx` Lo Nibble ><br>---------<br>`EExx` Hi Nibble V |           0           |           1           |             2             |           3           |           4           |             5             |           6           |                  7                  |           8           |               F                |
|:-----------------------------------------------------:|:---------------------:|:---------------------:|:-------------------------:|:---------------------:|:---------------------:|:-------------------------:|:---------------------:|:-----------------------------------:|:---------------------:|:------------------------------:|
|                           0                           |         Line          |    2 lines (close)    |  2 lines (medium spaced)  |    3 lines (close)    |  2 lines (far apart)  | 1 line (double thickness) |  3 lines (far apart)  | Line (quadruple thickness + shadow) |    Lines disabled     |                                |
|                           1                           | Flash varint of above | Flash varint of above |   Flash varint of above   | Flash varint of above | Flash varint of above |   Flash varint of above   | Flash varint of above |        Flash varint of above        | Flash varint of above |                                |
|                           F                           |                       |                       |                           |                       |                       |                           |                       |                                     |                       | Stop playback and show credits |

## Links

The code for the driver and the demo is available at [AYCEdemo/twin-tiuna](https://github.com/AYCEdemo/twin-tiuna).

Abstract64's arrangement is available at https://www.youtube.com/watch?v=5xWEkZSFwKQ,
however the visuals are XYscope rather than an emulator or hardware recording,
though the intro splash warning of possible seizures due to rapid flashing
is still present.

The original track is available on [YouTube](https://www.youtube.com/watch?v=C0vqrmRgfM8)
and [Bandcamp](https://petriform.bandcamp.com/album/familial-verses).

Abstract64 is present on:
- [YouTube](https://www.youtube.com/@64abstract)
- [Twitter/X](https://x.com/@64abstract)
- Discord (64abstract)

Natt Akuma is present on:
- [YouTube](https://www.youtube.com/@akumanatt)
- [Twitter/X](https://x.com/@akumanatt)
- Discord (akumanatt)