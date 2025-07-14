My opinion on MAME's emulation of synths:

Version: 0.277b

## YAMAHA
- MU5
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- MU10
    - Overall: works
    - Sound: yes[1][2]
    - Graphics: no screen
    - Available options: `-midiin`, `-midiout`
- MU15
    - I forgor I have no roms for it[7]
    - Available options: `-midiin`, `-midiout`
- MU50
    - Overall: works
    - Sound: yes[3][2]
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- MU80
    - Overall: works
    - Sound: no (nor did 0.265 have any)
    - Graphics: yes[4]
    - Available options: `-midiout`
- MU90
    - Overall: works
    - Sound: yes[5]
    - Graphics: yes
    - Available options: `-midiout`
    - MU90B: No roms[7], assumed identical to master
- MU100
    - Overall: works
    - Sound: yes[5]
    - Graphics: yes
    - Available options: `-midiout`
    - Notes: complex enough to not be able to run at 100% speed most of the time
    - MU100B (Screenless): No roms[7] but im pretty sure its identical to master
    - MU100R (Rack): Identical to master

- MU128
    - Overall: not working (stuck on "Checking PLG" screen)
    - Graphics: yes[6]
    - Sound: ???[5]
    - Available options: `-midiout`
- MU500
    - No roms[7]
- MU1000
    - No roms[7]
- MU2000
    - No roms[7]
- AN1x Control Synthesizer [an1x]
    - No roms[7]
- FB-01 FM Sound Generator [fb01]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - Available options: `-midiin`
- DD-9 Digital Percussion [dd9]
    - Overall: works
    - Sound: yes
    - Graphics: yes
- DX7
    - Overall: not working[9]
    - Sound: ???
    - Graphics: yes
- DX9
    - Overall: works
    - Sound: unimplemented
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- DX11
    - Overall: ???
    - Sound: ???
    - Graphics: yes
- DX100
    - Overall: works
    - Sound: yes[8]
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- PCS-30 [pcs30]
    - Overall: ???
    - Sound: ???
    - Graphics: no screen
- PSR-11 [psr11]
    - Overall: works
    - Sound: very yes
    - Graphics: yes
- PSR-16 [psr16]
    - Overall: ???
    - Sound: ???
    - Graphics: no screen
- PSR-36 [psr36]
    - Overall: ???
    - Sound: ???
    - Graphics: no screen
- PSR-40 [psr40]
    - Overall: ???
    - Sound: ???
    - Graphics: no screen
- PSR-60 [psr60]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
    - PSR-70 [psr70]: identical to master
- PSR-79 [psr79]
    - Overall: ???
    - Sound: unimplemented
    - Graphics: yes
- PSR-150 [psr150]
    - Overall: works
    - Sound: very yes
    - Graphics: yes
    - PSR-75 [psr75]: identical to master
- PSR-180 [psr180]
    - Overall: works
    - Sound: very yes
    - Graphics: yes
    - PSR-76 [psr76]: identical to master
- PSR-190 [psr190]
    - Overall: works
    - Sound: very yes
    - Graphics: yes
    - PSR-78 [psr78]: identical to master
- PSR-260 [psr260]
    - Overall: works
    - Sound: unimplemented
    - Graphics: yes
- PSR-340 [psr340]
    - no roms[7]
- PSR-500 [psr500]
    - Overall: ???
    - Sound: ???
    - Graphics: no screen
- PSR-540 [psr540]
    - no roms[7]
    - Available options: `-midiin`, `-midiout`
- PSS-12 [pss12]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - PSS-6 [pss6]: identical to master

[1] It actually sounds way more elaborate than I expected it to, considering I tested it with a midi that targets MU50, it still doesn't support some controllers tho
~~I honestly find it weird that it supports Variation effct while not going for ADR controls~~ Seems like a MIDI issue on my side, but I dont remember that happening in 0.265. MU10 specific: Sound now actually works conpared to 0.265
[2] It absolutely breaks with high cutoff, the noise is all over the place
[3] Generally sounds different from 0.265, the Variation and Chorus sound a LOT weaker, Reverb is way stronger. I cannot test now though as 0.265 seems to be breaking itself and not detecting MU50 roms when ther are present, which is partially a reason I updated
[4] Contrast not emulated
[5] Seems to completely lack the effect unit emulation
[6] I have no idea if contrast is emulated since the system gets stuck
[7] I have no idea if I can get them myself since I remember the MAME merged rom archive getting locked out for download from unregistered users
[8] I assume there is something wrong with patch loading as most of them have a deep lfo that they probably should not have
[9] States that the battery needs changing
