#!/usr/bin/env python3
"""Main script to solve the calendar puzzle for a given date."""

import sys
import time
from calendar_puzzle import parse_board, parse_pieces
from solver import PuzzleSolver, parse_date, get_target_coords, visualize_solution


def main():
    """Main entry point for the solver."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python solve_puzzle.py <date>")
        print("  date: 'today', 'MM-DD', or 'YYYY-MM-DD'")
        print("\nExamples:")
        print("  python solve_puzzle.py today")
        print("  python solve_puzzle.py 01-14")
        print("  python solve_puzzle.py 2026-12-25")
        sys.exit(1)

    date_str = sys.argv[1]

    print("=" * 60)
    print("CALENDAR PUZZLE SOLVER")
    print("=" * 60)

    # Parse date
    try:
        month, day, weekday = parse_date(date_str)
        print(f"\nTarget date: {month} {day}, {weekday}")
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)

    # Load board and pieces
    print("\nLoading puzzle configuration...")
    board = parse_board('board.txt')
    pieces = parse_pieces('pieces.txt')

    print(f"  Board: {len(board.coords)} squares")
    print(f"  Pieces: {len(pieces)} pieces ({sum(len(p.coords) for p in pieces)} squares)")

    # Get target coordinates
    try:
        target_coords = get_target_coords(board, month, day, weekday)
        print(f"  Target coordinates: {len(target_coords)}")
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)

    # Solve the puzzle
    print("\nSolving...")
    solver = PuzzleSolver(board, pieces)

    start_time = time.time()
    solution = solver.solve(target_coords)
    elapsed_time = time.time() - start_time

    if solution:
        print(f"✓ Solution found in {elapsed_time:.2f} seconds!")
        print(f"\nPieces placed: {len(solution.placements)}")

        # Show piece placements
        print("\nPiece placements:")
        for piece_name, orientation_idx, coord, _ in solution.placements:
            print(f"  {piece_name}: orientation {orientation_idx} at ({coord.row}, {coord.col})")

        # Visualize the solution
        print("\n" + "=" * 60)
        print("SOLUTION")
        print("=" * 60)
        print(f"\nTarget date: {month} {day}, {weekday}\n")
        print(visualize_solution(solution))
        print("\nLegend:")
        print("  Letters = Piece placements (a-j)")
        print("  Labels = Uncovered date squares")

    else:
        print(f"✗ No solution found (searched for {elapsed_time:.2f} seconds)")
        print("\nThis could mean:")
        print("  - The puzzle is unsolvable for this date")
        print("  - There's an error in the board/piece configuration")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
