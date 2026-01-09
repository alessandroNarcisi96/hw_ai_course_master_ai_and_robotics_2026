#!/usr/bin/env python3
"""
Main script to run all experiments for the AI homework.
Reads Sokoban levels from a folder.
"""

import os
from experiments import ExperimentRunner


def load_levels(levels_dir="levels"):
    """Load all .txt Sokoban levels from a directory."""
    if not os.path.isdir(levels_dir):
        raise FileNotFoundError(f"Levels directory not found: {levels_dir}")

    level_files = [
        os.path.join(levels_dir, f)
        for f in sorted(os.listdir(levels_dir))
        if f.endswith(".txt")
    ]

    if not level_files:
        raise RuntimeError(f"No .txt level files found in {levels_dir}")

    print(f"Loaded {len(level_files)} level files from {levels_dir}/")
    return level_files


def main():
    """Run complete experiment suite."""
    print("=" * 70)
    print("ARTIFICIAL INTELLIGENCE HOMEWORK - SOKOBAN SOLVER")
    print("=" * 70)

    # Load levels from folder
    level_files = load_levels("levels")

    # Create experiment runner
    runner = ExperimentRunner()

    # Run experiments
    print("\nRunning experiments...")

    # A* experiments
    runner.run_a_star_on_levels(level_files, timeout=60)

    # CSP experiments
    runner.run_csp_on_levels(level_files, timeout=30)

    # Save results
    runner.save_results()

    # Generate plots
    runner.generate_plots()

    # Print summary
    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)

    # A* summary
    if runner.a_star_results:
        successful = sum(1 for r in runner.a_star_results if r.get("success"))
        total = len(runner.a_star_results)
        print(f"A* Results: {successful}/{total} successful")

        heuristic_stats = {}
        for result in runner.a_star_results:
            h = result.get("heuristic", "unknown")
            heuristic_stats.setdefault(h, {"success": 0, "total": 0, "times": []})

            heuristic_stats[h]["total"] += 1
            if result.get("success"):
                heuristic_stats[h]["success"] += 1
                if "total_time" in result:
                    heuristic_stats[h]["times"].append(result["total_time"])

        for h, stats in heuristic_stats.items():
            success_rate = 100 * stats["success"] / stats["total"]
            avg_time = (
                sum(stats["times"]) / len(stats["times"])
                if stats["times"]
                else 0
            )
            print(f"  {h}: {success_rate:.1f}% success, avg time: {avg_time:.3f}s")

    # CSP summary
    if runner.csp_results:
        successful = sum(1 for r in runner.csp_results if r.get("success"))
        total = len(runner.csp_results)
        print(f"\nCSP Results: {successful}/{total} successful")

    print("\n" + "=" * 70)
    print("EXPERIMENTS COMPLETED!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - results/a_star_results.json")
    print("  - results/csp_results.json")
    print("  - results/experiment_plots.png")
    print("\nReady to write report!")


if __name__ == "__main__":
    main()
