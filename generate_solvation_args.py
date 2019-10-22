#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv
import os

###
### Short python script for generating submission scripts that run chunks of solvate_matrix_bin_BSS.py using
### arguments for start and endpoints.


with open("output/ligands_parameterised/mapping_reference.csv", "r") as file:
	reader = csv.reader(file)
	total_perturbations = sum(1 for row in reader)

# we want to have 1000 jobs:
n_jobs = 1000
perturbations_per_job = int(total_perturbations/ (n_jobs))

def generate_submission(start, end):
	submission = str(
				"#!/bin/bash\n"
				"cd ../\n"

				"#SBATCH --job-name=FreeSolv\n"
				"#SBATCH -o serial_output/"+str(start)+"~"+str(end)+".out\n"
				"#SBATCH -e serial_output/"+str(start)+"~"+str(end)+".err\n"
				"#SBATCH -p serial\n"
				"#SBATCH -n 4\n"
				"#SBATCH -N 1\n"
				"#SBATCH --time 48:00:00\n\n"

				
				"/home/jscheen/biosimspace.app/bin/python3.7 solvate_matrix_bin_BSS.py -start "+str(start)+" -end "+str(end)
				)
	return submission

path = "./submission_scripts/"
if not os.path.exists(path):
	os.makedirs(path)


counter = 0
for i in range(n_jobs):
	start = counter
	end = counter + perturbations_per_job
	if end < 411522:
		file_lines = generate_submission(start, end)
		counter += perturbations_per_job + 1
	# prevent overshoot:
	else:
		file_lines = generate_submission(start, 411522)
		break

	with open(path+"job_"+str(i)+".sh", "w") as file:
		file.write(file_lines)
		file.close()




