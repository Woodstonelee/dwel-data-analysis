#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dualpts2at-hf20140919_20
#$ -V
#$ -m ae
#$ -t 1-5

################################################################################
# generate NIR and SWIR HS projection images from spectral point cloud. 
DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

NIRHSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_atp2.img" \
)

SWIRHSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_atp2.img" \
)

CAMHEIGHTS=( \
  1.30 1.40 1.10 1.12 1.36 \
  1.26 1.21 1.17 1.12 1.12 1.21 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2atproj.py"

OUTRES=2.5
python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${NIRHSPRJFILES[$SGE_TASK_ID-1]} -p 4 --pixelfunc "mean" --pulseno=8 --intensity=4 -H 1.5 --maxzen=117 -r $OUTRES -H ${CAMHEIGHTS[$SGE_TASK_ID-1]}
python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${SWIRHSPRJFILES[$SGE_TASK_ID-1]} -p 5 --pixelfunc "mean" --pulseno=8 --intensity=4 -H 1.5 --maxzen=117 -r $OUTRES -H ${CAMHEIGHTS[$SGE_TASK_ID-1]}

################################################################################
# generate color-composite HS projection image files.
CCFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_atp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_cc_hsproj.py"

python $PYCMD -n ${NIRHSPRJFILES[$SGE_TASK_ID-1]} -s ${SWIRHSPRJFILES[$SGE_TASK_ID-1]} -c ${CCFILES[$SGE_TASK_ID-1]} --nb 1 --sb 1 --nm 2 --sm 2
