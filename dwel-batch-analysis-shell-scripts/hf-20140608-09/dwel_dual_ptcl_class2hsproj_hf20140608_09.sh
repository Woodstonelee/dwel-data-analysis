#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2hs-hf20140608-09
#$ -V
#$ -m ae
#$ -t 1-10

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
)

NDITHRESH=( \
0.400 \
0.426 \
0.376 \
0.383 \
0.456 \
0.400 \
0.400 \
0.447 \
0.400 \
0.400 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}".txt"
OUTFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_hsp2.img"

python $PYCMD -i $INFILENAME -o $OUTFILENAME -p 16 --pixelfunc "mode" -C -M --pulseno=6 --intensity=4 -H 1.5 --maxzen=117