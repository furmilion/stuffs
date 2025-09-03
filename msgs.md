The MSGS situation is crazy

## What is MSGS?
Well, first of all, you my want to ask me the following question: "What the hell even is MSGS?"
Fret not, my dear friend for I will explain to you what is it.

So, you may or may not have a PC. If you do, you can run either
some Linux distro, MacOS or Windows.

If you have a Windows PC, *and* you run any version of Windows
from Windows 98 to Windows 10 inclusive, then congrats! 

Your system got bundled with additional piece of software, that
you may find in Device Manager. This mysterious piece of software
may either be titled "Microsoft GS Wavetable Synth" or
"Microsoft GS Wavetable SW Synth".
This is what we'll refer to as MSGS from on. I assume you know
what this abbreviation translates to.

### Crash course

MSGS<sup>[[1]](#msgs)</sup> is a software MIDI synth that is bundled with Windows operating
system, starting with Windows 98.

"GS" in its name isn't just for show, but actually means that it
supports [Roland's GS](https://en.wikipedia.org/wiki/Roland_GS) standard.
Judging by the patch set, MSGS was derived from [SC-55mkII](https://en.wikipedia.org/wiki/Roland_SC-55).

By default, MSGS starts in GM mode, and to use GS features such as addition
or redefining of drum channels or use of GS banks, a GS Reset myst be performed.
The sound set itself is located in `gm.dls` somewhere in `%systemroot%\WinSxS`
folder on Windows 10.

|                   |  MSGS   |         SC-55          | SC-55mkII  |
|:-----------------:|:-------:|:----------------------:|:----------:|
|        GM         |   Yes   | Firmware 1.20 or later |    Yes     |
|        GS         |   Yes   |          Yes           |    Yes     |
|       Parts       |   16    |           16           |     16     |
|      Voices       |   32    |           24           |     28     |
|   Tones (Basic)   |   226   |          189           |    226     |
| Tones (MT-32 Map) |    0    |          128           |    128     |
|     Drum Kits     |    9    |           9            |     9      |
|    Sample Rate    | 22050hz |        32000hz         |  32000hz   |
|  Low Pass Filter  |   No    |          Yes           |    Yes     |
|    Rate Limit     |  None   |       31250 baud       | 31250 baud |
|   CC#91 Reverb    |   No    |          Yes           |    Yes     |
|   CC#93 Chorus    |   No    |          Yes           |    Yes     |


---
#### Notes
<a name="msgs"></a>
[1] [A Japanese Wikipedia article about MSGS](https://ja.wikipedia.org/wiki/Microsoft_GS_Wavetable_SW_Synth) and [DirectMusic Synthesizer](https://ja.wikipedia.org/wiki/Microsoft_Synthesizer)

---


So there is an unfinished [MSGS cover](/midis/crystal_msgs.mid) of [Crystal Oscillator](https://youtu.be/uL2XWtx3ePk)
unfortunately, I will not finish the midi at any cost, due to a simple reason: not enough voices msgs has (32).
I have tried Windows XP, but MSGS there differs in general:
- You can't play several different patches on a single channel (which is what I do for distorted kicks at the end and for this metal sfx at the start)
- CC#120 All Sounds Off seems to be acting as CC#123 All Notes Off (which is what I use to abruptly cut sounds)
  - After a bit of testing, it seems that despite sharing the action with CC#123 All Notes Off, it still ignores hold pedal and releases notes.
- It seems to sound a bit brighter?

Here is a comparison between MSGS on [Windows 10](/tests/msgs_10.ogg) and MSGS on [Windows XP/98](/tests/msgs_xp.ogg), on that Crystal Oscillator cover.

And fun fact: this shares the behavior with Windows 98 MSGS (which I did test too).

So uh, sorry, no Crystal Oscillator midi.