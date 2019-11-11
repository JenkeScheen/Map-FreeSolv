#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BioSimSpace as BSS
from BioSimSpace import _Exceptions

import glob
from tqdm import tqdm
import os
import pickle
import csv
import subprocess
from argparse import ArgumentParser
import time

## TODO
## figure out a way to brute-force ring-breaking



def read_pairings_file(args):
	"""
	- Function that reads the pairings for all the perturbations possible in freesolv 
	  and slices them according to the provided args

	Args:
	
	- args: argparse values that instruct which slice of all pairings to take.

	Returns:

	- a nested list of the sliced suggested pairings
	"""
	fully_connected_ntwk = []
	with open("./output/ligands_parameterised/mapping_reference.csv", "r") as file:
		reader = csv.reader(file)
		for row in reader:
			fully_connected_ntwk.append(row)

	# now use the args to slice the required pairings, continue with those:
	start = int(args.start)
	end = int(args.end)
	fully_connected_ntwk = fully_connected_ntwk[start:end]

	return fully_connected_ntwk


def map_ligand_pairs(pair, verbose=False):
	"""
	- Function that takes a perturbation pair, reads in the molecules using BSS and creates
	  the mapping

	Args:
	
	- a list containing the names of the two molecules in the pair

	Returns:

	- the mol objects (BSS), the mapping (dict) and the pair name 
	"""

	path = "output/ligands_parameterised/"
	pair_name = pair[0]+"~"+pair[1]


	mol1 = BSS.IO.readMolecules([path+pair[0]+".rst7", path+pair[0]+".prm7"])[0]
	mol2 = BSS.IO.readMolecules([path+pair[1]+".rst7", path+pair[1]+".prm7"])[0]

	mapping = BSS.Align.matchAtoms(mol1, mol2)


	if verbose == True:
		# print out mapping info per match:
		print(pair[0], "<--~", pair[2])
		for idx0, idx1 in mapping.items():
			print(pair[1].getAtoms()[idx0], "<--~", pair[3].getAtoms()[idx1])
		print("################################################################")



	# write out these mappings:
	with open("./output/ligand_mappings/mappings.p", "ab") as handle:
		pickle.dump([pair,mapping], handle)

	return mol1, mol2, mapping, pair_name



def align_molecules(mol1, mol2, mapping, pair_name, method="flexible"):
	"""
	- Function that aligns the two molecules of the pair spatially

	Args:
	
	- mol1, mol2: BSS molecule objects
	- mapping: dict containing the BSS-generated mapping between atoms of the molecules
	- pair_name: a string of the names of both molecules connected with a tilde

	Returns:

	- aligned: a list of the two molecules that are now aligned (mol1 is aligned to mol2)
	"""

	# determine which alignment method to use:

	if method == "rmsd":
		def align_match(mol1, mol2, mapping):
			# use the RMSD scoring function to align the first molecule of the pair to the second,
			# while using the predefined mapping:
			mol1_aligned = BSS.Align.rmsdAlign(mol1, mol2, mapping)

			# return the aligned molecules:
			return [mol1_aligned, mol2]

	elif method == "flexible":
		def align_match(mol1, mol2, mapping):

			# use fkcombu to align the first molecule of the pair to the second,
			# while using the predefined mapping:
			mol1_aligned = BSS.Align.flexAlign(mol1, mol2, mapping, fkcombu_exe="/home/jscheen/fkcombu")

			# return the aligned molecules:
			return [mol1_aligned, mol2]
	else:
		raise NameError("Alignment method not recognised, use \"rmsd\" or \"flexible\".") 
	
	# use the alignment function to align each pair:
	try:
		aligned = align_match(mol1, mol2, mapping)

	# if fkcombu fails, revert back to rmsd:
	except _Exceptions.AlignmentError:

		aligned = [BSS.Align.rmsdAlign(mol1, mol2, mapping), mol2]

	# now write the aligned pairs with their mappings to files:
	path = "./output/ligand_pairs_aligned/"+pair_name+"/"
	mol1_name = pair_name.split("~")[0]
	mol2_name = pair_name.split("~")[1]

	if not os.path.exists(path):
		os.makedirs(path)

	BSS.IO.saveMolecules(path+"tar_"+mol1_name, aligned[0], "PRM7")
	BSS.IO.saveMolecules(path+"tar_"+mol1_name, aligned[0], "RST7")
	BSS.IO.saveMolecules(path+"ref_"+mol2_name, aligned[1], "PRM7")
	BSS.IO.saveMolecules(path+"ref_"+mol2_name, aligned[1], "RST7")

	with open(path+"mapping.p", 'wb') as handle:
		pickle.dump(mapping, handle)

	return aligned


def merge_pairs(aligned_mols, mapping, pair_name, verbose=False):
	"""
	- Function that merges two aligned molecules

	Args:
	
	- aligned_mols: list containing the two aligned BSS molecule objects
	- mapping: dict containing the BSS-generated mapping between atoms of the molecules
	- pair_name: a string of the names of both molecules connected with a tilde

	Returns:

	- a BSS merged molecules object
	"""	

	mol1 = aligned_mols[0]
	mol2 = aligned_mols[1]
	mol1_name = pair_name.split("~")[0]
	mol2_name = pair_name.split("~")[1]


	# map the ligand pairs:
	try:
		merged = BSS.Align.merge(mol1, mol2, mapping,
							allow_ring_breaking=True,
							allow_ring_size_change=True
							)
		
		# write the merged pair to a file:
		path = "output/merged_ligand_pairs/merged/"+pair_name+"/"
		if not os.path.exists(path):
			os.makedirs(path)
	
		BSS.IO.saveMolecules(path+"/lambda0.prm7", merged._toRegularMolecule(), "PRM7")
		BSS.IO.saveMolecules(path+"/lambda0.rst7", merged._toRegularMolecule(), "RST7")

		BSS.IO.saveMolecules(path+"/lambda1.prm7", merged._toRegularMolecule(is_lambda1=True), "PRM7")
		BSS.IO.saveMolecules(path+"/lambda1.rst7", merged._toRegularMolecule(is_lambda1=True), "RST7")


		if verbose == True:
			print("Merged", mol1_name, "-->", mol2_name)


	# merging can fail for multiple reasons, see docs:
	except _Exceptions.IncompatibleError:


		# write the failed pair to a file:
		directory = "output/merged_ligand_pairs/failed_to_merge/"+mol1_name+"~"+mol2_name
		if not os.path.exists(directory):
			os.makedirs(directory)
		BSS.IO.saveMolecules(directory+"/lambda0.pdb", mol1, fileformat="MOL2")
		BSS.IO.saveMolecules(directory+"/lambda1.pdb", mol2, fileformat="MOL2")

		if verbose == True:
			print("Merging failed for", mol1_name, "-->", mol2_name)
		return
	return merged

def solvate_merged_pairs(merged, pair_name):
	"""
	- Function that solvates two merged molecules in a 3nm box.

	Args:
	
	- merged: a BSS object containing merged molecules
	- pair_name: a string of the names of both molecules connected with a tilde

	Returns:

	- a BSS solvated merged molecules object
	"""
	mol1_name = pair_name.split("~")[0]
	mol2_name = pair_name.split("~")[1]

	solvated = BSS.Solvent.tip3p(molecule=merged, box=3*[3*BSS.Units.Length.nanometer])
	
	return solvated


def setup_freenrg_protocol(solvated, pair_name):
	"""
	- Function that sets up a SOMD free energy calculation folder hierarchy;
	  the folders are written to FE_scratch and then archived into FE/.

	Args:
	
	- solvated: a BSS object containing a solvated merged molecular object
	- pair_name: a string of the names of both molecules connected with a tilde

	Returns:

	- None
	"""


	protocol = BSS.Protocol.FreeEnergy()

	freenrg_somd = BSS.FreeEnergy.Solvation(
									solvated, 
									protocol, 
									engine="SOMD", 
									work_dir="FE_scratch/"+pair_name
									)
	archive_command = "tar -zcf FE/"+pair_name+".tar.gz FE_scratch/"+pair_name
	clean_scratch_command = "rm -r FE_scratch/"+pair_name
	subprocess.call(archive_command, shell=True)
	subprocess.call(clean_scratch_command, shell=True)


def main():
	# process commandline input that indicates which chunk of the perturbations to process:
	parser = ArgumentParser()
	parser.add_argument(
        "-start",
        help="Index startpoint to run this solvation script on.",
        metavar='INT',
        default='True',
        required='True'
    )
	parser.add_argument(
        "-end",
        help="Index endpoint to run this solvation script on.",
        metavar='INT',
        default='True',
        required='True'
    )

	args = parser.parse_args()
	# read in the correct combination of pairings using the caught args:
	fully_connected_ntwk = read_pairings_file(args)

	for pair in fully_connected_ntwk:
		start = time.time()

		mol1, mol2, mapping, pair_name = map_ligand_pairs(pair)
		aligned_mols = align_molecules(mol1, mol2, mapping, pair_name)
		merged = merge_pairs(aligned_mols, mapping, pair_name, verbose=False)

		# merging can fail for multiple reasons, see docs. For successful merges:
		if merged is not None:
			print("Solvating", pair_name)
			solvated = solvate_merged_pairs(merged, pair_name)
			print("Setting up SOMD..")
			setup_freenrg_protocol(solvated, pair_name)
		end = time.time()
		print("Took "+str(round(end-start))+" seconds.")


if __name__ == "__main__":
	main()
