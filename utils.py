def formatProgression(progression):
    formatted_progression = {}
    for key, chords in progression.items():
        formatted_chords = [formatChord(chord) for chord in chords]
        formatted_progression[key] = formatted_chords
    return formatted_progression

def formatChord(chord):
    root = chord[0]
    formatted_chord = ""
    
    # Check for accidentals (sharp or flat)
    if len(chord) > 1 and (chord[1] == '#' or chord[1] == 'b'):
        root += chord[1]
        remainder = chord[2:]
    else:
        remainder = chord[1:]
    
    if "m" in remainder and ("maj" or "min") not in remainder:
        remainder = remainder.replace("m", "min")
    
    if "M" in remainder and "Maj" not in remainder:
        remainder = remainder.replace("M", "maj")
    
    # Form the formatted chord
    formatted_chord = root + ":" + remainder.lower()

    return formatted_chord
