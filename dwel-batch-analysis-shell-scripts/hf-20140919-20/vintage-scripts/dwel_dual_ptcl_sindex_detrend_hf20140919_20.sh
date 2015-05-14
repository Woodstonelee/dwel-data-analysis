#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-dt-ndi-hf20140919-20
#$ -V
#$ -m ae
#$ -t 1-10

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
)

DTPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414_detrend.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414_detrend.txt" \
)

PARFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/ndi_summary_hfhd20140919.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/ndi_summary_hfhd20140919.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/ndi_summary_hfhd20140919.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/ndi_summary_hfhd20140919.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/ndi_summary_hfhd20140919.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/ndi_summary_hfhm20140920.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/ndi_summary_hfhm20140920.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/ndi_summary_hfhm20140920.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/ndi_summary_hfhm20140920.txt_pwreg1st_range_vs_ndi.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/ndi_summary_hfhm20140920.txt_pwreg1st_range_vs_ndi.txt" \
)

# PARFILES=( \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# "/usr3/graduate/zhanli86/Programs/misc/dwel-calibration/nsf-dwel-cal-201410/cal-nsf-20140812-outputs-v20150202/cal_dwel_gm_20140812_pwreg1st_range_vs_ndi.txt" \
# )

# start Zhan Li's python environment
module load anaconda
source activate zhanli_py27

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_detrend_points_index.py"

python $PYCMD -i "${CLSPTSFILES[$SGE_TASK_ID-1]}" -p "${PARFILES[$SGE_TASK_ID-1]}" -o "${DTPTSFILES[$SGE_TASK_ID-1]}" -x 15 -r 7
