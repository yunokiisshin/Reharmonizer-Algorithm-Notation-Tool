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
    
    # Form the formatted chord
    formatted_chord = root + ":" + remainder

    return formatted_chord


# creates a list of progression without the chords
def constructRootList(progression):


def noteToInt(note):
    note_to_int_dict = {
        "C": 0,
        "C#": 1, "Db": 1,
        "D": 2,
        "D#": 3, "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6, "Gb": 6,
        "G": 7,
        "G#": 8, "Ab": 8,
        "A": 9,
        "A#": 10, "Bb": 10,
        "B": 11
    }
    
    return note_to_int_dict.get(note, -1)  # Returns -1 if the note is not found



def intToNote(number):
    int_to_note_dict = {
        0: "C",
        1: "C#",
        2: "D",
        3: "D#",
        4: "E",
        5: "F",
        6: "F#",
        7: "G",
        8: "G#",
        9: "A",
        10: "A#",
        11: "B"
    }
    
    return int_to_note_dict.get(number, "Invalid note")  # Returns "Invalid note" if the number is not in range
