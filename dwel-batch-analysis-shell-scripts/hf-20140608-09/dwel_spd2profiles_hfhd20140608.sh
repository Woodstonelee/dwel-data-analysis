#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-spd2profiles-hf20140608
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

OUTNAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140608_C_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140608_E_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140608_N_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140608_S_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140608_W_dual" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

NIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_nir.spd"
SWIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_swir.spd"

OUTPREFIX=${OUTNAMES[$SGE_TASK_ID-1]}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}

if [ $SGE_TASK_ID -eq 1 ]
then
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.547 0.547 --plot --savetemp -g --leafIalim 0.85 0.99 --woodIalim 0.85 0.99 --plantIalim 0.85 0.99
#    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.547 0.547 --plot --usetemp -g
else
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.547 0.547 --plot --savetemp --leafIalim 0.85 0.99 --woodIalim 0.85 0.99 --plantIalim 0.85 0.99
#    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.547 0.547 --plot --usetemp 
fi