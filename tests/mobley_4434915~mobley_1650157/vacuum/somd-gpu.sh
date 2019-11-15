#!/bin/bash
#SBATCH --job-name=FREESOLV
#SBATCH -o somd-array-gpu-%A.%a.out
#SBATCH -p gpu
#SBATCH -n 1
#SBATCH --gres=gpu:1
#SBATCH --time 24:00:00
#SBATCH --array=0-10

module load cuda/9.2
module load BSS/dev

echo "CUDA DEVICES:" $CUDA_VISIBLE_DEVICES

lamvals=( 0.0000 0.1000 0.2000 0.3000 0.4000 0.5000 0.6000 0.7000 0.8000 0.9000 1.0000 )
lam=${lamvals[SLURM_ARRAY_TASK_ID]}

sleep 5

echo "lambda is: " $lam

#mkdir lambda-$lam
cd lambda_$lam

export OPENMM_PLUGIN_DIR=/export/users/common/BioSimSpace/sire.app/lib/plugins/

srun /export/users/common/BioSimSpace/sire.app/bin/somd-freenrg -C ./somd.cfg -c ./somd.rst7 -t ./somd.prm7 -m ./somd.pert -l $lam -p CUDA
cd ..

wait

if [ "$SLURM_ARRAY_TASK_ID" -eq "10" ]
then
    sleep 600
    sbatch ./mbar.sh
fi
