# tg100_re

Here are scripts n stuff that I'll use for tearing apart
TG100 program ROM as it seems like people only did that
with SC-55, which I feel is very unfair.

# About the TG100 itself

## Basic info

TG100 was an answer from Yamaha to Roland's SC-55.
AFAIK it was the first GM sound module of theirs.

TG100 supports GM and nothing else, while the first
iteration of SC-55 only and already supported Roland's
own "GS" mode which is an extension of GM, GM itself
arrived in later firmware version. Yamaha will eventually
come up with their own XG extension to GM in their MU line
of modules and various other synths, but that's already
out of scope.

## The guts

TG100 runs an H8/500 from Hitaachi and the sound is produced
with Yamaha's YMW258-F aka MultiPCM which you already might
have met when working with chiptune or if you looked at
Sega Model 2 arcades, early versions of which used MultiPCM
before they switched to SCSP.

YMW258-F is a 28-voice sampler, which supports 8- or 12-bit
linear PCM, the latter is in which the entire Wave ROM of TG100
is encoded in. That chip is also predecessor to OPL4's sample
part, which is 24 voices instead and also supports 16-bit PCM
alongside a couple more features.

Thats avout it, the chip doesn't have much interesting stuff,
its just a sampler with hardware envelopes and Yamaha's signature
non-linear volume curve.

It also has a very interesting "Level Direct" feature.
The entire purpose of this bit is that when it is set,
the volume level ia applied to a voice directly, otherwise
it is smoothly ramped from current to target.

A similar feature is introduced in YM2164 "OPP", a
little-known successor to YM2151 "OPM", and YM2414 "OPZ"
and YM2424 "OPZ2", which are also not that widely known
and are successors to OPP.
The feature is called "TL Ramp", and it functions exactly
the same, except for the fact that it also has controllable
speed instead of just being on-off.

Thats about all the info I have on this odd piece of hardware.