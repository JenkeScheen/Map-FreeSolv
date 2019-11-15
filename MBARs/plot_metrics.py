# quick script to plot some MBAR metrics to check if FreeSolv runs correctly.

import matplotlib.pyplot as plt 
import seaborn as sns
import csv
import glob
import pandas as pd 
import numpy as np
from rdkit.Chem import AllChem, Descriptors, rdMolAlign, rdDepictor, rdmolfiles, rdmolops


def full_vs_subsampled_mbar():
	mbar_types = [
				"full", 
				"subsampling"
				]
	 			
	legs = [
			"free", 
			"vac"
			]

	def get_lowest_logp(perturbation_names):
		# given a perturbation, compute the total polarity and change in polarity.
		def read_lig_pdb(lig_name):
			mol_path = "../ligands/"+lig_name+".pdb"
			mol = rdmolfiles.MolFromPDBFile(
										mol_path, 
										sanitize=False
										)
			return mol


		logPs = []
		for pert in perturbation_names:
			ligA = pert.split("~")[0]
			ligB = pert.split("~")[1]
			ligA, ligB = read_lig_pdb(ligA), read_lig_pdb(ligB)


			lowest_logP = min((Descriptors.MolLogP(ligA), Descriptors.MolLogP(ligB)))
			logPs.append(lowest_logP)
		return logPs

	for mbar_type in mbar_types:

		est_errors = []
		for leg in legs:
			result_lines = []

			mbar_paths = glob.glob(mbar_type+"/"+leg+"/*")
			# read through the MBAR output files:
			for path in mbar_paths:
				f = open(path, "r")
				for line in f:
					# read the line after the #MBAR keyword for the energy prediction: 
					if line.startswith("#MBAR"):

						name = path.split("/")[2].replace("_vacuum","").replace("_free", "")
						result_lines.append([name, next(f)])

			for line in result_lines:
				# clean and make a list of the errors:
				name = line[0]
				result = line[1].split(", ")[1].split("  ")[0].replace(" \n", "")
				est_errors.append([name, result, leg])

		# prepare the data for plotting:
		df = pd.DataFrame(est_errors, columns=["pert", "error", "type"])
		logPs = get_lowest_logp(list(df["pert"]))
		df["Lowest LogP"] = logPs


		df = df.astype({"error" : float})
		df = df.set_index("pert")
		df.dropna(inplace=True)
		df = df.loc[df["error"] < 0.5]
		df_free = df.loc[df["type"] ==  "free"]
		df_vac = df.loc[df["type"] ==  "vac"]


		if mbar_type == "full":
			print(df_free.sort_values(by=["error"]))
			print(df_vac.sort_values(by=["error"]))

			sns.scatterplot(df_free["error"], df_vac["error"])
			plt.xlabel(r"Solvated leg MBAR error [kcal$\cdot$mol$^{-1}$]")
			plt.ylabel(r"Vacuum leg MBAR error [kcal$\cdot$mol$^{-1}$]")
			# plt.xlim(0, 0.5)
			# plt.ylim(0, 0.5)
			plt.show()

		# #initialise double-framed plot:
		# f, axes = plt.subplots(1,2)

		# #build the left-hand side density plot:
		# sns.distplot(df_free["error"], kde=True, hist=False, bins=1000, label="Free", ax=axes[0])
		# sns.distplot(df_vac["error"], kde=True, hist=False, bins=1000, label="Vacuum", ax=axes[0])

		# axes[0].set_xlim(0, 1.5)
		# axes[0].set_ylim(0, 12)
		# axes[0].set_xlabel(r"MBAR estimator error [kcal$\cdot$mol$^{-1}$]")
		# axes[0].set_ylabel("Density")
		# axes[0].legend()

		# # build the right-hand side scatterplot:
		# df_vac.rename(columns={'error':'error_vac'}, inplace=True)
		# df_free.rename(columns={'error':'error_free'}, inplace=True)

		# df_vac = df_vac.drop(["Lowest LogP"], axis=1)

		# result = pd.concat([df_vac, df_free], axis=1).dropna()


		# sns.scatterplot(result["error_free"], result["error_vac"], hue=result["Lowest LogP"], ax=axes[1], palette="coolwarm")
		# axes[1].set_xlim(0, 1.5)
		# axes[1].set_ylim(0, 1.5)

		# axes[1].set_xlabel(r"Solvated leg MBAR error [kcal$\cdot$mol$^{-1}$]")
		# axes[1].set_ylabel(r"Vacuum leg MBAR error [kcal$\cdot$mol$^{-1}$]")
		# axes[1].set(adjustable='box-forced', aspect='equal')
		# plt.tight_layout()

		# # set the plot title and save:
		# if mbar_type == "full":
		# 	title = "Full MBAR\nn="+str(len(result))
		# if mbar_type == "subsampling":
		# 	title = "Subsampled MBAR\nn="+str(len(result))
		# plt.annotate(title, xy=(-1.7,1), annotation_clip=False, size="large")
		# plt.savefig(mbar_type+"mbar_analysis.png", dpi=300)
		# plt.show()

def snipped_traj_scatterplot():
	# process data for snipped vs full trajectory scatterplot:

	traj_types = [
				"full",
				"snipped"
				]
	legs = [
			"free", 
			"vac"
			]


	snipped_df_free = pd.DataFrame()
	snipped_df_vac = pd.DataFrame()

	for traj_type in traj_types:

		est_errors = []
		for leg in legs:
			result_lines = []

			mbar_paths = glob.glob(traj_type+"/"+leg+"/*")
			# read through the MBAR output files:
			for path in mbar_paths:
				f = open(path, "r")
				for line in f:
					# read the line after the #MBAR keyword for the energy prediction: 
					if line.startswith("#MBAR"):

						name = path.split("/")[2].replace("_vacuum","").replace("_free", "")
						result_lines.append([name, next(f)])

			for line in result_lines:
				# clean and make a list of the errors:
				name = line[0]
				result = line[1].split(", ")[1].split("  ")[0].replace(" \n", "")
				est_errors.append([name, result, leg])

		# construct seperate dataframes:
		df = pd.DataFrame(est_errors, columns=["pert", traj_type+"_error", "leg"])
		df = df.set_index("pert")
		
		df = df.astype({traj_type+"_error" : float})
		df = df.loc[df[traj_type+"_error"] < 5]

		df_free = df.loc[df["leg"] == "free"]
		df_vac = df.loc[df["leg"] == "vac"]

		snipped_df_free = pd.concat([snipped_df_free, df_free], axis=1).dropna()
		snipped_df_vac = pd.concat([snipped_df_vac, df_vac], axis=1).dropna()

	# initialise double-framed plot:
	f, axes = plt.subplots(1,2, sharey=True)

	sns.scatterplot(
					snipped_df_free["full_error"], 
					snipped_df_free["snipped_error"],
					ax=axes[0]
					)
	sns.scatterplot(
					snipped_df_vac["full_error"], 
					snipped_df_vac["snipped_error"],
					ax=axes[1]
					)

	axes[0].set_title("Solvated\nMBAR error [kcal$\cdot$mol$^{-1}$]")
	axes[1].set_title("Vacuum\nMBAR error [kcal$\cdot$mol$^{-1}$]")

	for ax in axes:
		ax.set_xlabel("Full trajectory (1 ns)")
		ax.set_ylabel("First 10% of trajectory")
		ax.set_xlim(0, 1)
		ax.set_ylim(0, 1)
		ax.set(adjustable='box-forced', aspect='equal')

	plt.show()
	plt.savefig("snipped_vs_full_traj_MBAR_errors.png", dpi=300)

full_vs_subsampled_mbar()
#snipped_traj_scatterplot()