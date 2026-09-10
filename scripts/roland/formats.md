# SC-55 and alike ROM Format

SC-55 uses scrambling to prevent data copying (and likely modifying).
The scrambling is applied both on byte and address line level.

Here are the tables for both:

BYTE LEVEL
| Scrambled position | Actual position |
|:-------------------|:----------------|
| 0                  | 2               |
| 1                  | 0               |
| 2                  | 4               |
| 3                  | 5               |
| 4                  | 7               |
| 5                  | 6               |
| 6                  | 3               |
| 7                  | 1               |

ADDRESS LINE LEVEL
| Scrambled position | Actual position |
|:-------------------|:----------------|
| 0                  | 2               |
| 1                  | 0               |
| 2                  | 3               |
| 3                  | 4               |
| 4                  | 1               |
| 5                  | 9               |
| 6                  | 13              |
| 7                  | 10              |
| 8                  | 18              |
| 9                  | 17              |
| 10                 | 6               |
| 11                 | 15              |
| 12                 | 11              |
| 13                 | 16              |
| 14                 | 8               |
| 15                 | 5               |
| 16                 | 12              |
| 17                 | 7               |
| 18                 | 14              |
| 19                 | 19              |
| 20                 | 20              |
| 21                 | 21              |
| 22                 | 22              |
| 23                 | 23              |

All the settings for the samples and instruments are in control ROM.

The compression used by the SC-55 and alike hardware and up until Fantom-2019 use the so-called FCE-DPCM.

FCE-DPCM seems to come in 2 parts: the shift table for, well, shifting,
and the actual DPCM data in 16-byte blocks. Dtech says that decompressed
data is close to 24-bit dynamic range, but from my tests its around 29-30 bits.

The shift table size depends on the maximum address sample reaches. This is limited to about 1 MByte per bank.
SC-55 dedicates first 1024 bytes to about nothing besides the date and the GS "watermark",
and right after that the DPCM shift table starts, spanning 31744 bytes,
and the at address 32768 througn 1048576 lies teh actual DPCM data.

As simple as that.

Now back to ROM scrambling: first 32 bytes of each bank seem to never be scrambled.
They contain the identificator of the ROM. Next 16 bytes seem to contain the ROM version.
And the next 16 bytes contain date in plain ASCII.

Thats about it there.
For the CPU and control ROM formats, see [EmuSC Wiki](https://github.com/skjelten/emusc/wiki/).

I am planning to make an editor for SC-55 that will be able to modify the instruments and customize the samples.
Half the work is essentially done already, since I have a decoder and already know the control ROM format.
Making the UI won't be that hard because I'll be using ImGUI. The only part that needs to be done is FCE-DPCM
encoder.

# SR-JV80 Card ROM Format

The scrambling and the data format is the same as SC-55.

A wavecard is 8MB in size.
One wavecard contains 7 DPCM data banks and 1 patch bank, each 1 MByte in size.

---
