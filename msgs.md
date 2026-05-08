# The MSGS situation is crazy

If you want to skip right to the point, click [here](#the-point).

I'm honestly surprised that this turned into actual somewhat
documentation of MSGS.


## What is MSGS?
Ahhhh, the good ol' MSGS.

Well, first of all, you may want to ask me the following question: "What the hell even is MSGS?"
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
or redefining of drum channels or use of GS banks, a GS Reset must be performed.
The sound set itself is located in `gm.dls` somewhere in `%systemroot%\System32\drivers\gm.dls`
folder on Windows 10 along with its `gmreadme.txt` file.

|                          | MSGS (Win10) | MSGS (WinXP_x64) / MSGS (Pre-Win10) |         SC-55          | SC-55mkII  |
|:------------------------:|:------------:|:-----------------------------------:|:----------------------:|:----------:|
|      Interpolation       |   Linear     |              Linear                 |       Linear(?)        |  Linear(?) |
|            GM            |     Yes      |                 Yes                 | Firmware 1.20 or later |    Yes     |
|            GS            |     Yes      |                 Yes                 |          Yes           |    Yes     |
|          Parts           |      16      |                 16                  |           16           |     16     |
|          Voices          |      32      |               64 / 32               |           24           |     28     |
|      Tones (Basic)       |     226      |                 226                 |          189           |    226     |
|    Tones (MT-32 Map)     |      0       |                  0                  |          128           |    128     |
|        Drum Kits         |      9       |                  9                  |           9            |     9      |
|       Sample Rate        |   22050hz    |             22050hz (?)             |        32000hz         |  32000hz   |
| Resonant Low Pass Filter |      No      |                 No                  |          Yes           |    Yes     |
|        Rate Limit        |     None     |                None                 |       31250 baud       | 31250 baud |
|       CC#91 Reverb       |      No      |                 No                  |          Yes           |    Yes     |
|       CC#93 Chorus       |      No      |                 No                  |          Yes           |    Yes     |

---

A lot of useful CC and other info on MSGS can be found
on [Zumi's MSGS blog](https://zumi.neocities.org/stuff/msgs/).
---

#### Crash course (but on Roland GS)

Roland GS is basically an extended version of General MIDI Level 1 aka GM.
It adds about this:
- Extra presets (arranged into "banks", with the default one being 0)
- Extra controllers (CC#91 Reverb, CC#93 Chorus, CC#94 Delay etc.)
- Extra drum kits apart from the default one (Power, Analog, Jazz and so on)

Activated via following SysEx: `F0 41 10 42 12 40 00 7F 00 41 F7`
Slight note about MSGS is that it always has these additional drum kits
accessible, regardless of if GS is enabled.

First synthesizer to incorporate Roland's GS standard was Sound Canvas SC-55.
At Yamaha this mode is referenced to as TG300B mode as they couldn't use the
trademark.

As a fun fact, Roland also had CTF (Capital Tone Fallback) which they
removed in SC-55mkII, supposedly because it was a patented tech
by Yamaha. What CTF does is basically this:
```
[User] Select this tone: [some unavailable patch via Bank MSB]
[SC55] Ok. Hey CTF, is this tone existent?
[CTF]  No. Closest tone to that is [closest available tone, rounded down]
[SC55] Ok, I'll use that.
```
##### GS Additions

Percussive sounds:

| Note | Percussion sound |
|:----:|:----------------:|
|  25  |    Snare Roll    |
|  26  |   Finger Snap    |
|  27  |      High Q      |
|  28  |       Slap       |
|  29  |   Scratch Push   |
|  30  |   Scratch Pull   |
|  31  |      Stick       |
|  32  |   Square Click   |
|  33  | Metronome Click  |
|  34  |  Metronome Bell  |
|  82  |      Shaker      |
|  83  |   Jingle Bell    |
|  84  |     Belltree     |
|  85  |    Castanets     |
|  86  |    Mute Surdo    |
|  87  |    Open Surdo    |

Controllers:

| CC# |        Purpose        |                                                     Short description                                                      |
|:---:|:---------------------:|:--------------------------------------------------------------------------------------------------------------------------:|
|  0  |    Bank Select MSB    |                                           The most significant byte of the bank                                            |
|  5  |    Portamento time    |                                              Controls the speed of portamento                                              |
| 32  |    Bank Select LSB    |                                           The least significant byte of the bank                                           |
| 65  |      Portamento       |                                     Whether is portamento on. 0\~63: Off, 64\~127: On                                      |
| 66  |       Sostenuto       |                               Like hold pedal, but only sustains notes that already were on                                |
| 67  |      Soft Pedal       |                                  Softens the notes, as in applies a slight lowpass filter                                  |
| 84  |  Portamento Control   |                                Specifies the note to glide from for the next note when set                                 |
| 91  |   Reverb Send Level   |                                   Specifies how loud should sound sent to reverb unit be                                   |
| 93  |   Chorus Send Level   |                                   Specifies how loud should sound sent to chorus unit be                                   |
| 94  |   Delay Send Level    |                                   Specifies how loud should sound sent to delay unit be                                    |
| 98  |       NRPN LSB        |                               Sets the NRPN LSB number to send data to. Sent after NRPN MSB                                |
| 99  |       NRPN MSB        |                               Sets the NRPN MSB number to send data to. Sent before NRPN LSB                               |
| 120 |    All Sounds Off     |                Cuts all sounds, regardless of whether are they held by CC#64 or CC#65 on specified channel                 |
| 121 | Reset All Controllers | Resets following controls: Pitchbend, PolyKeyPress, ChannelPress, Mod wheel, Expression, Hold, Portamento, Sostenuto, Soft |
| 123 |     All Notes Off     |                         Turns all notes off unless held by CC#64 Sustain Pedal or CC#65 Sostenuto                          |

MSGS, however, ignores portamento and soft pedal controls (a software synthesizer built to be
fast and cheap with an acceptable sound quality, after all).
Also, MSGS accepts all of these apart from Bank controls even when in GM mode,
including the extra percussion always being available.

---
#### Notes
<a name="msgs"></a>
[1] [A Japanese Wikipedia article about MSGS](https://ja.wikipedia.org/wiki/Microsoft_GS_Wavetable_SW_Synth) and [DirectMusic Synthesizer](https://ja.wikipedia.org/wiki/Microsoft_Synthesizer)

---

## The point.

So there is an unfinished [MSGS cover](/midis/crystal_msgs.mid) of [Crystal Oscillator](https://youtu.be/uL2XWtx3ePk)
unfortunately, I will not finish the midi at any cost, due to a simple reason: ~~not enough voices msgs has (32)~~
I have reconsidered this and am not as much bothered by voice limitation that much as it seems to not be that obvious after some modifications.
Here arises the second reason, which I did not mention previously: the song itself it too complex.

Anyway, back to the point:

I have tried Windows XP, but MSGS there differs in general:
- You can't play several different patches on a single channel (which is what I do for distorted kicks at the end and for this metal sfx at the start)
- CC#120 All Sounds Off seems to be acting as CC#123 All Notes Off (which is what I use to abruptly cut sounds)
  - After a bit of testing, it seems that despite sharing the action with CC#123 All Notes Off, it still ignores hold pedal and releases notes.
- It seems to sound a bit brighter?

Here is a comparison between MSGS on [Windows 10](/tests/msgs_10.ogg) and MSGS on [Windows 98](/tests/msgs_98.ogg), on that Crystal Oscillator cover.
I could not be bothered to re-render the Windows XP version, so you have Win98 one as a comparison instead. If anyone is willing to do so,
pull request it in there and you'll be credited.

And fun fact: this shares the behavior with Windows 98 MSGS (which I did test too).

So uh, sorry, no Crystal Oscillator midi.

To those who are still confused about what "Crystal Oscillator" is:

Crystal Oscillator is a Yamaha OPL3 Original song in HiTech genre with A4=450hz, made my the
Otomata Labs demogroup, specifically the Abstract64 member of it. It was made for
Oldskool Music Revision 2025, "<32kb executable" category, in which it took the
first place with the final file size of around 28 kilobytes.

## Personal notes

Honestly, I love MSGS. The low quality sound is signature IMO.
A lot of people say MSGS sounds bad. While I'd agree that MSGS
sounds not entirely good by its own, it can sound on par
with professional music when you adapt and use its quirks
to your advantage.

Few such examples are:

[`~ YAOTA ~`](https://www.youtube.com/watch?v=uCP62SBwe5M), by [Bruhman Kot](https://www.youtube.com/@kot_bruhman) (also known just as Kot or KoleOBlack)

[`~ GENERAL SERUM ~`](https://www.youtube.com/watch?v=QhoD5o0SYNU), by Kot and [Abstract64](https://www.youtube.com/@64abstract)

[HueArme](https://soundcloud.com/user-416698216-971657402), the person that pushed the synthesizer to its limits.
- of notable example is [PIPI](https://www.youtube.com/watch?v=6RIIdi_DA10);
it's one I find really cool. Using an electronic piano as a kick? you need
quite the creativity to come up with that.

And finally, shameless self-promotion here, cover of [Crystal Oscillator](/tests/msgs_10.ogg).