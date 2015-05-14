#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2spd-hfhd20140608
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
)

NDITHRESH=( \
0.400 \
0.426 \
0.376 \
0.383 \
0.456 \
)

INSHEIGHTS=( \
1.33 1.42 1.37 1.37 1.30 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}".txt"

python $PYCMD -i $INFILENAME --agh ${INSHEIGHTS[$SGE_TASK_ID-1]} --inres 0.115 --nrow 1022 --ncol 3142