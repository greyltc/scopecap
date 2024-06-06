#!/usr/bin/env python

# thanks MiDi
# https://web.archive.org/web/20240605222741/https://www.eevblog.com/forum/testgear/download-speed-from-rigol-ds1054z-or-similar-oscilloscope-to-a-pc/25/

import pyvisa as visa	# needs a backend e.g. NI-VISA or PyVISA-py TODO: eliminate pyvisa dep
import sys
import time
from decimal import Decimal
import csv
from uuid import uuid4
import pathlib

#def ef(value, places=None):
#	return EngFormatter(sep="", places=places).format_eng(float(value)) #round(value, 4) - need to round in exp form

def crange(start,end,step):
	i = start
	while i < end-step+1:
		yield i, i+step-1
		i += step
	yield i, end

def wait_ready(instrument):
	#instrument.write("*OPC")
	instrument.write("*WAI")
	ready = instrument.query("*OPC?").strip()
	#print(ready)
	while ready != "1":													# never occured, needed?
		ready = instrument.query("*OPC?").strip()
		print(f"\n-------------------not ready: {ready}-----------------------")
		#pass

def is_error(instrument):
	wait_ready(instrument)
	status = instrument.query("*ESR?").strip()
	if status not in ('0', '1'):
		wait_ready(instrument)
		return instrument.query(":SYST:ERR?").strip()	#:SYSTem:ERRor[:NEXT]?
	else:
		return False

def connect(address):
	try:
		rm = visa.ResourceManager("@py")
		instrument = rm.open_resource(address, write_termination = '\n', read_termination = '\n')
	except Exception as e:
		print(f"Cannot open instrument: {str(e)}")
		sys.exit(-1)

	print(instrument.query("*IDN?").strip())
	return instrument

def checkstop(instrument):
	status = instrument.query(":TRIG:STAT?").strip()
	assert status == "STOP"


def screenshot(instrument):
	time.sleep(2)														# wait until all messages are gone (e.g. can operate now)
	start_time = time.time()
	screenshot = instrument.query_binary_values(":DISP:DATA? ON,OFF,PNG", datatype='B') #  ON,OFF,PNG - BMP is a bit faster
	stop_time = time.time()
	print(f"Screenshot took {stop_time - start_time:.3f}s")
	return screenshot

def read_data(instrument, ch: int = 1):
	mem_depth = int(instrument.query(":ACQ:MDEP?"))			# memory depth

	# :WAV needs to be en bloc, at least between STAR & STOP
	instrument.write(f":WAV:SOUR CHAN{int(ch)}")			# data from channel 1-4
	wait_ready(instrument)
	instrument.write(":WAV:MODE RAW")						# data from internal memory
	wait_ready(instrument)
	instrument.write(":WAV:FORM BYTE")						# data as byte
	data = []
	start_time = time.time()
	for interval in crange(1, mem_depth, 250_000):			# 250_000 is max chunk size for bytes
		#instrument.write(f":WAV:STAR {interval[0]}")		# start index of memory
		#instrument.write(f":WAV:STOP {interval[1]}")		# stop index of memory
		#data += (instrument.query_binary_values(f":WAV:DATA?", datatype='B')) # get the data, B = unsigned char
		data += (instrument.query_binary_values(f":WAV:STAR {interval[0]}\n:WAV:STOP {interval[1]}\n:WAV:DATA?", datatype='B')) # get the data, B = unsigned char
		print(f"{len(data)/mem_depth:3.0%} memory read in {time.time() - start_time:.3f}s ({len(data)}/{mem_depth}) reading: {interval[0]}:{interval[1]}", end="\r")
	print()
	# debug
	print(mem_depth)
	sps = float(instrument.query(":ACQ:SRAT?").strip())		# query the current sample rate in Sa/s
	print(f"SPS: {sps}")
	#timebase_scale = float(instrument.query(":TIM:SCAL?").strip())		# query timebase scale
	#print(f"Timebase scale: {ef(timebase_scale)}s/div")

	return data, sps

def scale_data(instrument, data):
	wait_ready(instrument)
	mem_depth = Decimal(instrument.query(":ACQ:MDEP?").strip()).normalize()				# memory depth
	wait_ready(instrument)
	wf_parameters = instrument.query(":WAV:PRE?").strip().split(",")					# get waveform parameters: <format>,<type>,<points>,<count>,<xincrement>,<xorigin>,<xreference>,<yincrement>,<yorigin>,<yreference>
	print(f"Waveform parameters: {wf_parameters}")
	while Decimal(wf_parameters[2]).normalize() not in (mem_depth, mem_depth/2, mem_depth/3, mem_depth/4):
		wait_ready(instrument)
		wf_parameters = instrument.query(":WAV:PRE?").strip().split(",")
		print(f"Waveform parameters: {wf_parameters}")
	yincrement = float(wf_parameters[7])
	yorigin = float(wf_parameters[8])
	yreference = float(wf_parameters[9])
	scaled_data = []
	for byte in data:
		scaled_data.append((float(byte) - yorigin - yreference) * yincrement)
	return scaled_data

def main():
	address = "TCPIP0::192.168.53.63::5555::SOCKET"  # enter your scope's connection string here
	channels = (1, 2, 3)  # enter the channels here you'd like to fetch
	scope = connect(address)
	checkstop(scope)  # only do this if the scope is stopped
	last_sps = 0
	csv_header = []
	chan_data =[]

	print("Fetching buffer data...")
	for chan in channels:
		csv_header.append(f"CH{chan}[V]")
		raw_dat, sps = read_data(scope, chan)
		chan_data.append(scale_data(scope, raw_dat))

		if not last_sps:
			last_sps = sps
		else:
			assert last_sps == sps, "Somehow sample rate doesn't match across channels"

	print("Fetching screenshot...")
	sc = screenshot(scope)

	# generate time
	#TODO: make the trigger moment t=0
	n_samples = len(raw_dat)
	dt = 1/sps
	timepoints = [x*dt for x in range(n_samples)]
	csv_header = ["t[s]"] + csv_header
	chan_data = [timepoints] + chan_data

	# dump to disk
	this_run = uuid4()

	png_file_name = f"{this_run}.png"
	print(f"Writing screenshot to file://{pathlib.Path.cwd()/png_file_name}")
	with open(png_file_name, mode='wb') as file:
		file.write(bytearray(sc))

	csv_file_name = f"{this_run}.csv"
	print(f"Writing data to file://{pathlib.Path.cwd()/csv_file_name}")
	with open(csv_file_name, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(csv_header)
		writer.writerows(zip(*chan_data))
	print(f"Done.")


if __name__ == "__main__":
	main()