from music21 import *

# custom implemented modules
from modules.rant import *
from modules.noteSolver import *
from modules.utils import *


def main():
    progression = {
            "0": ["Dmin7"],
            "1": ["G7"],
            "2": ["Cmaj7"],
            "3": ["Cm7", "F7"],
            "4": ["Bbmaj7"],
            "5": ["Am7", "D7"],
            "6": ["Gm7", "C7sus4"],
            "7": ["FMaj7"]
        }
    
    # print("before: ")
    new_prog = rant(progression, 1)
    
    # print("after: ")
    # print(new_prog)
    
    # CSP part
    chords_list = [item for sublist in list(new_prog.values()) for item in sublist]
    # print("Chords list:", chords_list)
    solution = produceAllNotes(chords_list, "rootless")
    # print("Solution:", solution)
    
    formatted_solution = []
    for item in solution:
        added_chord = list(item.values())
        added_chord = [int(note) for note in added_chord]
        formatted_solution.append(added_chord)
    
    
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
    
    return



if __name__ == "__main__":
    main()