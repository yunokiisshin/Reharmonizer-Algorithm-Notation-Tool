from music21 import *

# custom implemented app.modules
from modules.rant import *
from modules.noteSolver import *
from modules.utils import *

from openai import OpenAI

import os
from dotenv import load_dotenv
import json

def string_to_dict(string):
    try:
        # Convert the string to a dictionary
        result_dict = json.loads(string)
        return result_dict
    except json.JSONDecodeError as e:
        print(f"An error occurred: {e}")
        return None


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
        
    if remainder == "":
        remainder = "maj"
    
    # Form the formatted chord
    formatted_chord = root + ":" + remainder.lower()
    
    return formatted_chord
    


def generate_chord_symbols(prompt):
    try:
        
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
)
        
        if not client:
            raise ValueError("OpenAI API key is not set in environment variables.")

        # few-shot prompt
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional musician and music theorist. Your job is to create a good 8-bar chord progression in C, suited to the genre. Only provide the strings as shown in the examples. Be creative, but not too odd. Take care of musical qualities. Don't always start with C; don't overly use 2-5-1. Do not use the character ø; replace it with b5 notation. Allowed chord symbols are \"maj\", \"min\", \"dim\", \"aug\", \"maj7\", \"min7\", \"7\", \"dim7\", \"hdim7\", \"minmaj7\", \"maj6\", \"min6\", \"9\", \"maj9\", \"min9\", \"sus4\". DO NOT OUTPUT ANYTHING BUT 8 BARS OF CHORD SYMBOLS."},
                {"role": "user", "content": "give me a jazz chord progression"},
                {"role": "assistant", "content": "{\"0\": [\"Dmin7\"], \"1\": [\"G7\"], \"2\": [\"Cmaj7\"], \"3\": [\"Amin7\", \"Fdim7\"], \"4\": [\"Dmin7\"], \"5\": [\"G7sus4\"], \"6\": [\"Cmaj7\"], \"7\": [\"Cmaj7\"]}"},
                {"role": "user", "content": "give me a pop chord progression"},
                {"role": "assistant", "content": "{\"0\": [\"Cmaj\"], \"1\": [\"E7\"], \"2\": [\"Amin7\"], \"3\": [\"Fmaj7\", \"G7\"], \"4\": [\"Dmin7\"], \"5\": [\"G7sus4\"], \"6\": [\"Cmaj7\"], \"7\": [\"Cmaj7\"]}"},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4",
            temperature = 0.5  # experiment with the value; smaller to get less random results
        )
        # print("response: " + response.choices[0].message['content'])
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None




def main():
    # progression = {
    #     "0": ["Dmin7"],
    #     "1": ["G7"],
    #     "2": ["Cmaj7"],
    #     "3": ["Amin7", "Fdim7"],
    #     "4": ["Dmin7"],
    #     "5": ["G7sus4"],
    #     "6": ["Cmaj7"],
    #     "7": ["Cmaj7"]
    # }
    
    load_dotenv()
    
    progression_raw = string_to_dict(generate_chord_symbols("give me a jazz chord progression"))
    print("progression_raw: ")
    print(progression_raw)
    
    # fit the progression into the format of Notation
    formatted_progression = formatProgression(progression_raw)
    
    # print("formatted progression: ")
    # print(formatted_progression)
    
    list_of_chords = [item for sublist in list(formatted_progression.values()) for item in sublist]
    print(list_of_chords)
    while None in list_of_chords:
        print("None found in progression. Rerunning...")
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
    
    for key in formatted_progression.keys():
        for _ in formatted_progression[key]:
            c = chord.Chord(formatted_solution[chord_index], duration=duration.Duration(4.0 / len(formatted_progression[key])))
            music_stream.append(c)
            chord_index += 1

    print("Chords list:", chords_list)
    print("Formatted solution:", formatted_solution)
    music_stream.write("midi", "output.mid")
    

if __name__ == "__main__":
    main()


