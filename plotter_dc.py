#!/usr/bin/env bash
# thanks to everyone whose code was mined to teach ChatGPT

import pandas as pd
import matplotlib.pyplot as plt
import pathlib

# Read the CSV file into a DataFrame
csv_file = '903f1a91-09a6-4b50-9148-73dbb2655f58.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# downsample
df = df[::10]

# Plot the data
plt.figure(figsize=(16/2, 9/2))

# Plot each column
plt.plot(df['t[s]'], df['CH2[V]'], label='Power Supply Signal. Avg=15.4V')
plt.plot(df['t[s]'], df['CH3[V]'], label='Intesnity Control Signal. Avg=1.14V')
plt.plot(df['t[s]'], df['CH1[V]'], label='Emission Photodiode Signal. Avg=3.20V')

# Add labels and title
plt.xlabel('Time [s]')
plt.ylabel('DC Coupled Voltage [V]')
plt.title('In-house LED Driver Noise Analysis (@1A drive current)')
plt.legend()

# Turn on the grid
plt.grid(True)

# Set the y-axis limit to start at 0
plt.ylim(bottom=0)

# Ensure a tight layout
plt.tight_layout()

# Save the plot as an SVG file
svg_out =f'{csv_file}.svg'
print(f"Saving file://{pathlib.Path.cwd()/svg_out}")
plt.savefig(svg_out, format='svg')

# Show the plot
plt.show()