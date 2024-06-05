from constraint import *
from music21 import pitch, chord, note
import random

# Global constraints: note values shouldn't be too high nor too low
LOWEST_NOTE = pitch.Pitch("C2").midi
HIGHEST_NOTE = pitch.Pitch("G5").midi
GLOBAL_DOMAIN = list(range(LOWEST_NOTE, HIGHEST_NOTE + 1))


# Helper functions
def shift(note, semitones):
    return pitch.Pitch(note.midi + semitones)

def fill_dict_value(note_dict, key, note):
    note_val = pitch.Pitch(note)
    while note_val.midi >= LOWEST_NOTE:
        note_val.midi -= 12
    note_val.midi += 12
    while note_val.midi <= HIGHEST_NOTE:
        note_dict[key].append(note_val.midi)
        note_val.midi += 12

def prepare_note_dict(root_note, chord_type):
    note_dict = dict([("root", []), ("third", []), ("fifth", []), ("seventh", []), ("ninth", []), ("extensions", [])])
    
    root = pitch.Pitch(root_note)
    
    is_sus4, is_sus2, is_b5, is_sharp5, is_b9, is_sharp9 = False, False, False, False, False, False
    # Remove any suffixes from the chord type, it would be processed later
    if 'sus4' in chord_type:
        chord_type = chord_type.replace('sus4', '')
        is_sus4 = True
    
    if 'sus2' in chord_type:
        chord_type = chord_type.replace('sus2', '')
        is_sus2 = True
    
    if 'b5' in chord_type:
        chord_type = chord_type.replace('b5', '')
        is_b5 = True
        
    if '#5' in chord_type:
        chord_type = chord_type.replace('#5', '')
        is_sharp5 = True
        
    if 'b9' in chord_type:
        chord_type = chord_type.replace('b9', '')
        is_b9 = True
        
    if '#9' in chord_type:
        chord_type = chord_type.replace('#9', '')
        is_sharp9 = True
        
    # chord_formulas contain intervals for possible chord types
    chord_formulas = {
        'maj': [0, 4, 7],  # Major triad
        'min': [0, 3, 7],  # Minor triad
        '7': [0, 4, 7, 10],  # Dominant 7th
        'maj7': [0, 4, 7, 11],  # Major 7th
        'min6': [0, 3, 7, 9],  # Minor 6th
        'min7': [0, 3, 7, 10],  # Minor 7th
        'dim7': [0, 3, 6, 9],  # Diminished 7th
        'maj9': [0, 4, 7, 11, 2],  # Major 9th
        'min9': [0, 3, 7, 10, 2],  # Minor 9th
        '9': [0, 4, 7, 10, 2],  # Dominant 9th
        '13': [0, 4, 7, 10, 2, 9],  # Dominant 13th
        '7#11': [0, 4, 7, 10, 6],  # Dominant 7th sharp 11th
        '7b13': [0, 4, 7, 10, 9],  # Dominant 7th flat 13th
        'dim': [0, 3, 6],  # Diminished triad
        'aug': [0, 4, 8],  # Augmented triad
        'dim7': [0, 3, 6, 9],  # Diminished 7th
        'hdim7': [0, 3, 6, 10],  # Half-diminished 7th
        'minmaj7': [0, 3, 7, 11],  # Minor major 7th
    }
    
    if chord_type not in chord_formulas.keys():
        error = "Chord type not recognized."
        raise ValueError(error)
    
    # interval_list: list of intervals to be added to the root note
    interval_list = chord_formulas[chord_type]
    
    interval_strings = ["root", "third", "fifth", "seventh", "ninth", "extensions"]
    
    for i, interval in enumerate(interval_list):
        interval_string = str(interval_strings[i])  # Ensure this results in a string
        note = shift(root, interval)
        fill_dict_value(note_dict, interval_string, note)
        
    # Alter the notes based on the chord type
    if is_sus4: 
        note_dict["third"].clear()
        third = shift(root, 5)
        fill_dict_value(note_dict, "third", third)
        
    if is_sus2: 
        note_dict["third"].clear()
        third = shift(root, 2)
        fill_dict_value(note_dict, "third", third)
        
    if is_b5: 
        note_dict["fifth"].clear()
        fifth = shift(root, 6)
        fill_dict_value(note_dict, "fifth", fifth)
    
    if is_sharp5: 
        note_dict["fifth"].clear()
        fifth = shift(root, 8)
        fill_dict_value(note_dict, "fifth", fifth)
        
    if is_b9:
        note_dict["ninth"].clear()
        ninth = shift(root, 1)
        fill_dict_value(note_dict, "ninth", ninth)
        if len(note_dict["ninth"]) > 1:
            note_dict["ninth"].pop(0)
        
    if is_sharp9:
        note_dict["ninth"].clear()
        ninth = shift(root, 3)
        fill_dict_value(note_dict, "ninth", ninth)
        if len(note_dict["ninth"]) > 1:
            note_dict["ninth"].pop(0)
    
    return note_dict


# Solver Wrapper
# mode: "simple", "jazz", "rootless", "drop2", etc, check if implemented. This is where customizations can be made.
def produceAllNotes(progression=list, mode=str):
    solutions = []
    notes_so_far = []
    
    for iteration in range(0, len(progression) - 1):
        solution = produceNotes(progression[iteration], progression[iteration+1], mode)
        if solution:
            # print("solution found")
            solutions.append(solution)
            notes_so_far.append(list(solution.values()))
            
        else:
            print("solution not found")
            break  # If no solution is found, break the loop
        # print("notes_so_far: ")
        # print(notes_so_far)
    
    solution = produceNotes(progression[iteration+1], progression[0], mode) # so that it tries to loop back to the first chord
    if solution:
            # print("solution found")
            solutions.append(solution)
            notes_so_far.append(list(solution.values()))
            
    else:
        print("solution not found")
        
    # print("notes_so_far: ")
    # print(notes_so_far)
        
    return solutions





# CSP Solver function
def produceNotes(current_chord, next_chord, mode="simple"):
    
    problem = Problem()
    
    
    # Simple mode: most basic voicing, with a doubled bass down an octave
    if mode == "simple":   
        # print("current_chord: " + current_chord)
        
        note_dict = prepare_note_dict(current_chord.split(':')[0], current_chord.split(':')[1])
        # print("note_dict: ")
        # print(note_dict)
        
        # Filter out empty lists and get the non-empty keys
        non_empty_keys = [key for key, value in note_dict.items() if value]
        
        # Create variables based on the number of non-empty keys
        note_vars = [f"{current_chord}_note_{i}" for i in range(len(non_empty_keys))]
        
        # print("note_vars: ")
        # print(note_vars) 
        # Add variables to the problem with the given domain; that is, possible note values corresponding to its possible value
        for i in range(len(note_vars)):
            problem.addVariable(note_vars[i], note_dict[non_empty_keys[i]])
        
        # Add constraints to ensure notes are ordered from small to big
        for k in range(len(note_vars) - 1):
            problem.addConstraint(lambda n1, n2: n1 < n2, (note_vars[k], note_vars[k+1]))
        
        problem.addVariable("bass_note", GLOBAL_DOMAIN)
        problem.addConstraint(lambda n1, n2: n1 == n2 + 12, (note_vars[0], "bass_note"))  
    
        
    elif mode == "jazz":
        # Craft a custom voicing for each chord
        jazz_voicings = {
            "maj": [[0, 11, 14, 16, 19], # open studio jazz
                    [0, 9, 11, 16, 19], 
                    [0, 7, 14, 19, 23], 
                    [0, 7, 9, 14, 16]],
            "min": [[0, 10, 15, 21, 26],
                    [0, 7, 10, 14, 17],
                    [0, 3, 10, 14, 19],
                    [0, 10, 14, 15, 21]], 
            "7": [[0, 10, 16, 20, 25],
                  [0, 10, 16, 20, 24],
                  [0, 10, 14, 16, 19],
                  [0, 10, 16, 21, 25]],
            "9": [[0, 10, 16, 20, 25],
                  [0, 10, 16, 20, 24],
                  [0, 10, 14, 16, 19],
                  [0, 10, 16, 21, 25]],
            "dim": [[0, 6, 9, 17],  # Peter Martin
                    [0, 6, 9, 15, 20],
                    [0, 3, 6, 9, 12],
                    [0, 6, 9, 15, 18]],
        }
        
        # print("current_chord: " + current_chord)
        
        current_chord_root = current_chord.split(':')[0]
        current_chord_type = current_chord.split(':')[1]
        
        if "maj" in current_chord_type:
            # randomly choose a voicing from maj voicings
            chord_structure = jazz_voicings["maj"][random.randint(0, len(jazz_voicings["maj"]) - 1)]
            
        elif "min" in current_chord_type:
            chord_structure = jazz_voicings["min"][random.randint(0, len(jazz_voicings["min"]) - 1)]
            
        elif "dim" in current_chord_type:
            chord_structure = jazz_voicings["dim"][random.randint(0, len(jazz_voicings["dim"]) - 1)] 
        
        elif "7" in current_chord_type:
            chord_structure = jazz_voicings["7"][random.randint(0, len(jazz_voicings["7"]) - 1)]
        
        else:
            error = "Ooh I have not thought that far in"
            raise ValueError(error)   
        
        note_vars = [f"{current_chord}_note_{i}" for i in range(len(chord_structure))]
        
        # Initialize variables
        problem.addVariables(note_vars, GLOBAL_DOMAIN)
        
        # First one is always root; since current_chord_root is the root, pitch.Pitch(current_chord_root).midi is the midi value
        root_midi = pitch.Pitch(current_chord_root).midi - 12
        if root_midi >= 55:
            root_midi -= 12     # ensure the bass is low enough
        problem.addConstraint(lambda n1: n1 == root_midi, (note_vars[0],))
        
        # Ensure that each note is placed accordingly to the difference within chord_structure
        for i in range(1, len(note_vars)):
            problem.addConstraint(lambda n1, n2, interval=chord_structure[i]: n2 == n1 + interval, (note_vars[0], note_vars[i]))

    
    elif mode == "rootless":
        
        rootless_voicings = {
            "maj": [[0, 9, 14, 19], # open studio jazz, PianoPig
                    [0, 7, 11, 14, 16]], 
            "min": [[0, 10, 14, 15, 19],
                    [0, 3, 5, 10, 14]], 
            "7": [[0, 4, 9, 10, 14],
                  [0, 10, 14, 16]],
            "9": [[0, 4, 9, 10, 14],
                  [0, 10, 14, 16]],
            "dim": [[0, 6, 9, 17],  # Peter Martin
                    [0, 6, 9, 15, 20],
                    [0, 3, 6, 9, 12],
                    [0, 6, 9, 15, 18]]
        }

        
        print("current_chord: " + current_chord)
        
        current_chord_root = current_chord.split(':')[0]
        current_chord_type = current_chord.split(':')[1]
        
        if "maj" in current_chord_type:
            # randomly choose a voicing from maj voicings
            chord_structure = rootless_voicings["maj"][random.randint(0, len(rootless_voicings["maj"]) - 1)]
            
        elif "min" in current_chord_type:
            chord_structure = rootless_voicings["min"][random.randint(0, len(rootless_voicings["min"]) - 1)]
            
        elif "dim" in current_chord_type:
            chord_structure = rootless_voicings["dim"][random.randint(0, len(rootless_voicings["dim"]) - 1)] 
        
        elif "7" in current_chord_type:
            chord_structure = rootless_voicings["7"][random.randint(0, len(rootless_voicings["7"]) - 1)]
        
        else:
            error = "Ooh I have not thought that far in"
            raise ValueError(error)   
        
        note_vars = [f"{current_chord}_note_{i}" for i in range(len(chord_structure))]
        
        # Initialize variables
        problem.addVariables(note_vars, GLOBAL_DOMAIN)
        
        # First one is always root; since current_chord_root is the root, pitch.Pitch(current_chord_root).midi is the midi value
        root_midi = pitch.Pitch(current_chord_root).midi - 12
        if root_midi >= 55:
            root_midi -= 12     # ensure the bass is low enough
        problem.addConstraint(lambda n1: n1 == root_midi, (note_vars[0],))
        
        # Ensure that each note is placed accordingly to the difference within chord_structure
        for i in range(1, len(note_vars)):
            problem.addConstraint(lambda n1, n2, interval=chord_structure[i]: n2 == n1 + interval, (note_vars[0], note_vars[i]))
    
    # elif mode == "drop2":
        
    # ensuring range
    problem.addConstraint(MinSumConstraint(len(note_vars) * 50))
    solutions = problem.getSolutions()
    
    if solutions:
        random_solution = random.choice(solutions)
        # print("Random solution:", random_solution)
        
        # remove root if it is rootless mode
        if mode == "rootless":
            random_solution.pop(f"{current_chord}_note_0")
    else: 
        error = "No solution found for produceNotes."
        raise ValueError(error)
    
    return random_solution


        
    
    


# progression=["C:maj7", "G:maj", "A:min7", "F:maj7"]
# solution = produceAllNotes(progression, "jazz")
# print("Solution:", solution)