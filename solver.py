"""Calendar Puzzle Solver using backtracking algorithm."""

from typing import Set, List, Optional, Dict
from calendar_puzzle import Board, Piece, Coord, parse_board, parse_pieces
from datetime import datetime


class GameState:
    """Represents the current state of the puzzle."""

    def __init__(self, board: Board, target_coords: Set[Coord]):
        """
        Initialize game state.

        Args:
            board: The puzzle board
            target_coords: Coordinates that must remain uncovered (the date)
        """
        self.board = board
        self.target_coords = target_coords
        self.occupied = set()  # Squares currently covered by pieces
        self.placements = []  # List of (piece_name, orientation_idx, coord) tuples

    def can_place(self, piece: Piece, coord: Coord) -> bool:
        """Check if a piece can be placed at the given coordinate."""
        absolute_coords = piece.place_at(coord)

        for abs_coord in absolute_coords:
            # Check if coordinate is on the board
            if not self.board.is_valid_coord(abs_coord):
                return False

            # Check if coordinate is already occupied
            if abs_coord in self.occupied:
                return False

            # Check if coordinate is a target (must remain uncovered)
            if abs_coord in self.target_coords:
                return False

        return True

    def place_piece(self, piece: Piece, coord: Coord, piece_name: str, orientation_idx: int):
        """Place a piece on the board."""
        absolute_coords = piece.place_at(coord)
        self.occupied.update(absolute_coords)
        self.placements.append((piece_name, orientation_idx, coord, absolute_coords))

    def remove_last_piece(self):
        """Remove the most recently placed piece."""
        if not self.placements:
            return

        _, _, _, absolute_coords = self.placements.pop()
        self.occupied.difference_update(absolute_coords)

    def is_complete(self) -> bool:
        """Check if all required squares are covered."""
        required_coverage = self.board.coords - self.target_coords
        return self.occupied == required_coverage

    def get_uncovered_coords(self) -> Set[Coord]:
        """Get coordinates that are not yet covered."""
        return (self.board.coords - self.target_coords) - self.occupied


class PuzzleSolver:
    """Solves the calendar puzzle using backtracking."""

    def __init__(self, board: Board, pieces: List[Piece]):
        """
        Initialize solver.

        Args:
            board: The puzzle board
            pieces: List of available pieces
        """
        self.board = board
        self.pieces = pieces
        self.piece_orientations = {}

        # Pre-compute all orientations for each piece
        for piece in pieces:
            self.piece_orientations[piece.name] = piece.get_all_orientations()

    def solve(self, target_coords: Set[Coord]) -> Optional[GameState]:
        """
        Solve the puzzle for given target coordinates.

        Args:
            target_coords: Coordinates that must remain uncovered

        Returns:
            GameState with solution, or None if no solution exists
        """
        state = GameState(self.board, target_coords)
        unused_pieces = list(self.pieces)

        if self._backtrack(state, unused_pieces):
            return state
        return None

    def _backtrack(self, state: GameState, unused_pieces: List[Piece]) -> bool:
        """
        Recursive backtracking to find a solution.

        Args:
            state: Current game state
            unused_pieces: Pieces not yet placed

        Returns:
            True if solution found, False otherwise
        """
        # Base case: all pieces placed
        if not unused_pieces:
            return state.is_complete()

        # Get next uncovered coordinate to fill (optimization)
        uncovered = state.get_uncovered_coords()
        if not uncovered:
            return state.is_complete()

        # Pick the first uncovered coordinate as anchor point
        target_coord = min(uncovered, key=lambda c: (c.row, c.col))

        # Try each remaining piece
        for piece_idx, piece in enumerate(unused_pieces):
            # Try all orientations of this piece
            orientations = self.piece_orientations[piece.name]

            for orientation_idx, oriented_piece in enumerate(orientations):
                # Try placing piece such that it covers the target coordinate
                # We need to try different positions of the piece
                for piece_coord in oriented_piece.coords:
                    # Calculate where to place piece origin so piece_coord covers target_coord
                    placement_coord = Coord(
                        target_coord.row - piece_coord.row,
                        target_coord.col - piece_coord.col
                    )

                    if state.can_place(oriented_piece, placement_coord):
                        # Place the piece
                        state.place_piece(oriented_piece, placement_coord, piece.name, orientation_idx)

                        # Recurse with remaining pieces
                        remaining = unused_pieces[:piece_idx] + unused_pieces[piece_idx + 1:]
                        if self._backtrack(state, remaining):
                            return True

                        # Backtrack
                        state.remove_last_piece()

        return False


def parse_date(date_str: str) -> tuple:
    """
    Parse date string and return (month_name, day_num, weekday_name).

    Args:
        date_str: Date in format 'YYYY-MM-DD' or 'MM-DD' or 'today'

    Returns:
        Tuple of (month_abbr, day_str, weekday_abbr)
    """
    if date_str.lower() == 'today':
        date_obj = datetime.now()
    else:
        # Try parsing different formats
        for fmt in ['%Y-%m-%d', '%m-%d']:
            try:
                if fmt == '%m-%d':
                    # Add current year
                    date_str_with_year = f"{datetime.now().year}-{date_str}"
                    date_obj = datetime.strptime(date_str_with_year, '%Y-%m-%d')
                else:
                    date_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD, MM-DD, or 'today'")

    # Get month abbreviation
    month_abbr = date_obj.strftime('%b')  # Jan, Feb, etc.

    # Get day number
    day_str = str(date_obj.day)

    # Get weekday abbreviation
    weekday_abbr = date_obj.strftime('%a')  # Mon, Tue, etc.

    return month_abbr, day_str, weekday_abbr


def get_target_coords(board: Board, month: str, day: str, weekday: str) -> Set[Coord]:
    """
    Find coordinates for the target date on the board.

    Args:
        board: The puzzle board
        month: Month abbreviation (e.g., 'Jan')
        day: Day number as string (e.g., '15')
        weekday: Weekday abbreviation (e.g., 'Mon')

    Returns:
        Set of coordinates for the target date
    """
    target_coords = set()

    for coord, label in board.grid.items():
        if label == month or label == day or label == weekday:
            target_coords.add(coord)

    if len(target_coords) != 3:
        raise ValueError(
            f"Expected 3 target coordinates, found {len(target_coords)} "
            f"for {month}/{day}/{weekday}"
        )

    return target_coords


def visualize_solution(state: GameState) -> str:
    """
    Create a visual representation of the solution.

    Args:
        state: Solved game state

    Returns:
        String representation of the board
    """
    # Create a mapping of coordinates to piece names
    coord_to_piece = {}
    for piece_name, orientation_idx, origin, absolute_coords in state.placements:
        for coord in absolute_coords:
            coord_to_piece[coord] = piece_name

    # Build the visualization
    lines = []
    for row in range(state.board.height):
        line_chars = []
        for col in range(state.board.width):
            coord = Coord(row, col)

            if not state.board.is_valid_coord(coord):
                line_chars.append('   ')
            elif coord in state.target_coords:
                label = state.board.get_label(coord)
                line_chars.append(f'{label:>3}')
            elif coord in coord_to_piece:
                piece_name = coord_to_piece[coord]
                # Use piece letter for visualization (Piece1->a, Piece2->b, etc.)
                piece_num = piece_name.replace('Piece', '')
                if piece_num.isdigit():
                    piece_letter = chr(ord('a') + int(piece_num) - 1)
                else:
                    piece_letter = 'x'  # fallback for unnamed pieces
                line_chars.append(f' {piece_letter} ')
            else:
                line_chars.append(' ? ')

        lines.append(''.join(line_chars))

    return '\n'.join(lines)
