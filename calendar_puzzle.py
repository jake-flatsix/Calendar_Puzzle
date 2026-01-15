"""Calendar Puzzle - Core classes and parsers."""

from typing import Set, Tuple, List, Dict
from dataclasses import dataclass


@dataclass(frozen=True)
class Coord:
    """Represents a coordinate on the board."""
    row: int
    col: int

    def __add__(self, other):
        return Coord(self.row + other.row, self.col + other.col)


class Board:
    """Represents the puzzle board with date labels."""

    def __init__(self, grid: Dict[Coord, str], width: int, height: int):
        """
        Initialize the board.

        Args:
            grid: Dictionary mapping coordinates to labels (month/day/weekday/blank)
            width: Width of the board
            height: Height of the board
        """
        self.grid = grid
        self.width = width
        self.height = height
        self.coords = set(grid.keys())

    def is_valid_coord(self, coord: Coord) -> bool:
        """Check if a coordinate exists on the board."""
        return coord in self.coords

    def get_label(self, coord: Coord) -> str:
        """Get the label at a coordinate."""
        return self.grid.get(coord, None)

    def __repr__(self):
        return f"Board({self.width}x{self.height}, {len(self.coords)} squares)"


class Piece:
    """Represents a game piece that can be rotated and flipped."""

    def __init__(self, name: str, coords: Set[Coord]):
        """
        Initialize a piece.

        Args:
            name: Name of the piece
            coords: Set of relative coordinates that make up the piece
        """
        self.name = name
        self.coords = coords
        self._normalize()

    def _normalize(self):
        """Normalize piece so top-left corner is at (0, 0)."""
        if not self.coords:
            return
        min_row = min(c.row for c in self.coords)
        min_col = min(c.col for c in self.coords)
        self.coords = {Coord(c.row - min_row, c.col - min_col) for c in self.coords}

    def rotate_90(self) -> 'Piece':
        """Rotate piece 90 degrees clockwise."""
        rotated = {Coord(c.col, -c.row) for c in self.coords}
        return Piece(self.name, rotated)

    def flip_horizontal(self) -> 'Piece':
        """Flip piece horizontally."""
        flipped = {Coord(c.row, -c.col) for c in self.coords}
        return Piece(self.name, flipped)

    def get_all_orientations(self) -> List['Piece']:
        """Get all unique orientations (rotations + flips)."""
        orientations = []
        seen = set()

        current = self
        for _ in range(2):  # Normal and flipped
            for _ in range(4):  # 4 rotations
                key = frozenset(current.coords)
                if key not in seen:
                    seen.add(key)
                    orientations.append(current)
                current = current.rotate_90()
            current = current.flip_horizontal()

        return orientations

    def place_at(self, coord: Coord) -> Set[Coord]:
        """Get the absolute coordinates if this piece is placed at coord."""
        return {coord + c for c in self.coords}

    def __repr__(self):
        return f"Piece({self.name}, {len(self.coords)} squares)"


def parse_board(filename: str) -> Board:
    """
    Parse the board configuration file.

    Args:
        filename: Path to board.txt file

    Returns:
        Board object
    """
    grid = {}
    max_width = 0

    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]

    height = len(lines)

    for row_idx, line in enumerate(lines):
        # Split by whitespace
        cells = line.split()
        max_width = max(max_width, len(cells))

        for col_idx, label in enumerate(cells):
            coord = Coord(row_idx, col_idx)
            grid[coord] = label

    return Board(grid, max_width, height)


def parse_pieces(filename: str) -> List[Piece]:
    """
    Parse the pieces configuration file.

    Args:
        filename: Path to pieces.txt file

    Returns:
        List of Piece objects
    """
    pieces = []

    with open(filename, 'r') as f:
        content = f.read()

    # Split by piece definitions
    piece_blocks = content.strip().split('\n\n')

    for block in piece_blocks:
        lines = block.split('\n')
        if not lines:
            continue

        # First line is the piece name
        name = lines[0].rstrip(':')

        # Parse the shape
        coords = set()
        for row_idx, line in enumerate(lines[1:]):
            for col_idx, char in enumerate(line):
                if char == '#':
                    coords.add(Coord(row_idx, col_idx))

        if coords:
            pieces.append(Piece(name, coords))

    return pieces
