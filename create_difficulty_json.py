"""Convert difficulty CSV to a simple JSON format for JavaScript loading."""

import json
import csv

def main():
    """Convert CSV to JSON."""
    difficulties = {}

    with open('difficulty_analysis_2026_rated.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row['date']
            difficulties[date] = {
                'solutions': int(row['total_solutions']),
                'stars': int(row['difficulty_stars']),
                'label': row['difficulty_label']
            }

    # Save as JSON
    with open('difficulty_ratings.json', 'w') as f:
        json.dump(difficulties, f, indent=2)

    print(f"Created difficulty_ratings.json with {len(difficulties)} dates")
    print(f"\nSample entries:")
    for date in list(difficulties.keys())[:3]:
        print(f"  {date}: {difficulties[date]}")

if __name__ == '__main__':
    main()
