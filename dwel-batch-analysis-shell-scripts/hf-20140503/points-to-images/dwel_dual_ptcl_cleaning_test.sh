#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dualpts-cleaning-test-hfhd20140503
#$ -V
#$ -m ae
#$ -t 1-13

INPTSFILE="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt"
OUTPREFIX="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/test-points-cleaning/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_signal_thresh_"

THRESH=(0.075  0.085  0.095  0.105  0.115  0.125  0.135  0.145  0.155  0.165  0.175  0.185  0.195)

OUTPTSFILE=$OUTPREFIX${THRESH[$SGE_TASK_ID-1]}".txt"
# clean the points
PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-spectral-points-generation/dwel_spectral_points_cleaning.py"
python $PYCMD -i $INPTSFILE -t ${THRESH[$SGE_TASK_ID-1]} -o $OUTPTSFILE

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

python $PYCMD -i $OUTPTSFILE -o ${OUTPTSFILE:0:${#OUTPTSFILE}-4}"_nhits_hsp2.img" -p 7 --pixelfunc "sum" -H 1.5 --maxzen=117

# PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_cc_hsproj.py"

# python $PYCMD -n ${NIRHSPRJFILES[$SGE_TASK_ID-1]} -s ${SWIRHSPRJFILES[$SGE_TASK_ID-1]} -c ${CCFILES[$SGE_TASK_ID-1]}
