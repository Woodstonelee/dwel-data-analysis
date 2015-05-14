#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dual-ptcl-class-hf20140421
#$ -V
#$ -m ae
#$ -t 1-5

DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
)

INDEX=( \
"NDI" \
"NDI" \
"NDI" \
"NDI" \
"NDI" \
)

NDITHRESH=( \
0.024 \
0.063 \
0.055 \
0.055 \
0.076 \
)

# start Zhan Li's python environment
module load anaconda
source activate zhanli_py27

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_points_classifier_index.py"

python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v -t ${NDITHRESH[$SGE_TASK_ID-1]}
