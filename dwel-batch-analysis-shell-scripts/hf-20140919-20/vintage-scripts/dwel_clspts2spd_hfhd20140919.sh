#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2spd-hfhd20140919
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt" \
)

NDITHRESH=( \
0.550 \
0.550 \
0.550 \
0.550 \
0.550 \
)

INSHEIGHTS=( \
1.30 1.40 1.10 1.12 1.36 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}".txt"

python $PYCMD -i $INFILENAME --agh ${INSHEIGHTS[$SGE_TASK_ID-1]} --inres 0.115 --nrow 1022 --ncol 3142