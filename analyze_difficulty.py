"""Analyze puzzle difficulty for all dates in 2026."""

import time
import json
import csv
from datetime import datetime, timedelta
from typing import Set, List, Optional, Dict, Tuple
from calendar_puzzle import Board, Piece, Coord, parse_board, parse_pieces
from solver import GameState, get_target_coords


class InstrumentedSolver:
    """Solver with metrics collection for difficulty analysis."""

    def __init__(self, board: Board, pieces: List[Piece]):
        self.board = board
        self.pieces = pieces
        self.piece_orientations = {}

        # Pre-compute all orientations for each piece
        for piece in pieces:
            self.piece_orientations[piece.name] = piece.get_all_orientations()

        # Metrics
        self.reset_metrics()

    def reset_metrics(self):
        """Reset all metrics for a new solve."""
        self.total_solutions = 0
        self.time_to_first_solution = None
        self.total_backtracks = 0
        self.max_depth_reached = 0
        self.nodes_explored = 0
        self.start_time = None
        self.first_piece_valid_positions = 0
        self.second_piece_avg_valid_positions = 0
        self.solutions = []

    def count_all_solutions(self, target_coords: Set[Coord]) -> Dict:
        """
        Count all possible solutions and collect metrics.

        Returns:
            Dictionary with all metrics
        """
        self.reset_metrics()
        self.start_time = time.time()

        state = GameState(self.board, target_coords)
        unused_pieces = list(self.pieces)

        # Skip expensive branching measurement for performance
        # self._measure_early_branching(state, unused_pieces, target_coords)

        # Find all solutions
        self._backtrack_count(state, unused_pieces, depth=0)

        total_time = time.time() - self.start_time

        return {
            'total_solutions': self.total_solutions,
            'time_to_first_solution': self.time_to_first_solution,
            'total_time': total_time,
            'total_backtracks': self.total_backtracks,
            'max_depth_reached': self.max_depth_reached,
            'nodes_explored': self.nodes_explored,
            'first_piece_valid_positions': self.first_piece_valid_positions,
            'second_piece_avg_valid_positions': self.second_piece_avg_valid_positions,
        }

    def _measure_early_branching(self, state: GameState, unused_pieces: List[Piece], target_coords: Set[Coord]):
        """Measure how many valid positions exist for the first few pieces."""
        # Count valid positions for first piece
        uncovered = state.get_uncovered_coords()
        if not uncovered:
            return

        target_coord = min(uncovered, key=lambda c: (c.row, c.col))
        first_piece = unused_pieces[0]
        orientations = self.piece_orientations[first_piece.name]

        valid_positions = 0
        for oriented_piece in orientations:
            for piece_coord in oriented_piece.coords:
                placement_coord = Coord(
                    target_coord.row - piece_coord.row,
                    target_coord.col - piece_coord.col
                )
                if state.can_place(oriented_piece, placement_coord):
                    valid_positions += 1

        self.first_piece_valid_positions = valid_positions

        # Measure average valid positions for second piece across all first piece placements
        second_piece_counts = []
        for oriented_piece in orientations:
            for piece_coord in oriented_piece.coords:
                placement_coord = Coord(
                    target_coord.row - piece_coord.row,
                    target_coord.col - piece_coord.col
                )
                if state.can_place(oriented_piece, placement_coord):
                    # Temporarily place first piece
                    state.place_piece(oriented_piece, placement_coord, first_piece.name, 0)

                    # Count valid positions for second piece
                    uncovered2 = state.get_uncovered_coords()
                    if uncovered2:
                        target_coord2 = min(uncovered2, key=lambda c: (c.row, c.col))
                        second_piece = unused_pieces[1]
                        orientations2 = self.piece_orientations[second_piece.name]

                        valid_positions2 = 0
                        for oriented_piece2 in orientations2:
                            for piece_coord2 in oriented_piece2.coords:
                                placement_coord2 = Coord(
                                    target_coord2.row - piece_coord2.row,
                                    target_coord2.col - piece_coord2.col
                                )
                                if state.can_place(oriented_piece2, placement_coord2):
                                    valid_positions2 += 1

                        second_piece_counts.append(valid_positions2)

                    # Remove first piece
                    state.remove_last_piece()

        if second_piece_counts:
            self.second_piece_avg_valid_positions = sum(second_piece_counts) / len(second_piece_counts)

    def _backtrack_count(self, state: GameState, unused_pieces: List[Piece], depth: int) -> None:
        """Recursive backtracking to count all solutions."""
        self.nodes_explored += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)

        # Base case: all pieces placed
        if not unused_pieces:
            if state.is_complete():
                self.total_solutions += 1
                if self.time_to_first_solution is None:
                    self.time_to_first_solution = time.time() - self.start_time
            return

        # Get next uncovered coordinate
        uncovered = state.get_uncovered_coords()
        if not uncovered:
            if state.is_complete():
                self.total_solutions += 1
                if self.time_to_first_solution is None:
                    self.time_to_first_solution = time.time() - self.start_time
            return

        # Pick first uncovered coordinate as anchor
        target_coord = min(uncovered, key=lambda c: (c.row, c.col))

        found_any_placement = False

        # Try each remaining piece
        for piece_idx, piece in enumerate(unused_pieces):
            orientations = self.piece_orientations[piece.name]

            # Try all orientations
            for orientation_idx, oriented_piece in enumerate(orientations):
                # Try placing so piece covers target coordinate
                for piece_coord in oriented_piece.coords:
                    placement_coord = Coord(
                        target_coord.row - piece_coord.row,
                        target_coord.col - piece_coord.col
                    )

                    if state.can_place(oriented_piece, placement_coord):
                        found_any_placement = True

                        # Place piece
                        state.place_piece(oriented_piece, placement_coord, piece.name, orientation_idx)

                        # Dead-end detection optimization
                        if len(state.placements) >= 5 and state.has_dead_end():
                            # Dead end detected, skip this branch
                            state.remove_last_piece()
                            continue

                        # Recurse with remaining pieces
                        remaining = unused_pieces[:piece_idx] + unused_pieces[piece_idx + 1:]
                        self._backtrack_count(state, remaining, depth + 1)

                        # Backtrack
                        state.remove_last_piece()

        # If no placement was found at this node, it's a dead end (backtrack)
        if not found_any_placement:
            self.total_backtracks += 1


def analyze_all_dates_2026():
    """Analyze puzzle difficulty for all dates in 2026."""
    print("Loading board and pieces...")
    board = parse_board('board.txt')
    pieces = parse_pieces('pieces.txt')

    print(f"Board: {board}")
    print(f"Pieces: {len(pieces)}")

    solver = InstrumentedSolver(board, pieces)

    # Load existing partial results if available
    results = []
    completed_dates = set()
    try:
        with open('difficulty_analysis_2026_partial.json', 'r') as f:
            results = json.load(f)
            completed_dates = set(r['date'] for r in results)
            print(f"Loaded {len(results)} previously completed dates")
            print(f"Resuming from {len(results) + 1}/365...")
    except FileNotFoundError:
        print("No partial results found, starting from beginning")

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 12, 31)
    current_date = start_date

    total_days = (end_date - start_date).days + 1
    processed = 0

    print(f"\nAnalyzing {total_days} dates in 2026...\n")

    while current_date <= end_date:
        processed += 1

        # Parse date
        date_str = current_date.strftime('%Y-%m-%d')
        month_abbr = current_date.strftime('%b')
        day_str = str(current_date.day)
        weekday_abbr = current_date.strftime('%a')

        # Skip if already completed
        if date_str in completed_dates:
            current_date += timedelta(days=1)
            continue

        # Get target coordinates
        try:
            target_coords = get_target_coords(board, month_abbr, day_str, weekday_abbr)
        except ValueError as e:
            print(f"Skipping {date_str}: {e}")
            current_date += timedelta(days=1)
            continue

        # Solve and collect metrics
        print(f"[{processed}/{total_days}] Analyzing {date_str} ({month_abbr} {day_str}, {weekday_abbr})...", end=' ', flush=True)

        metrics = solver.count_all_solutions(target_coords)

        result = {
            'date': date_str,
            'month': month_abbr,
            'day': day_str,
            'weekday': weekday_abbr,
            'total_solutions': metrics['total_solutions'],
            'time_to_first_solution_ms': round(metrics['time_to_first_solution'] * 1000, 2) if metrics['time_to_first_solution'] else None,
            'total_time_sec': round(metrics['total_time'], 2),
            'total_backtracks': metrics['total_backtracks'],
            'max_depth_reached': metrics['max_depth_reached'],
            'nodes_explored': metrics['nodes_explored'],
        }

        results.append(result)

        print(f"{metrics['total_solutions']} solutions, {round(metrics['time_to_first_solution'] * 1000, 1)}ms to first")

        current_date += timedelta(days=1)

    # Save results
    print("\nSaving results...")

    # Save as JSON
    with open('difficulty_analysis_2026.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Save as CSV
    with open('difficulty_analysis_2026.csv', 'w', newline='') as f:
        fieldnames = [
            'date', 'month', 'day', 'weekday',
            'total_solutions', 'time_to_first_solution_ms', 'total_time_sec',
            'total_backtracks', 'max_depth_reached', 'nodes_explored'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    solutions = [r['total_solutions'] for r in results]
    time_to_first = [r['time_to_first_solution_ms'] for r in results if r['time_to_first_solution_ms']]
    backtracks = [r['total_backtracks'] for r in results]

    print(f"\nTotal Solutions:")
    print(f"  Min: {min(solutions)}")
    print(f"  Max: {max(solutions)}")
    print(f"  Avg: {sum(solutions) / len(solutions):.1f}")
    print(f"  Median: {sorted(solutions)[len(solutions)//2]}")

    print(f"\nTime to First Solution (ms):")
    print(f"  Min: {min(time_to_first):.2f}")
    print(f"  Max: {max(time_to_first):.2f}")
    print(f"  Avg: {sum(time_to_first) / len(time_to_first):.2f}")

    print(f"\nTotal Backtracks:")
    print(f"  Min: {min(backtracks)}")
    print(f"  Max: {max(backtracks)}")
    print(f"  Avg: {sum(backtracks) / len(backtracks):.1f}")

    # Find easiest and hardest puzzles
    print("\n" + "="*80)
    print("EASIEST PUZZLES (Most solutions)")
    print("="*80)
    sorted_by_solutions = sorted(results, key=lambda r: r['total_solutions'], reverse=True)
    for r in sorted_by_solutions[:10]:
        print(f"  {r['date']}: {r['total_solutions']} solutions")

    print("\n" + "="*80)
    print("HARDEST PUZZLES (Fewest solutions)")
    print("="*80)
    for r in sorted_by_solutions[-10:]:
        print(f"  {r['date']}: {r['total_solutions']} solutions")

    print("\n" + "="*80)
    print("FASTEST TO SOLVE (Time to first solution)")
    print("="*80)
    sorted_by_time = sorted([r for r in results if r['time_to_first_solution_ms']],
                           key=lambda r: r['time_to_first_solution_ms'])
    for r in sorted_by_time[:10]:
        print(f"  {r['date']}: {r['time_to_first_solution_ms']:.2f}ms")

    print("\n" + "="*80)
    print(f"\nResults saved to:")
    print(f"  - difficulty_analysis_2026.json")
    print(f"  - difficulty_analysis_2026.csv")
    print()


if __name__ == '__main__':
    analyze_all_dates_2026()
