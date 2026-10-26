# The MSGS situation is crazy

[ Last edited 26/10/26 ]

Contents:
 - [Disclaimer](#disclaimer)
 - [What is MSGS?](#what-is-msgs)
   - [Crash course](#crash-course)
     - [SysEx Response](#sysex-response)
     - [GS crash course](#gs-crash-course)
       - [GS Additions](#gs-additions)
   - [Notes](#notes)
 - [Quirks](#quirks)
 - [Why?](#why)
 - [Personal notes](#personal-notes)
 - [Credits](#credits)

I'm honestly surprised that this turned into actual somewhat
documentation of MSGS.
## Disclaimer

This is a rant that eventually turned into a research.
All of the stuff described here is based purely on my
observations and could be wrong or different in any part
of this, I did not do any decompilations.

This document also references a [clean-room reimplementation of MSGS](https://github.com/sloptainment/slopgs) as found in Windows XP, Service Pack 3.

Enjoy reading!

## What is MSGS?
<img width="360" height="356" alt="image" src="https://github.com/user-attachments/assets/8014fa25-c42b-4a1d-9ffe-a6d4229f003c" />

Ahhhh, the good ol' MSGS.

Well, first of all, you may want to ask me the following question: "What the hell even is MSGS?"
Fret not, my dear friend for I will explain to you what is it.

So, you may or may not have a PC. If you do, you can run either
some Linux distro, MacOS or Windows.

If you have a Windows PC, *and* you run any version of Windows
from Windows 98 to Windows 11 inclusive, then congrats! 

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

MSGS takes *aaalmost* the entire sound set from an SC-55mkII, that is what I believe at least.
Bass Drum 1 might come from later modules, as the sound is not present in the SC-55 line.

|                          | MSGS (Win10) | MSGS (Pre-Win10)<sup>[[1]](#why-pre-10)</sup> | MSGS (Win11 Inbox Dev Preview 9, Native mode<sup>[[3]](#native-mode-note)</sup>) | SC-55                  | SC-55mkII   |
|:------------------------:|:------------:|:---------------------------------------------:|:--------------------------------------------------------------------------------:|:----------------------:|:-----------:|
| Interpolation            | Linear       | Linear                                        | Sinc (likely)                                                                    | 4-p Lin (?)            | 4-p Lin (?) |
| GM                       | Yes          | Yes                                           | Yes                                                                              | Firmware 1.20 or later | Yes         |
| GS                       | Yes          | Yes                                           | Yes                                                                              | Yes                    | Yes         |
| GM 2                     | No           | No                                            | Partial<sup>[[4]](#midi2-support)</sup>                                          | No                     | No          |
| XG                       | No           | No                                            | Bank select only                                                                 | No                     | No          |
| Parts                    | 16           | 16                                            | 16                                                                               | 16                     | 16          |
| Voices                   | 32           | 48 (+ 6<sup>[[2]](#weird-voice-count)</sup>)  | 256                                                                              | 24                     | 28          |
| Tones (Basic)            | 226          | 226                                           | 226                                                                              | 189                    | 226         |
| Tones (MT-32 Map)        | 0            | 0                                             | 0                                                                                | 128                    | 128         |
| Drum Kits                | 9            | 9                                             | 9                                                                                | 9                      | 9           |
| Sample Rate              | 22050hz      | 22050hz                                       | 44100hz                                                                          | 32000hz                | ~33100hz    |
| Resonant Low Pass Filter | No           | No                                            | No                                                                               | Yes                    | Yes         |
| Rate Limit               | None         | None                                          | None                                                                             | 31250 baud             | 31250 baud  |
| CC#91 Reverb             | No           | No                                            | Yes<sup>[[5]](#effects-note)</sup>                                               | Yes                    | Yes         |
| CC#93 Chorus             | No           | No                                            | Yes<sup>[[5]](#effects-note)</sup>                                               | Yes                    | Yes         |

---

<a name="why-pre-10"></a>

[1] Assuming MSGS stayed as is all the way until Windows 10 (while I *did* have Win7, I did not test there).

<a name="weird-voice-count"></a>

[2] As per Zumi's [MSGS clean-room impl doc](https://github.com/sloptainment/slopgs/blob/master/artifacts/SPEC.adoc#725-design-intent-behind-the-48-primary--6-reserve-pool-split), derived from reverse engineering.

<a name="native-mode-note"></a>

[3] Compatibility mode not mentioned as it mostly repeats the old synth, aside from these:

- Voice allocator seems to be different, as the MIDI I'll talk about later drops some notes *in the beginning*, which it realistically should not
- Sound output differs, for whatever reason, likely it being made for 44100hz

<a name="midi2-support"></a>

[4] Supported MIDI2 Events, as mentioned:

- Note On pitch 7.9 attribute
- Per-note pitch bend
- Registered per-note controllers: pitch 7.25, volume, pan
- Per-note management, including detach

<a name="effects-note"></a>

[5] As I have no Windows 11 Machine, I cannot test whether the reverb and chorus are CC-controllable or just system toggles.

#### SysEx Response

A SysEx, aka System Exclusive, is a special type of MIDI messages.
Each manufacturer has its own set of SysEx messages, alongside
the common ones that usually all have.

A System Exclusive message consists of bytes `F0 F7` acting as boundaries,
some data between them and a checksum just before the the closing byte.
Usually a SysEx has the following structure: `F0 vv dd dt cs F7`, where `vv` is vendor ID, `dd` is device ID, `dt` is any other data and `cs` is checksum.
Generally SysEx _must_ be at least **6** bytes long, and at least **11** bytes long for Roland SysEx.
Most of this section is borrowed from [here](#blog).

| Vendor ID | Device ID | Data | Name | Notes |
|:----------|:---------:|:-----|:----:|:------|
| `7E` (Universal Non-realtime) | `dd` | `06 01` | Identity Request | Doesn't require a checksum; Windows 11-only; Returns data about the synth |
| `7E` (Universal Non-realtime) | `dd` | `09 01` | GM System On | Doesn't require a checksum; Win11: Resets banking mode to GS |
| `7E` (Universal Non-realtime) | `dd` | `09 02` | GM System Off | Doesn't require a checksum; Win11: Resets the synth; Win10: GM System On |
| `7E` (Universal Non-realtime) | `dd` | `09 03` | GM2 System On | Doesn't require a checksum; Win11: Resets banking mode to GS; Win10: GM System On |
| `7F` (Universal Realtime) | `dd` | `04 01 .. vv` | Master Volume | `..` is ignored. Otherwise, self-explanatory |
| `7F` (Universal Realtime) | `dd` | `04 03 ll mm` | Master Fine Tuning | Due to [this](#effects-note) I cannot test how it actually works. |
| `7F` (Universal Realtime) | `dd` | `04 04 ll mm` | Master Coarse Tuning | Due to [this](#effects-note) I cannot test how it actually works. |
| `7F` (Universal Realtime) | `dd` | `04 05 ll mm` | Global Parameter Control | Due to [this](#effects-note) I cannot test how it actually works. |
| `41 42 12` (Roland) | `dd` | `40 00 7F 00` | GS Reset | Self-explanatory. Win11: Resets banking mode to GS |
| `41 42 12` (Roland) | `dd` | `40 1p 02 0x` | GS Set Channel For Part | Sets the input Part ID `p` to channel `x`. Note that Part 00 is Drums part. |
| `41 42 12` (Roland) | `dd` | `40 1p 15 0x` | GS Part is Rhythm | Any nonzero value `x` makes Part ID `p` a Rhythm part. Allows for multiple drum parts. MSGS supposedly supports more than 2. |
| `41 42 12` (Roland) | `dd` | `40 1p 40` | GS Scale Tuning | Tune adjust for the note scale of Part ID `p`. Ranges from -1 to +1 semitone in values from `00` to `7F` where 40 is no offset. Usually 12 bytes are sent, but the list can be terminated early by inserting an `80` before the end. |


---
<a name="blog"></a>
A lot of useful CC and other info on MSGS can be found
on [Zumi's MSGS blog](https://zumi.neocities.org/stuff/msgs/).

---

#### GS crash course

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
| 25   | Snare Roll       |
| 26   | Finger Snap      |
| 27   | High Q           |
| 28   | Slap             |
| 29   | Scratch Push     |
| 30   | Scratch Pull     |
| 31   | Stick            |
| 32   | Square Click     |
| 33   | Metronome Click  |
| 34   | Metronome Bell   |
| 82   | Shaker           |
| 83   | Jingle Bell      |
| 84   | Belltree         |
| 85   | Castanets        |
| 86   | Mute Surdo       |
| 87   | Open Surdo       |

Controllers:

| CC# | Purpose               | Short description                                                                                                          | MSGS Responds |
|:---:|:----------------------|:---------------------------------------------------------------------------------------------------------------------------|:--------------|
| 0   | Bank Select MSB       | The most significant byte of the bank                                                                                      | Yes           |
| 5   | Portamento time       | Controls the speed of portamento                                                                                           | No            |
| 32  | Bank Select LSB       | The least significant byte of the bank                                                                                     | No            |
| 65  | Portamento            | Whether is portamento on. 0\~63: Off, 64\~127: On                                                                          | No            |
| 66  | Sostenuto             | Like hold pedal, but only sustains notes that already were on                                                              | No            |
| 67  | Soft Pedal            | Softens the notes, as in applies a slight lowpass filter                                                                   | No            |
| 84  | Portamento Control    | Specifies the note to glide from for the next note when set                                                                | No            |
| 91  | Reverb Send Level     | Specifies how loud should sound sent to reverb unit be                                                                     | No            |
| 93  | Chorus Send Level     | Specifies how loud should sound sent to chorus unit be                                                                     | No            |
| 94  | Delay Send Level      | Specifies how loud should sound sent to delay unit be                                                                      | No            |
| 98  | NRPN LSB              | Sets the NRPN LSB number to send data to. Sent after NRPN MSB                                                              | No            |
| 99  | NRPN MSB              | Sets the NRPN MSB number to send data to. Sent before NRPN LSB                                                             | No            |
| 120 | All Sounds Off        | Cuts all sounds, regardless of whether are they held by CC#64 or CC#65 on specified channel                                | Yes           |
| 121 | Reset All Controllers | Resets following controls: Pitchbend, PolyKeyPress, ChannelPress, Mod wheel, Expression, Hold, Portamento, Sostenuto, Soft | Yes           |
| 123 | All Notes Off         | Turns all notes off unless held by CC#64 Sustain Pedal or CC#65 Sostenuto                                                  | Yes           |
| 126 | Channel Mono          | Cuts all sound on a channel and sets the polyphony to CC value                                                             | As Poly       |
| 127 | Channel Poly          | Cuts all sound on a channel and resets it to polyphonic mode                                                               | As Poly       |

| RPN# | Purpose               | Short description                                                                                                          | MSGS Responds |
|:----:|:----------------------|:---------------------------------------------------------------------------------------------------------------------------|:--------------|
| 0000 | Pitch Bend Range      | Pitch bend range. Most devices cap at 24, while MSGS allows for up to 48.                                                  | Yes           |
| 0001 | Fine Tune             | Channel fine tune within +-1 semitone. 8192 (`2000h`) = no detune.                                                         | Yes           |
| 0002 | Coarse Tune           | Channel coarse tune within +-64 semitones. 64 (`0040h`) = no detune.                                                       | Yes           |

MSGS ignores most of these (a software synthesizer built to be
fast and cheap with an acceptable sound quality, after all).
Also, MSGS accepts all of these apart from Bank controls even when in GM mode,
including the extra percussion always being available.

---

#### Notes

<a name="msgs"></a>
[1] [A Japanese Wikipedia article about MSGS](https://ja.wikipedia.org/wiki/Microsoft_GS_Wavetable_SW_Synth) and [DirectMusic Synthesizer](https://ja.wikipedia.org/wiki/Microsoft_Synthesizer)

---

## Quirks

Despite stemming from SC-55, MSGS gained its own quirks.

General:
 - A channel cannot have 2 instances of the same note. A new note cuts the previous one.
   SC-55 applies this only to drum channels.
 - Whole ass 48 semitone pitch bend range! (Why though?)
 - No effects of any kind, apart from Windows 11

Windows 98...XP:
 - A channel cannot have 2 different patches sounding
 - All Sounds Off instead releases notes while ignoring pedals
 - Slower to response in general
 - Sounds as if it was EQ'd

Windows 10+:
 - A channel can have 2 different patches sounding under the following conditions:
   - A channel has another note sounding
   - A program change happened
   - A new note after a program change is struck
 
 This also allows the channel to have 2 instances of the same note, although both share the note-off event.
 - All Sounds Off cuts off all sound on a channel
 - Faster to response
 - Flat sound

---
## Why?

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

Here are MSGS renders of that Crystal Oscillator cover on different systems:

- [Windows 11](/tests/msgs_11.ogg)
- [Windows 10](/tests/msgs_10.ogg)
- [Windows XP](/tests/msgs_xp.ogg) (outdated, replacement pending)
- [Windows 98](/tests/msgs_98.ogg)

I could not be bothered to re-render the Windows XP version, so I asked a friend to do it, so the render can be replaced anytime soon.

And fun fact: WinXP shares the behavior with Windows 98 MSGS (which I did test too).

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

## Credits

- [nnonick](https://github.com/nnonickreal) for some Windows XP testing & upcoming Windows XP recordings, and upcoming Windows Vista tests.
- [Zumi](https://github.com/ZoomTen) for [clean-room reimplementation](https://github.com/sloptainment/slopgs) of Windows XP MSGS & documenting how it works, and kickstarting this document.
- [Abstract64](https://www.youtube.com/@64abstract), [Kot](https://www.youtube.com/@kot_bruhman) and
  [HueArme](https://soundcloud.com/user-416698216-971657402) for making me interested in the synth in the first place.
- YOU, for reading this.
