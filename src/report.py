import os
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt

def generate_report(results, cipher_name):
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
    with open(summary_file, "w") as f:
        f.write(f"Crib Matches: {', '.join(cribs)}\n")