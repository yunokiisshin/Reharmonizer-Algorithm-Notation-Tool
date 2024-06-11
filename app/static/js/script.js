document.getElementById('generateBtn').addEventListener('click', drawProgression);

const progression = {
    "0": ["Dmin7"],
    "1": ["G7"],
    "2": ["Cmaj7"],
    "3": ["Amin7", "Fdim7"],
    "4": ["Dmin7"],
    "5": ["G7sus4"],
    "6": ["Cmaj7"],
    "7": ["Cmaj7"]
};

const progression_two = {
    "0": ["Dmin7"],
    "1": ["Db7"],
    "2": ["Cmaj7"],
    "3": ["A7", "Fdim7"],
    "4": ["D7"],
    "5": ["G7sus4"],
    "6": ["Cmaj7"],
    "7": ["Cmaj7"]
};



const colors = ["#FFC0CB", "#A9A9A9", "#ADD8E6", "#D3D3D3", "#FFD700", "#98FB98", "#FF69B4", "#8A2BE2"];

function drawInitialGrid() {
    const canvas = document.getElementById('chordCanvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const rows = 2;
    const columns = 4;
    const sectionWidth = canvas.width / columns;
    const sectionHeight = canvas.height / rows;

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < columns; col++) {
            drawSection(ctx, col * sectionWidth, row * sectionHeight, sectionWidth, sectionHeight, "", "#D3D3D3");
        }
    }
}

function drawProgression() {
    const canvas = document.getElementById('chordCanvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const row1Count = 4;
    const row2Count = 4;

    const topProgression = Array.from({length: row1Count}, (_, i) => i.toString());
    const bottomProgression = Array.from({length: row2Count}, (_, i) => (i + row1Count).toString());

    const rowHeight = canvas.height / 2;
    const sectionWidthTop = canvas.width / row1Count;
    const sectionWidthBottom = canvas.width / row2Count;

    drawRow(ctx, topProgression, sectionWidthTop, 0, rowHeight);
    drawRow(ctx, bottomProgression, sectionWidthBottom, rowHeight, rowHeight);
}

function drawRow(ctx, progressionKeys, sectionWidth, yOffset, rowHeight) {
    let x = 0;
    progressionKeys.forEach((key, i) => {
        // if 2 is selected in the pulldown then use progression_two
        const chords = progression[key] || [];
        const chordWidth = sectionWidth / chords.length;
        chords.forEach((chord, j) => {
            drawSection(ctx, x, yOffset, chordWidth, rowHeight, chord, colors[(i + j) % colors.length]);
            x += chordWidth;
        });
    });
}

function drawSection(ctx, x, y, width, height, chord, color) {
    const borderWidth = 5; // Width of the white border

    // Draw white border
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(x - borderWidth, y - borderWidth, width + 2 * borderWidth, height + 2 * borderWidth);

    // Draw colored section
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);

    // Draw chord text
    if (chord) {
        ctx.fillStyle = "#000000";
        ctx.font = "bold 48px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(chord, x + width / 2, y + height / 2);
    }
}

window.onload = () => {
    drawInitialGrid();
};
