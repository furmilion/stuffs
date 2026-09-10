import struct

def note_from_key(key: int = 0):
    octave = key//12
    notes = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
    notes_neg = ["c_", "c+", "d_", "d+", "e_", "f_", "f+", "g_", "g+", "a_", "a+", "b_"]
    if key >= 0:
        while key > 11:
            key -= 12
        return notes[key] + str(octave)
    elif key < 0:
        while key < 0:
            key += 12
        return notes_neg[key] + str(-octave)
        
def parseCard(card=None, dumpSamples=False):
    insts = []
    headerSize = 0
    if not card:
        print("No card supplied!")
        return

    print("########### SWAYED Wavecard Viewer")
    file = open(card, "rb"); fread = file.read; fseek = file.seek; ftell = file.tell
    
    if fread(8) != b"SWAYSROM":
        print("Not a SWAYED wavecard!")
    headerSize += 8
    
    cardID = struct.unpack("<H",fread(2))[0]
    headerSize += 2
    cardName = fread(struct.unpack("<H",fread(2))[0]).decode()
    headerSize += 2 + len(cardName)
    instDefs = struct.unpack("<H",fread(2))[0]
    headerSize += 2

    for _ in range(instDefs):
        #print(ftell())
        instName    = fread(struct.unpack("<H",fread(2))[0]).decode()
        headerSize += 2 + len(instName)
        instSamples = struct.unpack("<B",fread(1))[0]
        headerSize += 1
        sampleDefs = []
        for __ in range(instSamples):
            sampleDefs.append({
                "unk1": struct.unpack("<B",fread(1))[0], # unknown parameters, no audible changes
                "unk2": struct.unpack("<B",fread(1))[0], 
                "unk3": struct.unpack("<B",fread(1))[0], 
                "unk4": struct.unpack("<B",fread(1))[0], 
                "fine": struct.unpack("<H",fread(2))[0], # fine tune up, ~103 cents when full
                "coar": struct.unpack("<B",fread(1))[0], # coarse tune, no idea how it works yet but it does work as intended
                "pbck": struct.unpack("<B",fread(1))[0], # playback related stuff, no idea how it works but it only plays if the value is 0x40
                "attn": struct.unpack("<B",fread(1))[0], # nonlinear attenuation, no effect if >= 0x80
                "ptc1": struct.unpack("<B",fread(1))[0], # coarser tune up???? ~350 cents when full
                "ptc2": struct.unpack("<B",fread(1))[0], # coarser than coarse tune???? ~3 semitones per value
                "root": struct.unpack("<B",fread(1))[0], # root key
                "high": struct.unpack("<B",fread(1))[0], # high key
                "mode": struct.unpack("<B",fread(1))[0], # playback mode
                "lpst": struct.unpack("<I",fread(4))[0], # loop start   | absolute offset in rom in samples
                "lpen": struct.unpack("<I",fread(4))[0], # loop end     | absolute offset in rom in samples
                "smst": struct.unpack("<I",fread(4))[0], # sample start | absolute offset in rom in samples
                "smen": struct.unpack("<I",fread(4))[0], # sample end   | absolute offset in rom in samples
            })
            headerSize += 0x1E
        #fseek(0x1E * instSamples, 1)
        insts.append([instName, instSamples, sampleDefs])
    
    print(
    f"Card:                 '{cardName}'\n"
    f"Unique ID:             {cardID} ({hex(cardID)})\n"
    f"ROM Offset:            {headerSize} ({hex(headerSize)})\n"
    f"Instruments defined:   {instDefs}\n"
    f"\n"
    )
    input()
    for inst in insts:
        print(
            f"\n####################################\n"
            f"{inst[0]}\n"
            f"Samples: {inst[1]}")
        for idx, smpl in enumerate(inst[2]):
            print(
            f"    # Sample {idx}:\n"
            f"        - Unknown 1:        ", f"{smpl['unk1']}".rjust(14), "(" + f"{hex(smpl['unk1'])})".rjust(11),    "\n"
            f"        - Unknown 2:        ", f"{smpl['unk2']}".rjust(14), "(" + f"{hex(smpl['unk2'])})".rjust(11),    "\n"
            f"        - Unknown 3:        ", f"{smpl['unk3']}".rjust(14), "(" + f"{hex(smpl['unk3'])})".rjust(11),    "\n"
            f"        - Unknown 4:        ", f"{smpl['unk4']}".rjust(14), "(" + f"{hex(smpl['unk4'])})".rjust(11),    "\n"
            f"        - Finer tune:       ", f"{smpl['fine']}".rjust(14), "(" + f"{hex(smpl['fine'])})".rjust(11), f"         = +{(smpl['fine']/65535) * 103} cents"    "\n"
            f"        - Fine tune?:       ", f"{smpl['ptc1']}".rjust(14), "(" + f"{hex(smpl['ptc1'])})".rjust(11), f"         = +{(smpl['ptc1']/255) * 350} cents"    "\n"
            f"        - Coarse tune:      ", f"{smpl['coar']}".rjust(14), "(" + f"{hex(smpl['coar'])})".rjust(11),    "\n"
            f"        - Coarser tune?:    ", f"{smpl['ptc2']}".rjust(14), "(" + f"{hex(smpl['ptc2'])})".rjust(11), f"         = +{(smpl['ptc2']) * 3} semitones"    "\n"
            f"        - Final tune:       ", f"".rjust(14),               " " + f" ".rjust(11),                    f"           +{((smpl['fine']/65535) * 103) + ((smpl['ptc1']/255) * 350)} cents"    "\n"
            f"        - Root key:         ", f"{smpl['root']}".rjust(14), "(" + f"{hex(smpl['root'])})".rjust(11), f"         = {note_from_key(smpl['root'])}"   "\n"
            f"        - High key:         ", f"{smpl['high']}".rjust(14), "(" + f"{hex(smpl['high'])})".rjust(11), f"         = {note_from_key(smpl['high'])}"   "\n"
            f"        - Playback mode:    ", f"{smpl['mode']}".rjust(14), "(" + f"{hex(smpl['mode'])})".rjust(11), f"         = {'Forward loop' if smpl['mode'] == 2 else 'One-shot' if smpl['mode'] in [0, 1] else 'Reverse'}"   "\n"
            f"        - Playback related: ", f"{smpl['pbck']}".rjust(14), "(" + f"{hex(smpl['pbck'])})".rjust(11),    "\n"
            f"        - Sample start:     ", f"{smpl['smst']}".rjust(14), "(" + f"{hex(smpl['smst'])})".rjust(11), f"samples  = offset", f"{smpl['smst'] * 2 + headerSize}".rjust(14), "(" + f"{hex(smpl['smst'] * 2 + headerSize)})".rjust(11), "in ROM"   "\n"
            f"        - Sample end:       ", f"{smpl['smen']}".rjust(14), "(" + f"{hex(smpl['smen'])})".rjust(11), f"samples  = offset", f"{smpl['smen'] * 2 + headerSize}".rjust(14), "(" + f"{hex(smpl['smen'] * 2 + headerSize)})".rjust(11), "in ROM"   "\n"
            f"        - Loop start:       ", f"{smpl['lpst']}".rjust(14), "(" + f"{hex(smpl['lpst'])})".rjust(11), f"samples  = offset", f"{smpl['lpst'] * 2 + headerSize}".rjust(14), "(" + f"{hex(smpl['lpst'] * 2 + headerSize)})".rjust(11), "in ROM"   "\n"
            f"        - Loop end:         ", f"{smpl['lpen']}".rjust(14), "(" + f"{hex(smpl['lpen'])})".rjust(11), f"samples  = offset", f"{smpl['lpen'] * 2 + headerSize}".rjust(14), "(" + f"{hex(smpl['lpen'] * 2 + headerSize)})".rjust(11), "in ROM"   "\n"
            )
            
#parseCard(r"D:\Users\Furmilion\AppData\Local\Stryde Audio\Swayed\Waveforms\ВКонтакте.swayaudio")
parseCard(r"D:\Users\Furmilion\AppData\Local\Stryde Audio\Swayed\Waveforms\SwayedPreset.swayaudio")
#parseCard(r"D:\Users\Furmilion\AppData\Local\Stryde Audio\Swayed\Waveforms\TestBank.swayaudio")