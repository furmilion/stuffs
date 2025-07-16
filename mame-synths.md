My opinion on MAME's emulation of synths:

Version: 0.277b

Table of Contents:
- [Yamaha](#yamaha)
	- [A](#ym_a)
	- [MUx](#ym_mu)
	- [D](#ym_d)
		- [DXx](#ym_dx)
	- [P](#ym_p)
		- [PSR](#ym_psr)
		- [PSS](#ym_pss)
	- [Q](#ym_q)
	- [R](#ym_R)
	- [S](#ym_s)
	- [T](#ym_t)
	- [VLx](#ym_vl)
- [Roland](#rlnd)
	- [Alpha Juno](#rlnd_ajuno)
	- [Boss](#rlnd_boss)
	- [CM32x](#rlnd_cm32)
	- [D-x](#rlnd_d)
	- [G](#rlnd_g)
	- [JD-800](#rlnd_jd)
	- [Juno](#rlnd_juno)
	- [JV](#rlnd_jv)
	- [JX](#rlnd_jx)
	- [MC](#rlnd_mc)
	- [MKS](#rlnd_mks)
	- [MT](#rlnd_mt)
	- [R-8](#rlnd_r8)
	- [R](#rlnd_r)
	- [S-x](#rlnd_s)
	- [Sound Canvas](#rlnd_sc)
	- [TB-303](#rlnd_tb303)
	- [TR](#rlnd_tr)
- [Korg](#korg)
	- [707](#korg_707)
	- [D](#korg_d)
	- [microKORG](#korg_mkorg)
	- [PolyX](#korg_poly)
	- [WaveStation](#korg_ws)
	- [Z3](#korg_z3)
- [Akai](#akai)
	- [A](#akai_a)
	- [MPC](#akai_mpc)
	- [V](#akai_v)
- [Casio](#casio)
	- [CZ](#casio_cz)
- [E-MU](#emu)
	- [Emax](#emu_emax)
	- [Emulator](#emu_lator)
- [Ensoniq](#ensq)
- [Kawai](#kwi)

<a name="yamaha"></a>
## YAMAHA

<a name="ym_a"></a>
- AN1x Control Synthesizer [an1x]
    - No `xn668a00.bin` `xt113b00.ic9` `xt113b00.ic1` roms [[7]](#note7)
<a name="ym_d"></a>
- DD-9 Digital Percussion [dd9]
    - Overall: works
    - Sound: yes
    - Graphics: yes
<a name="ym_dx"></a>
- DX7 [dx7]
    - Overall: not working [[9]](#note9)
    - Sound: ???
    - Graphics: yes
- DX9 [dx9]
    - Overall: works
    - Sound: unimplemented
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- DX11 [dx11]
    - Overall: not working
    - Sound: ??? [[10]](#note10)
    - Graphics: yes
- DX100 [dx100]
    - Overall: works
    - Sound: yes [[8]](#note8)
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
<a name="ym_f"></a>
- FB-01 FM Sound Generator [fb01]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - Available options: `-midiin`
<a name="ym_mu"></a>
- MU5 [mu5]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- MU10 [mu10]
    - Overall: works
    - Sound: yes [[1]](#note1) [[2]](#note2)
    - Graphics: no screen
    - Available options: `-midiin`, `-midiout`
- MU15 [mu15]
    - No `xv684c0.bin` rom [[7]](#note7)
    - Available options: `-midiin`, `-midiout`
- MU50 [mu50]
    - Overall: works
    - Sound: yes [[3]](#note2) [[2]](#note2)
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
- MU80 [mu80]
    - Overall: works
    - Sound: no (nor did 0.265 have any)
    - Graphics: yes [[4]](#note4)
    - Available options: `-midiout`
- MU90 [mu90]
    - Overall: works
    - Sound: yes [[5]](#note5)
    - Graphics: yes
    - Available options: `-midiout`
    - MU90B [mu90b]: no `xt040c0.ic9` rom[[7]](#note7), assumed identical to master
- MU100 [mu100]
    - Overall: works
    - Sound: yes [[5]](#note5)
    - Graphics: yes
    - Available options: `-midiout`
    - Notes: complex enough to not be able to run at 100% speed most of the time
    - MU100B (Screenless) [mu100b]: No `xu50710.bin` `sx518b0.ic34` `sx743b0.ic35` roms[[7]](#note7), assumed identical to master
    - MU100R (Rack) [mu100r]: Identical to master

- MU128 [mu128]
    - Overall: not working (stuck on "Checking PLG" screen)
    - Graphics: yes [[6]](#note6)
    - Sound: ??? [[5]](#note5)
    - Available options: `-midiout`
- MU500 [mu500]
    - No `xv364a0.ic49` `xv365a0.ic50` `xw848a0.ic53` `xw849a0.ic54` roms [[7]](#note7)
	- MU1000 [mu1000]: no `mu1000-v2.01-h.bin` `mu1000-v2.01-l.bin` roms[[7]](#note7), assumed identical to master
	- MU2000 [mu2000]: no `mu2000-v2.01-h.bin` `mu2000-v2.01-l.bin` roms[[7]](#note7), assumed identical to master
<a name="ym_p"></a>
- PCS-30 [pcs30]
    - Overall: not working
    - Sound: ???
    - Graphics: no screen
- PS-400 [ps400]
    - Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="ym_psr"></a>
- PSR-11 [psr11]
    - Overall: works
    - Sound: very yes
    - Graphics: yes
- PSR-16 [psr16]
    - Overall: not working [[10]](#note10)
    - Sound: ???
    - Graphics: no screen
- PSR-36 [psr36]
    - Overall: not working [[10]](#note10)
    - Sound: ???
    - Graphics: no screen
- PSR-40 [psr40]
    - Overall: not working [[10]](#note10)
    - Sound: ???
    - Graphics: no screen
- PSR-60 [psr60]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - Available options: `-midiin`, `-midiout`
    - PSR-70 [psr70]: identical to master
- PSR-79 [psr79]
    - Overall: not working [[10]](#note10)
    - Sound: ???
    - Graphics: yes
- PSR-150 [psr150]
    - Overall: works
    - Sound: very yes
    - Graphics: yes
    - PSR-75 [psr75]: identical to master
    - PSS-11 [pss11]: no `xl437a00.ic4` rom[[7]](#note7), assumed identical to master
    - PSS-21 [pss21]: no `xl437a00.ic4` rom[[7]](#note7), assumed identical to master
    - PSS-31 [pss31]: no `xl437a00.ic4` rom[[7]](#note7), assumed identical to master
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
    - No `xr951a0.ic1` `ks0066_f05.bin` roms[[7]](#note7)
- PSR-500 [psr500]
    - Overall: not working [[10]](#note10)
    - Sound: ???
    - Graphics: no screen
- PSR-540 [psr540]
    - No `xr951a0.ic1` rom [[7]](#note7)
	- No `psr540-lcd.svg`
- PSR-2000 [pss2000]
    - Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
    - Available options: `-midiin`, `-midiout`
<a name="ym_pss"></a>
- PSS-12 [pss12]
    - Overall: works
    - Sound: yes
    - Graphics: yes
    - PSS-6 [pss6]: identical to master
- PSS-480/580 [pss480]
    - Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- PSS-680 [pss680]
    - Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
	- PSS-780 [pss780]: identical to master
<a name="ym_q"></a>
- QS300 [qs300]
	- No `xq055e0.ic04` `xq320e0.ic24` `xq056e0.ic09` `xq057c0.ic10` `xq058c0.ic11` `t6963c_0101.bin` roms [[7]](#note7)
	- EOS B900: no roms[[7]](#note7), assumed identical to master
- QY70 Music Sequencer [qy70]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes
	- Available options: `-midiout`
<a name="ym_r"></a>
- RX15 Digital Rhythm Programmer [rx15]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes
<a name="ym_s"></a>
- SY35 Music Synthesizer [sy35]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="ym_t"></a>
- TG100 [tg100]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- TX81Z FM Tone Generator [tx81z]
	- Overall: works
	- Sound: very yes
	- Graphics: yes
<a name="ym_vl"></a>
- VL1 [vl1]
	- Overall: not working[[10]](#note10)
	- Sound: ???
	- Graphics: yes
- VL70-m [vl70]
	- Overall: works
	- Sound: unimplemented
	- Graphics: yes[[4]](#note4)
	- Available options: `-midiout`
	
<a name="rlnd"></a>
## ROLAND

<a name="rlnd_ajuno"></a>
- Alpha Juno 1 Programmable Polyphonic Synthesizer [ajuno1]
	- Overall: works
	- Sound: ??? [[10]](#note10)
	- Graphics: yes
- Alpha Juno 2 Programmable Polyphonic Synthesizer [ajuno2]
	- Overall: works
	- Sound: ??? [[10]](#note10)
	- Graphics: yes
	- HS80 [hs80]: no roms[[7]](#note7), assumed identical to master
<a name="rlnd_boss"></a>
- Boss GX-700 Guitar Effects Processor [gx700]
- Boss SE-70 Super Effects Processor [se70]
- Boss SX-700 Studio Effects Processor [sc700]
	- Overall: not working
	- Sound: ??? [[11]](#note11)
	- Graphics: no screen

<a name="rlnd_cm32"></a>
- CM-32L [cm32l]
- CM-32P [cm32p]
	- Overall: works
	- Sound: ??? [[10]](#note10) [[12]](#note12)
	- Graphics: yes

<a name="rlnd_d"></a>
- D-10 Multi Timbral Linear Synthesizer [d10]
	- Overall: works
	- Sound: ??? [[10]](#note10)
	- Graphics: yes
	- D-110 Multi Timbral Sound Module [d110]: no `d-110.v1.10.ic19.bin` `r15179873-lh5310-97.ic12.bin` `r15179878.ic7.bin` `r15179880.ic8.bin` `r15179879.ic6.bin` roms[[7]](#note7), assumed identical to master
- D-50 Linear Synthesizer (2.xx) [d50]
	- No `d78312g-022_15179266.ic25` rom [[7]](#note7)
	- D-50 Linear Synthesizer (1.xx) [d50o]: no `roland__1-11__2-1-96_greg.v1.10.ic22` `d78312g-017_15179261.ic25` `roland_a__r15179835_8710eai__tc532000p-7469.ic30` `roland_b__r15179836_8710eai__tc532000p-7470.ic29` roms[[7]](#note7), assumed identical to master
	- D-550 Linear Synthesizer [d550]: no `roland_d-550_v1.02_eprom_firmware.ic22` rom[[7]](#note7), assumed identical to master
- D-70 Super LA Synthesizer [d70]
	- No `roland_d70_v1.19_a_even.ic4` `roland_d70_v1.19_b_odd.ic9` roms [[7]](#note7)
<a name="rlnd_g"></a>
- GR-700 Guitar Synthesizer [gr700]
	- No `m5l8048-067p_b4d4.ic1` rom [[7]](#note7)
<a name="rlnd_jd"></a>
- JD-800 Programmable Synthesizer [jd800]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="rlnd_juno"></a>
- Juno-6 (JU-6) Polyphonic Synthesizer [juno6]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- Juno-106 Programmable Polyphonic Synthesizer [juno106]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="rlnd_jv"></a>
- JV-880 Multi Timbral Synthesizer Module [jv880]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="rlnd_jx"></a>
- JX-3P Programmable Preset Polyphonic Synthesizer
	- No roms [[7]](#note7)
- JX-8P Polyphonic Synthesizer (3.x) [jx8p]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
	- JX-8P Polyphonic Synthesizer (2.x) [jx8po]: no `jx8p-a-v21.ic6` `upd7537-014_15179201.ic1` roms[[7]](#note7), assumed identical to master
- JX-10 Super JX Polyphonic Synthesizer [jx10]
	- No `jx-10_a2_3.ic6` `upd7538a-013_15179240.ic3` `jx-10_b2_1.ic1` `jx-10_c2_1.ic1` roms [[7]](#note7)
	- MKS-70 Super JX Polyphonic Synthesizer [mks70]: no `mks70_v108-a.ic6` `b-v103.ic1` `c-v103.ic1` roms[[7]](#note7), assumed identical to master
<a name="rlnd_mc"></a>
- MC-50 Micro Composer [mc50]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- MC-50mkII Micro Composer [mc50mk2]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- MC-300 Micro Composer [mc300]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="rlnd_mks"></a>
- MKS-7 Super Quartet [mks7]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- MKS-30 Planet-S MIDI Module [mks30]
	- No `m5l8048-067p_b4d4.ic1` rom [[7]](#note7)
- MKS-50 Synthesizer Module [mks50]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes
<a name="rlnd_mt"></a>
- MT-32 [mt32]
	- See [CM-32L/CM-32P](#roland_cm32)
- MT-80s Music Player [mt80s]
	- No `mt80s_101.ic4` `mb838000.ic7` roms [[7]](#note7)
- MT-100 [mt100]
	- No `mt32_2.0.3.ic28` `r15449121.ic37.bin` `r15179917.ic13.bin` `mt100_4.0.0.bin` roms [[7]](#note7)
- PR-100 Digital Sequencer (2.02) [pr100]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
	- PR-100 Digital Sequencer (2.01) [pr100_201]: no `pr100-201_mbm27c512-20.ic10` rom[[7]](#note7), assumed identical to master
<a name="rlnd_r8"></a>
- R-8 Human Rhythm Composer (2.02) [r8]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
	- R-8M Total Percussion Sound Module (1.04) [r8m]: identical to master
- R-8 Mk II Human Rhythm Composer [r8mk2]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
<a name="rlnd_r"></a>
- RA-30 Realtime Arranger [ra30]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- RD-500 Digital Piano [rd500]
	- No `rd500_rom.bin` `roland-a_r00342978.ic4` `roland-b_r00343012.ic5` `roland-c_r00343023.ic6` `roland-d_r00343034.ic7` roms [[7]](#note7)

[Music Style Cards are skipped over]

<a name="rlnd_s"></a>
- S-10 Digital Sampling Keyboard [s10]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes
	- MKS-100 Digital Sampler [mks100]: no `roland_mks-100_v1.04_ic26.bin` rom[[7]](#note7), assumed identical to master
- S-50 Digital Sampling Keyboard
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes
	- S-550 Digital Sampler [s550]: no `s-550_2-0-0.ic6` `s-550_2-0-0.ic3` `upd7537c-014_15179201.ic35` roms[[7]](#note7), assumed identical to master
- S-220 Digital Sampler [s220]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes
<a name="rlnd_sc"></a>
- Sound Canvas SC-55 [sc55]
	- No `roland_r15199778_6435328a97f.ic30` rom [[7]](#note7)
	- Sound Canvas SC-155 [sc155]: no `roland_r15199799.ic30` `roland_r15209361.ic15` roms [[7]](#note7), assumed identical to master
	- Sound Canvas CM300 [cm300]: no `roland_r15199774.ic6` `roland_r15279812.ic8` `roland_r15279806.ic2` `roland_r15279807.ic3` `roland_r15279808.ic4` `roland_r15239182.ic2` roms[[7]](#note7), assumed identical to master
- Sound Canvas SC-55mkII [sc55mk2]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- SoundCanvas SC-88VL [sc88vl]
	- No `roland_sc88_vl-1.04.ic29` `roland-r00232667-m38881m2-150gp.ic23` `roland-r00785356-hn624316fbc25.ic10` `roland-r00785367-hn624316fbc26.ic7` `roland-r00788489-hn624316fbc27.ic4` `roland-r00788490-hn624316fbc28.ic2` roms [[7]](#note7)
<a name="rlnd_tb303"></a>
- TB-303 Bass Line [tb303]
	- Overall: works
	- Sound: unimplemented
	- Graphics: broken
<a name="rlnd_tr"></a>
- TR-505 Rhythm Composer [tr505]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- TR-606 Drumatix [tr606]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- TR-707 Rhythm Composer [tr707]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- TR-727 Rhythm Composer [tr727]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- TR-808 Rhythm Composer [tr808]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- TR-909 Rhythm Composer [tr909]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- U-20 RS-PCM Keyboard [u20]
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- U-220 RS-PCM Sound Module
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: no screen
- W-30 Music Workstation
	- Overall: not working [[10]](#note10)
	- Sound: ???
	- Graphics: yes

<a name="korg"></a>
## KORG

<a name="korg_707"></a>
- 707 Performing Synthesizer [korg707]
	- No `870904.ic7` rom [[7]](#note7)
<a name="korg_d"></a>
- DS-8 Digital Synthesizer [ds8]
	- No `870214.ic9` rom [[7]](#note7)
- DSS-1 Digital Sampling Synthesizer [dss1]
	- No `860336.ic19` `860436.ic18` `860536.ic12` `860236.ic15` roms [[7]](#note7)
- DVP-1 Digital Voice Processor [dvp1]
	- No `850803.ic6` `tms320m10nl.ic9` `tms320m10nl.ic8` roms [[7]](#note7)
- DW-8000 Programmable Digital Waveform Synthesizer [dw8000]
	- No `dw8000-v0713.ic38` `hn613256p-t70_32004086.ic46` `hn613256p-t71_32004087.ic45` `hn613256p-cb4_32004088.ic44` `hn613256p-cb5_32004089.ic43` roms [[7]](#note7)
- DW-8000-EX Programmable Digital Waveform Synthesizer [dw8000ex]
	- No `korg-dw8000-ex.bin` `exp-1.bin` `exp-2.bin` `exp-3.bin` `exp-4.bin` roms [[7]](#note7)

<a name="korg_m1"></a>
- M1 Music Workstation (Rev. 19) [korgm1]
	- No `rev19-ic23-880219.bin` `rev19-ic32-880319.bin` `mb83512-15p-259.ic30` `upd23c512-039.ic26` `upd23c512-039.ic20` roms [[7]](#note7)
	- M1 EX Music Workstation (1.29) [korgm1ex]: no `v. 1.29 27c512 hi ic23.bin` `v. 1.29 27c512 lo ic32.bin` roms[[7]](#note7)
	- M1R Music Workstation (1.06) [korgm1r]: no `880506_ic23 high _27c512_ m1r.bin` `880606_ic32 low _27c512_ m1r.bin` roms[[7]](#note7)
	- M1R EX Music Workstation (1.12) [korgm1rex]: no `880512 _ic23 high _27c512_ m1rex.bin` `880612 _ic32 low _27c512_ m1rex.bin` roms[[7]](#note7)
<a name="korg_mkorg"></a>
- microKORG Synthesizer/Vocoder [microkorg]
	- No `korg_microkorg_v1.03_29lv800b.ic20` rom [[7]](#note7)
<a name="korg_poly"></a>
- Poly-61 Programmable Polyphonic Synthesizer [poly61]
	- No `d8049c-337.bin` `d8049c-384.bin` roms [[7]](#note7)
- Poly-800 Programmable Polyphonic Synthesizer [poly800]
	- No `830236.ic22` rom [[7]](#note7)
- Poly-800 Programmable Polyphonic Synthesizer (MIDI Dump Kit) [poly800mdk]
	- No `mdk.ic22` rom [[7]](#note7)
- Poly-800II Programmable Polyphonic Synthesizer [poly800ii]
	- No `851005.ic24` roms [[7]](#note7)
- Polysix Programmable Polyphonic Synthesizer [polysix]
	- No `d8048c-345.bin` `d8049c-217.bin` `nvram.bin` roms [[7]](#note7)
<a name="korg_ws"></a>
- WaveStation A/D [korgwsad]
	- No `wsad_1p25_910205l.ic41` `wsad_1p25_910305r.ic40` `m37450m4-233fp.bin` roms [[7]](#note7)
- WaveStation EX [korgwsex]
	- No `wsex_319_u18.bin` `wsex_319_u19.bin` `m37450m4-233fp.ic34` `ws3p7.bin` `ws3p8.bin` `ws3p9.bin` `ws4p0.bin` roms [[7]](#note7)
- WaveStation SR [korgwssr]
	- No `920305.ic22` `920405.ic23` `m37450m4-233fp.bin` roms [[7]](#note7)
<a name="korg_z3"></a>
- Z3 Guitar Synthesizer [korgz3]
	- No `881405.ic5` `881505.ic4` `881605.ic13` roms [[7]](#note7)

<a name="akai"></a>
## AKAI

<a name="akai_a"></a>
- AX80 [ax80]
	- No `akai ax80 main cpu mask rom.ic2` `ax-80k.ic4` roms [[7]](#note7)
<a name="akai_mpc"></a>
- MPC-3000 [mpc3000]
    - No `mpc312ls.bin` `mpc312ms.bin` `mp3000__op_v1.0.am27c256__id0110.ic602.bin` roms [[7]](#note7)
- MPC60 MIDI Production Center
	- No `mp6cpu2.ic2` `mp6cpu3.ic3` `mp6cpu1.ic4` `mpc6cpu4.ic5` `mpc60_voice_1_v1-0.ic17` `mpc60_voice_2_v1-0.ic18` `upd78c11g-044-36.ic1` `akai mpc60 panel eprom op v1-1 2764.ic2` roms [[7]](#note7)
<a name="akai_v"></a>
- VX600 Programmable Matrix Synthesizer [vx600]
	- No `vx600_-1-_v1.2.ic45` `upd78c11g-044-36.ic46` `vx600_-2-_v1.12.ic47` roms [[7]](#note7)

<a name="casio"></a>
## CASIO
<a name="cazio_cz"></a>
- CZ-1 [cz1]
	- No `upd27c256c-20a154.bin` `init_main.bin` `upd23c128ec-036.bin` `init_sub.bin` `upd8049hc-672.bin` roms [[7]](#note7)
	- Available options: `-midiin`
	- MZ-1 (Prototype) [mz1]: no roms [[7]](#note7)

<a name="emu"></a>
## E-MU
<a name="emu_emax"></a>
	- Emax Digital Sampling Keyboard [emax]
		- No `emax.bin` `im368-1_ba__r1129-11.ic7` `ip345c.bin` roms [[7]](#note7)
		- Emax Plus Digital Sampling Keyboard [emaxp]: no `ip424a3089.bin` `ip379a.bin` roms [[7]](#note7)
	- Emax II 16-bit Digital Sound System [emax2]
		- No `ip43aemu_3891.ic20` `ip43bemu_4291.ic19` `93c06n.ic24` roms [[7]](#note7)
<a name="emu_lator"></a>
	- Emulator II [emu2]
		- No `e2newermain_hdmb2_3_main.ic42` `eiiscanv2-1.ic28` `eiiscanv3-1.ic28` `74s472.ic137` `74s472.ic135` roms [[7]](#note7)
	- Emulator Three Digital Sound Production System [emu3]
		- No `e3-lsboot_ip381a_emu_systems_4088.ic3` `e3-msboot_ip380a_emu_systems_4088.ic4` `im368.ic31` roms [[7]](#note7)

<a name="ensq"></a>
## ENSONIQ

Empty for now.

<a name="kwi"></a>
## KAWAI

Empty for now.


<a name="note1"></a>
[1] It actually sounds way more elaborate than I expected it to, considering I tested it with a midi that targets MU50, it still doesn't support some controllers tho
~~I honestly find it weird that it supports Variation effct while not going for ADR controls~~ Seems like a MIDI issue on my side, but I dont remember that happening in 0.265. MU10 specific: Sound now actually works conpared to 0.265

<a name="note2"></a>
[2] It absolutely breaks with high cutoff, the noise is all over the place

<a name="note3"></a>
[3] Generally sounds different from 0.265, the Variation and Chorus sound a LOT weaker, Reverb is way stronger. I cannot test now though as 0.265 seems to be breaking itself and not detecting MU50 roms when ther are present, which is partially a reason I updated

<a name="note4"></a>
[4] Contrast not emulated

<a name="note5"></a>
[5] Seems to completely lack the effect unit emulation

<a name="note6"></a>
[6] I have no idea if contrast is emulated since the system gets stuck

<a name="note7"></a>
[7] I have no idea if I can get them myself since I remember the MAME merged rom archive getting locked out for download from unregistered users

<a name="note8"></a>
[8] I assume there is something wrong with patch loading as most of them have a deep lfo that they probably should not have

<a name="note9"></a>
[9] States that the battery needs changing

<a name="note10"></a>
[10] No midi in option to test sound

<a name="note11"></a>
[11] No way to input sound to test

<a name="note12"></a>
[12] CM-32P: no cart images to test, but apparently there is some sound (Fretless Bass @ E-5)