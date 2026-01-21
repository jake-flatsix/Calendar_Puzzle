"""Add difficulty ratings to the puzzle analysis data."""

import json
import csv
from typing import List, Dict


def calculate_difficulty_rating(puzzle: Dict, all_puzzles: List[Dict]) -> Dict:
    """
    Calculate difficulty rating based on solution count.

    Rating scale:
    - 5 stars (Expert): Very few solutions (most constrained)
    - 4 stars (Hard): Below average solutions
    - 3 stars (Medium): Average number of solutions
    - 2 stars (Easy): Above average solutions
    - 1 star (Very Easy): Many solutions (least constrained)
    """
    # Extract metrics
    solution_counts = [p['total_solutions'] for p in all_puzzles]
    times = [p['time_to_first_solution_ms'] for p in all_puzzles if p['time_to_first_solution_ms']]

    # Sort for percentile calculation
    solution_counts_sorted = sorted(solution_counts)
    times_sorted = sorted(times)

    # Calculate percentiles (lower percentile for solutions = harder)
    solutions = puzzle['total_solutions']
    time_ms = puzzle['time_to_first_solution_ms']

    # Percentile for solutions (lower count = lower percentile = harder)
    solution_percentile = solution_counts_sorted.index(solutions) / len(solution_counts_sorted)

    # Percentile for time (higher time = higher percentile = harder)
    if time_ms:
        time_percentile = times_sorted.index(time_ms) / len(times_sorted)
    else:
        time_percentile = 0.5  # Default to middle if no time data

    # Combined difficulty score (0-1, where 1 is hardest)
    # Weight: 100% solution count
    difficulty_score = (1 - solution_percentile)

    # Map to star rating (1-5)
    if difficulty_score >= 0.8:
        stars = 5
        label = "Expert"
    elif difficulty_score >= 0.6:
        stars = 4
        label = "Hard"
    elif difficulty_score >= 0.4:
        stars = 3
        label = "Medium"
    elif difficulty_score >= 0.2:
        stars = 2
        label = "Easy"
    else:
        stars = 1
        label = "Very Easy"

    return {
        'difficulty_score': round(difficulty_score, 4),
        'difficulty_stars': stars,
        'difficulty_label': label,
        'solution_percentile': round(solution_percentile, 4),
        'time_percentile': round(time_percentile, 4)
    }


def main():
    """Load data, calculate ratings, and save updated files."""
    print("Loading difficulty analysis data...")

    with open('difficulty_analysis_2026.json', 'r') as f:
        puzzles = json.load(f)

    print(f"Loaded {len(puzzles)} puzzles")
    print("\nCalculating difficulty ratings...")

    # Calculate ratings for each puzzle
    for puzzle in puzzles:
        rating = calculate_difficulty_rating(puzzle, puzzles)
        puzzle.update(rating)

    # Save updated JSON
    with open('difficulty_analysis_2026_rated.json', 'w') as f:
        json.dump(puzzles, f, indent=2)

    # Save updated CSV
    with open('difficulty_analysis_2026_rated.csv', 'w', newline='') as f:
        fieldnames = [
            'date', 'month', 'day', 'weekday',
            'total_solutions', 'time_to_first_solution_ms',
            'difficulty_stars', 'difficulty_label', 'difficulty_score'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(puzzles)

    # Print statistics
    print("\n" + "="*80)
    print("DIFFICULTY RATING DISTRIBUTION")
    print("="*80)

    star_counts = {}
    for puzzle in puzzles:
        stars = puzzle['difficulty_stars']
        star_counts[stars] = star_counts.get(stars, 0) + 1

    for stars in sorted(star_counts.keys()):
        label = puzzles[0]['difficulty_label'] if stars == puzzles[0]['difficulty_stars'] else ""
        for p in puzzles:
            if p['difficulty_stars'] == stars:
                label = p['difficulty_label']
                break
        count = star_counts[stars]
        percentage = count / len(puzzles) * 100
        print(f"  {'★' * stars}{'☆' * (5-stars)} ({stars} star - {label:12s}): {count:3d} puzzles ({percentage:.1f}%)")

    # Show examples from each difficulty level
    print("\n" + "="*80)
    print("EXAMPLE PUZZLES BY DIFFICULTY")
    print("="*80)

    for stars in [5, 4, 3, 2, 1]:
        puzzles_at_level = [p for p in puzzles if p['difficulty_stars'] == stars]
        if puzzles_at_level:
            # Show a few examples
            print(f"\n{stars} Star ({puzzles_at_level[0]['difficulty_label']}):")
            for puzzle in sorted(puzzles_at_level, key=lambda p: p['difficulty_score'], reverse=True)[:3]:
                print(f"  {puzzle['date']}: {puzzle['total_solutions']:4d} solutions, "
                      f"{puzzle['time_to_first_solution_ms']:8.1f}ms (score: {puzzle['difficulty_score']:.3f})")

    print("\n" + "="*80)
    print(f"\nResults saved to:")
    print(f"  - difficulty_analysis_2026_rated.json")
    print(f"  - difficulty_analysis_2026_rated.csv")
    print()


if __name__ == '__main__':
    main()
