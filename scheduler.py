from start import start_scheduling
import sys

print("Arguments received= ", sys.argv)

pos_present = False
slots_present = False
files_needed = {}
for arg in sys.argv:
    if "=" in arg:
        kv_par = arg.split("=")
        files_needed[kv_par[0]] = kv_par[1]

if 'pos' not in files_needed:
    print("No files passed for POs, using default file: pos.csv")
    files_needed["pos"] = "pos.csv"


if 'slots' not in files_needed:
    print("No files passed for slots, using default file: slots.csv")
    files_needed["slots"] = "slots.csv"

slots_file_array = files_needed["slots"].split(",")
pos_file_array = files_needed["pos"].split(",")

start_scheduling(slots_file_array, pos_file_array)