from utils import *
from Notation import *

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
    # Initialize notation instance
    notation = Notation()
    
    # fit the progression into the format of Notation
    
    
    if level == 0:
        new_prog = simplifyChords(progression)
        return new_prog
    
    
    if level == 1:
        return progression
    

    if level == 2:
        new_prog = substituteChords(progression)
        return new_prog
    
    
    if level == 3:
        new_prog = reharmonize(progression)
        return new_prog
    


# for level 1 process
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
    root = chord[0]
    triad = ""
    
    # Check for accidentals (sharp or flat)
    if len(chord) > 1 and (chord[1] == '#' or chord[1] == 'b'):
        root += chord[1]
        remainder = chord[2:]
    else:
        remainder = chord[1:]
    
    # Determine chord quality and form the triad
    if 'm' in remainder and ('maj' or 'Maj') not in remainder:
        triad = root + "m"
    elif 'aug' in remainder:
        triad = root + "aug"
    elif 'dim' in remainder:
        triad = root + "dim"
    else:
        triad = root + "M"

    return triad



# for level 2 process
'''
Given a chord progression, generates another progression 
with certain amount (defined via param) of chords substituted.

params:
    progression: a dictionary representing an 8-bar chord progression.
    num: an integer that indicates how many chords will be substituted.

returns: 
    new_prog: post-substitution progression. Same amount of 
'''
def substituteChords(progression=dict, num=int):
    new_prog = formatProgression(progression)
    
    
    
    
# for level 3 process
def reharmonize(progression):



def main():
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
    
    new_prog = rant(progression, 0)
    # when you do progression, 0, you get:
    # {'0': ['Am'], '1': ['DM'], '2': ['GM'], '3': ['Cm', 'FM'], '4': ['BbM'], '5': ['Am', 'DM'], '6': ['Gm', 'CM'], '7': ['FM']}
    print(new_prog)
    return 

if __name__ == "__main__":
    main()
