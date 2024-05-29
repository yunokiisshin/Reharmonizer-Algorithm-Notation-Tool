# https://archives.ismir.net/ismir2005/paper/000080.pdf
# Based on a 2005 ISMIR paper

class Notation:
    def __init__(self):
        self.shorthand = ["maj", "min", "dim", "aug", 
                          "maj7", "min7", "7", "dim7", 
                          "hdim7", "minmaj7", "maj6", 
                          "min6", "9", "maj9", "min9", "sus4"]
        self.modifier = ["#", "b"]
        self.natural = ["A", "B", "C", "D", "E", "F", "G"]
        self.intervals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.chord_structures = {
            "maj" : [0, 4, 7],
            "min" : [0, 3, 7],
            "dim" : [0, 3, 6],
            "aug" : [0, 4, 8],
            "maj7" : [0, 4, 7, 11],
            "min7" : [0, 3, 7, 10],
            "7" : [0, 4, 7, 10],
            "dim7" : [0, 3, 6, 9],
            "hdim7" : [0, 3, 6, 10],
            "minmaj7" : [0, 3, 7, 11],
            "maj6" : [0, 4, 7, 9],
            "min6" : [0, 3, 7, 9],
            "9" : [0, 4, 7, 10, 14],
            "maj9" : [0, 4, 7, 11, 14],
            "min9" : [0, 3, 7, 10, 14],
            "sus4" : [0, 5, 7]
        }

    def create_chord(self, root, shorthand=None, degrees=None, bass=None):
        """
        Create a chord representation based on the given parameters.
        
        :param root: The root note of the chord (e.g., "C", "G#", "Bb").
        :param shorthand: The shorthand notation for common chords (e.g., "maj", "min7").
        :param degrees: A list of intervals or modified intervals (e.g., ["b3", "5", "b7"]).
        :param bass: The bass note if different from the root (e.g., "3", "5").
        :return: The chord representation as a string.
        """
        if shorthand:
            chord = f"{root}:{shorthand}"
            if degrees:
                chord += f"({','.join(degrees)})"
        else:
            chord = f"{root}:({','.join(degrees)})" if degrees else root
        
        if bass:
            chord += f"/{bass}"
        
        return chord

    def parse_chord(self, chord_str):
        """
        Parse a chord string and return its components.
        
        :param chord_str: The chord string (e.g., "C:maj7", "D:min7(b3,11)/5").
        :return: A dictionary with root, shorthand, degrees, and bass.
        """
        root = None
        shorthand = None
        degrees = []
        bass = None
        
        if chord_str == self.no_chord:
            return {"root": None, "shorthand": None, "degrees": None, "bass": None}
        
        # Separate root and the rest of the chord
        if ":" in chord_str:
            parts = chord_str.split(":")
            root = parts[0]
            rest = parts[1]
        else:
            parts = chord_str.split("/")
            root = parts[0]
            rest = None
            if len(parts) > 1:
                bass = parts[1]
        
        # Parse the rest of the chord
        if rest:
            if "/" in rest:
                rest, bass = rest.split("/")
            if "(" in rest:
                shorthand, degrees_part = rest.split("(")
                degrees = degrees_part.rstrip(")").split(",")
            else:
                shorthand = rest
        
        return {"root": root, "shorthand": shorthand, "degrees": degrees, "bass": bass}

    def display_chord(self, chord_dict):
        """
        Display a chord dictionary in a readable format.
        
        :param chord_dict: The chord dictionary (e.g., {"root": "C", "shorthand": "maj7", "degrees": [], "bass": None}).
        :return: A readable chord string.
        """
        chord_str = chord_dict["root"]
        if chord_dict["shorthand"]:
            chord_str += f":{chord_dict['shorthand']}"
            if chord_dict["degrees"]:
                chord_str += f"({','.join(chord_dict['degrees'])})"
        elif chord_dict["degrees"]:
            chord_str += f":({','.join(chord_dict['degrees'])})"
        
        if chord_dict["bass"]:
            chord_str += f"/{chord_dict['bass']}"
        
        return chord_str


# Example usage
notation = Notation()
chord1 = notation.create_chord("C", "maj7")
chord2 = notation.create_chord("D#", "min7", ["b3", "5", "b7", "9"], "5")
parsed_chord = notation.parse_chord("D#:min7(b3,5,b7,9)/5")

print(chord1)  # Output: C:maj7
print(chord2)  # Output: D#:min7(b3,5,b7,9)/5
print(parsed_chord)  # Output: {'root': 'D#', 'shorthand': 'min7', 'degrees': ['b3', '5', 'b7', '9'], 'bass': '5'}
print(notation.display_chord(parsed_chord))  # Output: D#:min7(b3,5,b7,9)/5
