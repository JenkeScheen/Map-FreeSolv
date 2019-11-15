#!/bin/bash


lamvals=( 0.0000 0.1000 0.2000 0.3000 0.4000 0.5000 0.6000 0.7000 0.8000 0.9000 1.0000 )


echo "lambda is: " $lam

mkdir lambda_$lam
cd lambda_$lam

export OPENMM_PLUGIN_DIR=/home/jscheen/sire.app/lib/plugins/

/home/jscheen/sire.app/bin/somd-freenrg -C ../somd.cfg -c ../somd.rst7 -t ../somd.prm7 -m ../somd.pert -l $lam -p OpenCL -d 1
