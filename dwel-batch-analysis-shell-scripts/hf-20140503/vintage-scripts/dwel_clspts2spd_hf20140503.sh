#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2spd-hf20140503
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
)

NDITHRESH=( \
0.250 \
0.400 \
0.200 \
0.350 \
0.200 \
)

INSHEIGHTS=( \
1.37 1.33 1.24 1.42 1.21 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}".txt"

python $PYCMD -i $INFILENAME --agh ${INSHEIGHTS[$SGE_TASK_ID-1]} --inres 0.115 --nrow 1022 --ncol 3142