#!/usr/bin/env bash
# thanks to everyone whose code was mined to teach ChatGPT

import pandas as pd
import matplotlib.pyplot as plt
import pathlib

# Read the CSV file into a DataFrame
csv_file = '8c9fb488-8c1e-4f07-be15-54e837172bc9.csv'
df = pd.read_csv(csv_file)

# downsample
df = df[::10]

# Plot the data
plt.figure(figsize=(16/2, 9/2))

# Plot each column
plt.plot(df['t[s]'], 1000*df['CH2[V]'], label='Power Supply Signal. mVpp=428')
plt.plot(df['t[s]'], 1000*df['CH3[V]'], label='Intesnity Control Signal. mVpp=45.6')
plt.plot(df['t[s]'], 1000*df['CH1[V]'], label='Emission Photodiode Signal. mVpp=22.4')

# Add labels and title
plt.xlabel('Time [s]')
plt.ylabel('AC Coupled Voltage [mV]')
plt.title('In-house LED Driver Noise Analysis (@1A drive current)')
plt.legend()

# Turn on the grid
plt.grid(True)

# Ensure a tight layout
plt.tight_layout()

# Save the plot as an SVG file
svg_out =f'{csv_file}.svg'
print(f"Saving file://{pathlib.Path.cwd()/svg_out}")
plt.savefig(svg_out, format='svg')

# Show the plot
plt.show()