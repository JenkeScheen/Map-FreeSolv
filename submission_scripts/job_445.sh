#!/bin/bash
cd ../
#SBATCH --job-name=FreeSolv
#SBATCH -o serial_output/183340~183751.out
#SBATCH -e serial_output/183340~183751.err
#SBATCH -p serial
#SBATCH -n 4
#SBATCH -N 1
#SBATCH --time 48:00:00

/home/jscheen/biosimspace.app/bin/python3.7 solvate_matrix_bin_BSS.py -start 183340 -end 183751