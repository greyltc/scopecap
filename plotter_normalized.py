#!/usr/bin/env bash
# thanks to everyone whose code was mined to teach ChatGPT

import pandas as pd
import matplotlib.pyplot as plt
import pathlib

# Read the CSV file into a DataFrame
csv_file = '8c9fb488-8c1e-4f07-be15-54e837172bc9.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# downsample
df = df[::10]

# Plot the data
plt.figure(figsize=(16/2, 9/2))

# Plot each column
plt.plot(df['t[s]'], df['CH2[V]']/15.4+1, label='Power Supply Signal')
plt.plot(df['t[s]'], df['CH3[V]']/1.14+1, label='Intesnity Control Signal')
plt.plot(df['t[s]'], df['CH1[V]']/3.2+1, label='Emission Photodiode Signal')

# Add labels and title
plt.xlabel('Time [s]')
plt.ylabel('AC Coupled Signal Normalzed By DC Average')
plt.title('In-house LED Driver Noise Analysis (@1A drive current)')
plt.legend()

# Turn on the grid
plt.grid(True)

# Ensure a tight layout
plt.tight_layout()

# Save the plot as an SVG file
svg_out =f'normaized_{csv_file}.svg'
print(f"Saving file://{pathlib.Path.cwd()/svg_out}")
plt.savefig(svg_out, format='svg')

# Show the plot
plt.show()