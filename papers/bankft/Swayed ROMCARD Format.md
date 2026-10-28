# SWAYED
Swayed is an emulation of the famous hybrid FM + AWM synthesizer, the Yamaha SY77.

It accepts both custom wavecards in its own format and the official SY77 cards.

## SWAYED Wavecards Format

I have figured it out by hand.
I have put it out there so anyone who wants to make any kind of
wavecard editor for this plugin would know the features and
general file structure. Since I do not yet fully understand
*all* fields in the format, this "document" is subjected to
any changes, but generally it gets the file structure correct.

### Main format

| Offset               | Size (bytes)  | Type | Description |
|:---------------------|:--------------|:-----|:------------|
| 0x00                 | 8             | char | File signature. Always `SWAYSROM`. |
| 0x08                 | 2             | u16  | Unique ROM ID. |
| 0x0A                 | 2             | u16  | Size of bank name. `$BNAMESIZE$` |
| 0x0C                 | `$BNAMESIZE$` | char | Bank name. |
| 0x0C + `$BNAMESIZE$` | 2             | u16  | Instrument count. |
| 0x0E + `$BNAMESIZE$` | --            |  --  | Instrument definitions. |

### Instrument definition format

| Offset (relative)    | Size (bytes)  | Type | Description |
|:---------------------|:--------------|:-----|:------------|
| 0x00                 | 2             | u16  | Size of instrument name. `$INAMESIZE$` |
| 0x02                 | `$INAMESIZE$` | char | Instrument name. |
| 0x02 + `$INAMESIZE$` | 1             | u8   | Sample count. |
| 0x03 + `$INAMESIZE$` | --            |  --  | Sample definitions. |

### Sample definition format

| Offset (relative)    | Size (bytes)  | Type | Description |
|:---------------------|:--------------|:-----|:------------|
| 0x00                 | 1             | u8   | Unknown field. Does not affect synthesis parameters as far as I've tested. |
| 0x01                 | 1             | u8   | Ditto. |
| 0x02                 | 1             | u8   | Ditto. |
| 0x03                 | 1             | u8   | Ditto. |
| 0x04                 | 2             | u16  | Seems to be fine tune. Adds around 103 cents when at `0xFFFF`. |
| 0x06                 | 1             | u8   | Coarse tune up. I have not yet figured out how it works exactly in relation to root key. |
| 0x07                 | 1             | u8   | Playback related flags? Always `0x40` and does not play if not this value. |
| 0x08                 | 1             | u8   | Non-linear attenuation. Values over `0x7F` are treated as `0x00`. |
| 0x09                 | 1             | u8   | Less fine tune. Adds around 350 cents when `0xFF`. |
| 0x0A                 | 1             | u8   | Coarser tune. Adds 3 semitones per step. |
| 0x0B                 | 1             | u8   | Root key. |
| 0x0C                 | 1             | u8   | Upper bound on keybard. Low bound is 0 or upper bound of previous sample + 1. |
| 0x0D                 | 1             | u8   | Seems to be playback mode. 0 and 1 are One-shot, 2 is Forward loop, >=3 is Reverse. |
| 0x0E                 | 4             | u32  | Sample loop start. ROM offset relative to the end of the bank header. |
| 0x12                 | 4             | u32  | Sample loop end. ROM offset relative to the end of the bank header. |
| 0x16                 | 4             | u32  | Sample start. ROM offset relative to the end of the bank header. |
| 0x20                 | 4             | u32  | Sample end. ROM offset relative to the end of the bank header. |
