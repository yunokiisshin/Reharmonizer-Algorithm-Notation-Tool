from music21 import *

# custom implemented app.modules
from app.modules.rant import *
from app.modules.noteSolver import *
from app.modules.utils import *


def main():
    progression = {
        "0": ["Dmin7"],
        "1": ["G7"],
        "2": ["Cmaj7"],
        "3": ["Amin7", "Fdim7"],
        "4": ["Dmin7"],
        "5": ["G7sus4"],
        "6": ["Cmaj7"],
        "7": ["Cmaj7"]
    }
    
    def formatProgression(progression):
        formatted_progression = {}
        for key, chords in progression.items():
            formatted_chords = [formatChord(chord) for chord in chords if chord is not None]
            formatted_progression[key] = formatted_chords
        return formatted_progression

    def formatChord(chord):
        if chord is None:
            return None
        
        root = chord[0]
        formatted_chord = ""
        
        # Check for accidentals (sharp or flat)
        if len(chord) > 1 and (chord[1] == '#' or chord[1] == 'b'):
            root += chord[1]
            remainder = chord[2:]
        else:
            remainder = chord[1:]
        
        # Ensure proper formatting for minor, major, and diminished chords
        if "m" in remainder and not any(sub in remainder for sub in ["maj", "min", "dim"]):
            remainder = remainder.replace("m", "min")
        
        if "M" in remainder and "Maj" not in remainder:
            remainder = remainder.replace("M", "maj")
        
        # Form the formatted chord
        formatted_chord = root + ":" + remainder.lower()
        
        return formatted_chord
        
    # fit the progression into the format of Notation
    formatted_progression = formatProgression(progression)
    print("HERE")
    list_of_chords = [item for sublist in list(formatted_progression.values()) for item in sublist]
    print(list_of_chords)
    while None in list_of_chords:
        print("None found in progression. Rerunning...")
        formatted_progression = formatProgression(progression)
        list_of_chords = [item for sublist in list(formatted_progression.values()) for item in sublist]
    
    new_prog = rant(formatted_progression, 1)
    print("after rant: ")
    print(new_prog)
    
    chords_list = [item for sublist in list(new_prog.values()) for item in sublist]
    
    solution_found = False
    while not solution_found:
        try:
            print()
            formatted_solution = produceAllNotes(chords_list, "simple")
            solution_found = True
        except ValueError as e:
            print(f"Error occurred: {e}. Retrying...")
    
    # for keeping track
    chord_index = 0
    
    # craft a midi file to hear the result
    music_stream = stream.Stream()
    
    for key in progression.keys():
        for _ in progression[key]:
            c = chord.Chord(formatted_solution[chord_index], duration=duration.Duration(4.0 / len(progression[key])))
            music_stream.append(c)
            chord_index += 1

    print("Chords list:", chords_list)
    print("Formatted solution:", formatted_solution)
    music_stream.write("midi", "output.mid")


if __name__ == "__main__":
    main()


