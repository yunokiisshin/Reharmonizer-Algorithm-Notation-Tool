from music21 import *
from utils import *
import random

'''
rant() converts a given chord progression into an altered version, depending on the level input. It is also a wrapping function containing multiple 
params:
    progression: a dictionary representing an 8-bar chord progression. An example would look like:
        if the represented chord_symbols = "Am7 D7 GM9 Cm7|F7 Bbmaj7 Am7|D7 Gm7|C7sus4 FMaj7":
        progression = {
            "0": ["Am7"],
            "1": ["D7"],
            "2": ["GM9"],
            "3": ["Cm7", "F7"],
            "4": ["Bbmaj7"],
            "5": ["Am7", "D7"],
            "6": ["Gm7", "C7sus4"],
            "7": ["FMaj7"]
        }

    level: the higher the number, the more advanced the reharmonization. 
        0: simplified; removes all the excessive extentions and turn all chords into triads
        1: as-is.
        2: conducts chord substitution on selected portions to 
           maintain chord functions while altering the harmony.
        3: conducts reharmonization on series of chords, sometimes altering the chord functions.

returns:
    new_prog: the altered chord progression, represented in dictionary form.
'''
def rant(progression, level):
    
    # fit the progression into the format of Notation
    formatted_progression = formatProgression(progression)
    # print(formatted_progression)
    
    if level == 0:
        new_prog = simplifyChords(formatted_progression)
        return new_prog
    
    if level == 1:
        return formatted_progression

    if level == 2:
        new_prog = substituteChords(formatted_progression)
        return new_prog
    
    if level == 3:
        new_prog = reharmonize(formatted_progression)
        return new_prog
    


# for level 0 process
def simplifyChords(progression):
    new_prog = progression.copy()
    
    for key in progression.keys():
        new_prog[key] = [turnIntoTriad(item) for item in progression[key]]
    return new_prog



'''
Turns a given chord symbol into its simple triad variant.
params: 
    chord: a string of chord symbol, e.g. F, Gm, AMaj7...
    
returns:
    triad: a triad version of the chord symbol.
'''
def turnIntoTriad(chord):
    root = chord.split(":")[0]
    modifier = chord.split(":")[1]
    triad = root
    if ("m" or "min") in modifier:
        triad += ":min"
    elif "aug" in modifier: 
        triad += ":aug"
    elif "dim" in modifier:
        triad += ":dim"
    else:
        triad += ":maj"
    
    return triad



    '''
    Given a chord progression, generates another progression 
    with certain amount (defined via param) of chords substituted.

    params:
        progression: a dictionary representing an 8-bar chord progression.
        num: an integer that indicates how many chords will be substituted.

    returns: 
        new_prog: post-substitution progression. Same amount of 
    '''




# for level 2 process
def substituteChords(progression):
    new_prog = progression.copy()
    
    # Iterate over each bar in the progression
    for bar in range(len(new_prog)):
        for i, chord in enumerate(new_prog[str(bar)]):
            root = chord.split(":")[0]
            modifier = chord.split(":")[1]
            # Check for tritone substitution conditions
            if modifier == "7" or modifier == "9": 
                altered_chord = tritoneSubstitution(chord)
                # Replace the old chord with the new one
                new_prog[str(bar)][i] = altered_chord
            
            if modifier == ("maj7" or "maj"):
                altered_chord = tonicSubstitution(chord)
                new_prog[str(bar)][i] = altered_chord
    
    return new_prog
    
    
    
'''Tritone substitution functionalities'''    
def tritoneSubstitution(chord):
        root = chord.split(":")[0]
        modifier = chord.split(":")[1]
        
        def getTritone(root):
            # Mapping from root notes to their tritone counterparts
            tritone_map = {
                "C": "Gb", "C#": "G", "Db": "G", "D": "Ab", "D#": "A", "Eb": "A",
                "E": "Bb", "F": "B", "F#": "C", "Gb": "C", "G": "Db", "G#": "D",
                "Ab": "D", "A": "Eb", "A#": "E", "Bb": "E", "B": "F"
            }
                
            if root in tritone_map:
                return tritone_map[root]
            else:
                return root  # If not found in map, return the root as is

        tritone_root = getTritone(root)
        return f"{tritone_root}:{modifier}"
    



'''
A loose variant of tonic substitution; may alter chord function, 
but it is interesting and coherent enough.
It alters the "tonic" (vague as the key is unspecified), I, into iii or vi
'''
def tonicSubstitution(chord):
    root = chord.split(":")[0]
    modifier = chord.split(":")[1]
    
    root_pitch = pitch.Pitch(root)
    root_midi = root_pitch.midi

    if modifier == "maj7":    
        # Randomly choose between iii and vi
        if random.choice([True, False]):
            new_pitch = pitch.Pitch()
            new_pitch.midi = root_midi - 3
            return f"{new_pitch.name}:min7"
        else:
            new_pitch = pitch.Pitch()
            new_pitch.midi = root_midi + 4
            return f"{new_pitch.name}:min7"
    elif modifier == "maj":
        if random.choice([True, False]):
            new_pitch = pitch.Pitch()
            new_pitch.midi = root_midi - 3
            return f"{new_pitch.name}:min"
        else:
            new_pitch = pitch.Pitch()
            new_pitch.midi = root_midi + 4
            return f"{new_pitch.name}:min"

# for level 3 process
def reharmonize(progression):
    new_prog = progression.copy()
    
    # Implement reharmonization logic
    
    
    
    
    return new_prog






'''
Given a chord progression, generates a list of unique root notes.
params:
    progression: a dictionary representing an 8-bar chord progression.
    
returns:
    root_list: a list of unique root notes.
'''
def constructRootList(progression):
    root_list = []
    for key in progression.keys():
        for chord in progression[key]:
            root = chord.split(":")[0]
            if root not in root_list:
                root_list.append(root)
    return root_list



