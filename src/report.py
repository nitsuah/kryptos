"""
Module for generating reports based on analysis results.
"""

import os

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')  # Use a non-GUI backend


def generate_report(results, cipher_name):
    '''Generate a report with frequency analysis and crib matches.'''
    frequencies = results.get('frequencies', {})
    cribs = results.get('cribs', [])
    output_dir = "reports"
    output_file = f"{output_dir}/{cipher_name}_report.png"

    # Ensure the reports directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate the frequency analysis plot
    plt.bar(frequencies.keys(), frequencies.values())
    plt.title(f"Frequency Analysis for {cipher_name}")
    plt.xlabel("Characters")
    plt.ylabel("Frequency")
    plt.savefig(output_file)
    plt.close()

    # Save a text summary of crib matches
    summary_file = f"{output_dir}/{cipher_name}_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"Crib Matches: {', '.join(cribs)}\n")
