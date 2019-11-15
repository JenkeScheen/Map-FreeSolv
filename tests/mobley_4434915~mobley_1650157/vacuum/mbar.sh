#!/bin/bash
#SBATCH --job-name=MBAR
#SBATCH -o analyse-free-nrg-%A.%a.out
#SBATCH -p gpu
#SBATCH -n 1
#SBATCH --time 00:10:00

srun /export/users/common/BioSimSpace/sire.app/bin/analyse_freenrg mbar -i lambda_*/simfile.dat --temperature 300.0 --percent 95 --overlap > freenrg-MBAR.dat

sleep 60

#bzip2 lambda_*/*
