#!/bin/bash
cd ../
#SBATCH --job-name=FreeSolv
#SBATCH -o serial_output/10300~10711.out
#SBATCH -e serial_output/10300~10711.err
#SBATCH -p serial
#SBATCH -n 4
#SBATCH -N 1
#SBATCH --time 48:00:00

/home/jscheen/biosimspace.app/bin/python3.7 solvate_matrix_bin_BSS.py -start 10300 -end 10711