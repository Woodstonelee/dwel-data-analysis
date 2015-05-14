#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-dt-ndi-hf20140421
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
)

DTPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154_detrend.txt" \
)

PARFILE="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/ndi_summary_hfhd20140421.txt_pwreg1st_range_vs_ndi.txt"

# start Zhan Li's python environment
module load anaconda
source activate zhanli_py27

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_detrend_points_index.py"

python $PYCMD -i "${CLSPTSFILES[$SGE_TASK_ID-1]}" -p "$PARFILE" -o "${DTPTSFILES[$SGE_TASK_ID-1]}" -x 15 -r 7
