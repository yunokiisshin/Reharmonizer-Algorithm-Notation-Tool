from rant import *
from noteSolver import *
from utils import *

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
    
    # print("before: ")
    new_prog = rant(progression, 2)
    
    # print("after: ")
    # print(new_prog)
    
    # CSP part
    chords_list = [item for sublist in list(new_prog.values()) for item in sublist]
    print("Chords list:", chords_list)
    solution = produceAllNotes(chords_list, "jazz")
    print("Solution:", solution)
    
    
    return

if __name__ == "__main__":
    main()