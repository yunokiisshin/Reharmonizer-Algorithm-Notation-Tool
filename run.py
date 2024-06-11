from app import app
from flask import Flask, request, jsonify

@app.route('/api/chords', methods=['POST'])
def get_chords():
    # This is where you would process the data and run your Python code
    data = request.json
    # For demonstration, we'll just return the received data
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
    return jsonify(progression)


if __name__ == '__main__':
    app.run(debug=True)