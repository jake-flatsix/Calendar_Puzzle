# Calendar_Puzzle

An interactive puzzle game where players arrange pentomino pieces to fill a board while revealing a specific date (month, day, and weekday).

## Features

- **Solver**: Command-line tool that uses backtracking to find solutions for any date
- **Interactive Player**: Web-based GUI for playing the puzzle manually
- **Flexible Configuration**: Easy-to-edit text files for board layout and piece shapes

## Setup

This project uses a virtual environment to keep dependencies isolated.

### Initial Setup

```bash
# 1. Create virtual environment (already done)
python -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# 3. Install dependencies
python -m pip install -r requirements.txt
```

### Every Time You Work on the Project

```bash
# Always activate the venv first!
source venv/bin/activate
```

## Usage

### 🌐 Live Web Version (GitHub Pages)

Play the puzzle online at: **[Your GitHub Pages URL will be here]**

The live version runs entirely in your browser with no installation needed!

### 💻 Local Python Version

#### CLI Solver

Solve the puzzle for any date from the command line:

```bash
python solve_puzzle.py today
python solve_puzzle.py 01-14
python solve_puzzle.py 2026-12-25
```

#### Local Web Server

Start the Flask development server:

```bash
python player_server.py
```

Then open your browser to: http://localhost:8000

### How to Play

1. Select a date to reveal target squares on the board
2. **Left-click** a piece to select it
3. **Right-click** on sidebar pieces to rotate them before selecting
4. **Right-click** on the board to cycle through orientations
5. Hover over the board to preview placement
6. **Left-click** on the board to place the piece
7. **Click** a placed piece to grab and reposition it
8. **Click outside** the board to remove a grabbed piece
9. Use **Hint** to get one piece at a time, or **Solve** for the complete solution
10. Fill all squares except the target date to win!

## Project Structure

```
Calendar_Puzzle/
├── index.html             # Static web version (GitHub Pages)
├── board.txt              # Board layout with dates
├── pieces.txt             # Piece definitions (pentominoes)
├── calendar_puzzle.py     # Core classes (Board, Piece, Coord)
├── solver.py              # Solver algorithm and game logic
├── solve_puzzle.py        # CLI solver tool
├── player_server.py       # Flask development server
├── templates/
│   └── player.html        # Flask template (local dev)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

**Two Versions:**
- **`index.html`** - Static site for GitHub Pages deployment (JavaScript solver)
- **`templates/player.html`** + **`player_server.py`** - Local Python/Flask version (same features)

## Configuration

### Board Layout (board.txt)

The board is defined as a text grid with months, days, weekdays, and blank squares (`.`).

### Pieces (pieces.txt)

Pieces are defined using ASCII art with `#` representing filled squares:

```
Piece1:
#####

Piece2:
####
#
```

## Development

When adding new features:

1. Always work within the venv
2. If adding dependencies: `python -m pip install <package>` then `python -m pip freeze > requirements.txt`
3. Test both solver and player after changes

## Virtual Environment Best Practice

This project follows Python best practices by using a dedicated virtual environment. Benefits:
- Dependencies are isolated from system Python
- No conflicts with other projects
- Reproducible environment via requirements.txt
- Easy to reset (delete `venv/` and recreate)

The `venv/` directory is excluded from git via `.gitignore`.
