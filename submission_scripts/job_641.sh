#!/bin/bash
cd ../
#SBATCH --job-name=FreeSolv
#SBATCH -o serial_output/264092~264503.out
#SBATCH -e serial_output/264092~264503.err
#SBATCH -p serial
#SBATCH -n 4
#SBATCH -N 1
#SBATCH --time 48:00:00

/home/jscheen/biosimspace.app/bin/python3.7 solvate_matrix_bin_BSS.py -start 264092 -end 264503