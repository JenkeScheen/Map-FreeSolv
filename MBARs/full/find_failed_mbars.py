#/bin/python

# quick script to find failed MBAR calculations. Of the ~460 calculations,
# ~100 have no MBAR value.

import matplotlib.pyplot as plt 
import seaborn as sns
import csv
import glob
import pandas as pd 
import numpy as np


legs = 		[
			"free",
			#"vac"
			]


est_errors = []

for leg in legs:
	result_lines = []

	mbar_paths = glob.glob(leg+"/*")
	# read through the MBAR output files:
	for path in mbar_paths:
		f = open(path, "r")
		for line in f:
			# read the line after the #MBAR keyword for the energy prediction: 
			if line.startswith("#MBAR"):
				name = path.split("/")[1].replace("_vacuum","").replace("_free", "")
				print(line.rstrip())

				result_lines.append([name, next(f)])
				#print("##########")
print(len(result_lines))
	# for line in result_lines:
	# 	# clean and make a list of the errors:
	# 	name = line[0]
	# 	result = line[1].split(", ")[1].split("  ")[0].replace(" \n", "")
	# 	est_errors.append([name, result, leg])