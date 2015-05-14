#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-spd2profiles-hf20140919
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

OUTNAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140919_C_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140919_E_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140919_N_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140919_S_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140919_W_dual" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/dwel_pgap_foliage_profile.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

NIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_nir.spd"
SWIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_swir.spd"

OUTPREFIX=${OUTNAMES[$SGE_TASK_ID-1]}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}

if [ $SGE_TASK_ID -eq 1 ]
then
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.547, 0.547 --plot --savetemp -g
else
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.547, 0.547 --plot --savetemp
fi