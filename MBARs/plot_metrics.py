# quick script to plot some MBAR metrics to check if FreeSolv runs correctly.

import matplotlib.pyplot as plt 
import seaborn as sns
import csv
import glob
import pandas as pd 
import numpy as np


legs = ["free",
		"vac"
		]

est_errors = []
for leg in legs:
	result_lines = []

	mbar_paths = glob.glob(leg+"/*")
	for path in mbar_paths:
		f = open(path, "r")
		for line in f:
			if line.startswith("#MBAR"):

				result_lines.append(next(f))

	for line in result_lines:
		est_errors.append([line.split(", ")[1].split("  ")[0], leg])

	
df = pd.DataFrame(est_errors, columns=["error", "type"])


df = df.astype({"error" : float})
df.dropna(inplace=True)
df = df.loc[df["error"] < 1]
df_free = df.loc[df["type"] ==  "free"]
df_vac = df.loc[df["type"] ==  "vac"]

sns.distplot(df_free["error"], kde=True, hist=False, bins=1000, label="Free")
sns.distplot(df_vac["error"], kde=True, hist=False, bins=1000, label="Vacuum")

#plt.xscale("log")

#plt.xticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3])
plt.xlim(0, 1)
plt.ylim(0, 15)
plt.xlabel(r"MBAR estimator error")
plt.ylabel("Count")
plt.legend()
plt.show()