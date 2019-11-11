#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BioSimSpace as BSS
from BioSimSpace import _Exceptions

import glob
from tqdm import tqdm
import os
import pickle
import csv
import time

###TODO
# use mol2 input instead of pdb


def make_IO_env():
	"""
	- Function that creates the I/O environment for the program

	Args:
	
	- None

	Returns:

	- None
	"""
	# make a directory to store ligand mappings in:
	directory = "./output/ligand_mappings/"
	if not os.path.exists(directory):
	    os.makedirs(directory)

	# make a directory to store parameterised ligands in:
	directory = "./output/ligands_parameterised/"
	if not os.path.exists(directory):
	    os.makedirs(directory)

	# make a directory to store aligned ligand pairs in:
	directory = "./output/ligand_pairs_aligned/"
	if not os.path.exists(directory):
	    os.makedirs(directory)

	# make directories to store merged molecules in:
	directories = [
					"./output/merged_ligand_pairs/",
					"./output/merged_ligand_pairs/merged/",
					"./output/merged_ligand_pairs/failed_to_merge/"
					]
	for directory in directories:
		if not os.path.exists(directory):
			os.makedirs(directory)

	# make a directory to store free energy protocol folder hierarchies in:
	directory = "./FE_scratch/"
	if not os.path.exists(directory):
	    os.makedirs(directory)

	directory = "./FE/"
	if not os.path.exists(directory):
	    os.makedirs(directory)

def read_ligand_dir(n_restriction = None):
	"""
	- Function that reads directory filled with ligands

	Args:
	
	- n_restriction - user-set parameter that dictates how many molecules to read in (for e.g. script testing)

	Returns:

	- List of file paths
	"""
	ligands_pdb = glob.glob("./ligands/*.pdb")

	if n_restriction is None:
		return ligands_pdb
	else:
		return ligands_pdb[:n_restriction]



def BSS_read_files(ligand_paths):
	"""
	- Loads ligand files into BSS and creates mappings between all of them

	Args:
	
	- ligand_paths - list containing file paths to the ligands

	Returns:

	- Dictionary with ligand names and BSS molecule objects	
	"""
	# print some info:
	total_number_of_ligands = len(ligand_paths)
	print("\nTotal number of ligands is", total_number_of_ligands)
	print("Theoretically possible mappings is", total_number_of_ligands*total_number_of_ligands-total_number_of_ligands, "\n")

	# loop over ligand_paths, load them as BSS molecule objects and compile:
	BSS_mol_bucket = {}
	print("Parameterising ligands..")
	for lig in ligand_paths:

		# derive name from filename:
		lig_name = lig.split("/")[2].split(".")[0]
		print("Working on "+lig_name)
		if lig_name == None:
			raise NameError("Failed to extract ligand name from", lig)

		# load BSS mol object, parametrise, add entry to dict:
		mol = BSS.IO.readMolecules(BSS.IO.glob(lig))[0]

		# Here parameterise the ligand:
		try:
			process = BSS.Parameters.gaff2(mol, net_charge=BSS.Parameters.formalCharge(mol))
			mol = process.getMolecule()

			# write the parameterised molecules to files:
			path = "./output/ligands_parameterised/"+lig_name
			BSS.IO.saveMolecules(path, mol, "PRM7")
			BSS.IO.saveMolecules(path, mol, "RST7")

			BSS_mol_bucket[lig_name] = mol

		except _Exceptions.ParameterisationError:
			print(lig_name+" failed!")
			pass

	return BSS_mol_bucket

def generate_fully_connected_ntwk(BSS_mol_dict):
	"""
	- Takes dictionary of BSS molecule objects and creates all possible combinations

	Args:
	
	- BSS_mol_dict - dictionary containing the BSS mol objects per ligand name

	Returns:

	- nested list with all ligand combinations and their names
	"""
	fully_connected_ntwk = []

	for lig_name, lig_object in BSS_mol_dict.items():
		for query_name, query_object in BSS_mol_dict.items():
			if lig_name != query_name:
				fully_connected_ntwk.append([lig_name, query_name])

	with open("./output/ligands_parameterised/mapping_reference.csv", "w") as file:
		writer = csv.writer(file)
		for row in fully_connected_ntwk:
			writer.writerow(row)


	return fully_connected_ntwk


def main():
	start = time.time()
	make_IO_env()
	ligand_paths = read_ligand_dir()
	BSS_mol_dict = BSS_read_files(ligand_paths)
	generate_fully_connected_ntwk(BSS_mol_dict)
	end = time.time()
	print("It took "+str(round(end-start))+" seconds to parameterise "+str(len(ligand_paths))+" ligands.")

if __name__ == "__main__":
	main()
