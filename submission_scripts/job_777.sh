#!/bin/bash
cd ../
#SBATCH --job-name=FreeSolv
#SBATCH -o serial_output/320124~320535.out
#SBATCH -e serial_output/320124~320535.err
#SBATCH -p serial
#SBATCH -n 4
#SBATCH -N 1
#SBATCH --time 48:00:00

/home/jscheen/biosimspace.app/bin/python3.7 solvate_matrix_bin_BSS.py -start 320124 -end 320535