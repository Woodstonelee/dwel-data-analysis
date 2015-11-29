#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-pts-add-fake-class-hf20150919
#$ -V
#$ -m ae

PYCMD="/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-union/hfhd20150919-dual-points/dwel_points_add_fake_class.py"
python $PYCMD
