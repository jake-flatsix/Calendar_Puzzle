#!/usr/bin/env python3
"""Flask web server for the interactive Calendar Puzzle player."""

from flask import Flask, render_template, jsonify, request
from calendar_puzzle import parse_board, parse_pieces, Coord
from solver import GameState, get_target_coords, parse_date, PuzzleSolver
import json

app = Flask(__name__)

# Load board and pieces at startup
board = parse_board('board.txt')
pieces = parse_pieces('pieces.txt')
solver = PuzzleSolver(board, pieces)


@app.route('/')
def index():
    """Serve the main player interface."""
    return render_template('player.html')


@app.route('/api/board')
def get_board():
    """Get board configuration."""
    # Convert board to JSON-serializable format
    grid_data = {}
    for coord, label in board.grid.items():
        grid_data[f"{coord.row},{coord.col}"] = label

    return jsonify({
        'width': board.width,
        'height': board.height,
        'grid': grid_data
    })


@app.route('/api/pieces')
def get_pieces():
    """Get all piece configurations."""
    pieces_data = []
    for piece in pieces:
        coords_list = [{'row': c.row, 'col': c.col} for c in piece.coords]
        pieces_data.append({
            'name': piece.name,
            'coords': coords_list
        })

    return jsonify(pieces_data)


@app.route('/api/target_coords', methods=['POST'])
def get_target_coords_api():
    """Get target coordinates for a given date."""
    data = request.json
    date_str = data.get('date', 'today')

    try:
        month, day, weekday = parse_date(date_str)
        target_coords = get_target_coords(board, month, day, weekday)

        coords_list = [{'row': c.row, 'col': c.col} for c in target_coords]

        return jsonify({
            'success': True,
            'month': month,
            'day': day,
            'weekday': weekday,
            'coords': coords_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/validate_placement', methods=['POST'])
def validate_placement():
    """Validate if a piece can be placed at a given position."""
    data = request.json

    # Parse piece coordinates
    piece_coords = {Coord(c['row'], c['col']) for c in data['piece_coords']}
    placement_coord = Coord(data['placement']['row'], data['placement']['col'])

    # Parse target coordinates (date squares to keep uncovered)
    target_coords = {Coord(c['row'], c['col']) for c in data['target_coords']}

    # Parse already occupied coordinates
    occupied = {Coord(c['row'], c['col']) for c in data['occupied']}

    # Create a temporary piece
    from calendar_puzzle import Piece
    temp_piece = Piece("temp", piece_coords)

    # Get absolute coordinates for this placement
    absolute_coords = temp_piece.place_at(placement_coord)

    # Check validity
    valid = True
    reason = ""

    for coord in absolute_coords:
        # Check if on board
        if not board.is_valid_coord(coord):
            valid = False
            reason = "Piece extends outside board boundaries"
            break

        # Check if already occupied
        if coord in occupied:
            valid = False
            reason = "Piece overlaps with already placed pieces"
            break

        # Check if covering target date
        if coord in target_coords:
            valid = False
            reason = "Piece covers the target date"
            break

    return jsonify({
        'valid': valid,
        'reason': reason
    })


@app.route('/api/check_win', methods=['POST'])
def check_win():
    """Check if the puzzle is solved."""
    data = request.json

    # Parse target and occupied coordinates
    target_coords = {Coord(c['row'], c['col']) for c in data['target_coords']}
    occupied = {Coord(c['row'], c['col']) for c in data['occupied']}

    # Check if all non-target squares are covered
    required_coverage = board.coords - target_coords
    is_complete = occupied == required_coverage

    return jsonify({
        'solved': is_complete,
        'covered': len(occupied),
        'required': len(required_coverage)
    })


@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    """Solve the puzzle for the given target coordinates."""
    data = request.json
    target_coords_list = data['target_coords']

    # Convert to set of Coord objects
    target_coords = {Coord(c['row'], c['col']) for c in target_coords_list}

    # Solve the puzzle
    solution = solver.solve(target_coords)

    if solution:
        # Format the solution for the frontend
        placements = []
        for piece_name, orientation_idx, origin, absolute_coords in solution.placements:
            piece_num = piece_name.replace('Piece', '')
            piece_letter = chr(ord('a') + int(piece_num) - 1) if piece_num.isdigit() else 'x'

            placements.append({
                'piece_name': piece_name,
                'piece_letter': piece_letter,
                'orientation_idx': orientation_idx,
                'origin': {'row': origin.row, 'col': origin.col},
                'coords': [{'row': c.row, 'col': c.col} for c in absolute_coords]
            })

        return jsonify({
            'success': True,
            'placements': placements
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No solution found for this date'
        })


@app.route('/difficulty_ratings.json')
def get_difficulty_ratings():
    """Serve the difficulty ratings JSON file."""
    try:
        with open('difficulty_ratings.json', 'r') as f:
            ratings = json.load(f)
        return jsonify(ratings)
    except FileNotFoundError:
        return jsonify({})


if __name__ == '__main__':
    print("=" * 60)
    print("CALENDAR PUZZLE - INTERACTIVE PLAYER")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open your browser to: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, port=8000)
