#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-spd2profiles-hf20140421
#$ -V
#$ -m ae
#$ -t 1-5

# SGE_TASK_ID=1

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

OUTNAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140421_C_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140421_E_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140421_N_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140421_S_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/cal-simul-appndi-visual-thresh/plant-profiles/HFHD_20140421_W_dual" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

NIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_nir.spd"
SWIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}"_swir.spd"

OUTPREFIX=${OUTNAMES[$SGE_TASK_ID-1]}"_NDI_thresh_"${NDITHRESH[$SGE_TASK_ID-1]}

echo $NIRFILENAME
echo $SWIRFILENAME
echo $OUTPREFIX

if [ $SGE_TASK_ID -eq 1 ]
then
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.651 0.651 --plot --savetemp -g --leafIalim 0.50 0.99 --woodIalim 0.50 0.99 --plantIalim 0.50 0.99
#    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.651 0.651 --plot --usetemp -g
else
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.651 0.651 --plot --savetemp --leafIalim 0.50 0.99 --woodIalim 0.50 0.99 --plantIalim 0.50 0.99
#    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight 30.0 --fwhm 0.651 0.651 --plot --usetemp
fi