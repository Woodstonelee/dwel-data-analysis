#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2hs-hf20140421
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
)

NDITHRESH=( \
0.024 \
0.063 \
0.055 \
0.055 \
0.076 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}".txt"
OUTFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_hsp2.img"

python $PYCMD -i $INFILENAME -o $OUTFILENAME -p 16 --pixelfunc "mode" -C -M --pulseno=6 --intensity=4 -H 1.5 --maxzen=117