# What is ECW?

ECW is a bank format used by Ensoniq/Creative Software Synthesizer.

As I found basically no tools nor even an unofficial doc for the format,
I made my own, with the help of Claude. If you hate AI, get over it.

## The software synth

The software synthesizer is a 128-voice GM/GS synth
that lacks filters and has toggleable global reverb
and chorus. It consumes the aforementioned ECW banks
to produce sound output.

# Bank format

| offset | type     | description                                                                        |
| :----- | :------- | :--------------------------------------------------------------------------------- |
| 0x0000 | char[4]  | Signature. Always `ECLW`                                                           |
| 0x0004 | u16      | Version?                                                                           |
| 0x0006 | u16      | Unknown. Always `0x1`                                                              |
| 0x0008 | u32      | Table directory offset `dir_off`; `0x700` in all 3 banks that came with the synth. |
| 0x000C | u32      | Unknown. Always `0x10`                                                             |
| 0x0010 | char[80] | Copyright information string.                                                      |
| 0x0060 | char[80] | Wavetable set name.                                                                |
| 0x00B0 | char[80] | Original filename.                                                                 |

## Table directory and tables


Group 3 omits record count.

| offset               | type   | description             |
| :------------------- | :----- | :---------------------- |
| `dir_off`            | u32    | Separator. `0x00010001` |
| `dir_off` + `0x0001` | --- | Group 1                 |
| `dir_off` + `0x0001` | --- | Group 1                 |
| `dir_off` + `0x0001` | --- | Group 2                 |
