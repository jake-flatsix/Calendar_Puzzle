"""Test script to verify board and piece parsing."""

from calendar_puzzle import parse_board, parse_pieces


def visualize_piece(piece):
    """Display a piece in ASCII format."""
    if not piece.coords:
        return

    max_row = max(c.row for c in piece.coords)
    max_col = max(c.col for c in piece.coords)

    for row in range(max_row + 1):
        line = ""
        for col in range(max_col + 1):
            from calendar_puzzle import Coord
            if Coord(row, col) in piece.coords:
                line += "#"
            else:
                line += " "
        print(line)


def main():
    print("=" * 60)
    print("PARSING BOARD")
    print("=" * 60)

    board = parse_board('board.txt')
    print(f"\n{board}")
    print(f"Total squares: {len(board.coords)}")

    # Count different label types
    months = []
    days = []
    weekdays = []
    blanks = []

    for coord, label in board.grid.items():
        if label == '.':
            blanks.append(label)
        elif label.isdigit():
            days.append(label)
        elif len(label) == 3 and label[0].isupper():
            if label in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                weekdays.append(label)
            else:
                months.append(label)

    print(f"\nMonths ({len(months)}): {sorted(months)}")
    print(f"Days ({len(days)}): {sorted(days, key=int)}")
    print(f"Weekdays ({len(weekdays)}): {weekdays}")
    print(f"Blanks ({len(blanks)}): {len(blanks)}")

    print("\n" + "=" * 60)
    print("PARSING PIECES")
    print("=" * 60)

    pieces = parse_pieces('pieces.txt')
    print(f"\nTotal pieces: {len(pieces)}")
    print(f"Total squares: {sum(len(p.coords) for p in pieces)}")

    for piece in pieces:
        print(f"\n{piece}:")
        visualize_piece(piece)

        # Test orientations
        orientations = piece.get_all_orientations()
        print(f"  Unique orientations: {len(orientations)}")

    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    # Check if the puzzle is solvable
    total_board_squares = len(board.coords)
    total_piece_squares = sum(len(p.coords) for p in pieces)
    uncovered_squares = 3  # The target date (month + day + weekday)

    print(f"\nBoard squares: {total_board_squares}")
    print(f"Piece squares: {total_piece_squares}")
    print(f"Uncovered (date): {uncovered_squares}")
    print(f"Expected coverage: {total_board_squares - uncovered_squares}")

    if total_piece_squares == total_board_squares - uncovered_squares:
        print("✓ Puzzle dimensions are valid!")
    else:
        print(f"✗ Mismatch! Difference: {total_piece_squares - (total_board_squares - uncovered_squares)}")


if __name__ == '__main__':
    main()
