#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dualpts2hs-hf20140503
#$ -V
#$ -m ae
#$ -t 1-5

################################################################################
# generate NIR and SWIR HS projection images from spectral point cloud. 
DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
)

NIRHSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
)

SWIRHSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${NIRHSPRJFILES[$SGE_TASK_ID-1]} -p 4 --pixelfunc "mean" -M --pulseno=8 --intensity=4 -H 1.5 --maxzen=117
python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${SWIRHSPRJFILES[$SGE_TASK_ID-1]} -p 5 --pixelfunc "mean" -M --pulseno=8 --intensity=4 -H 1.5 --maxzen=117

################################################################################
# generate color-composite HS projection image files.
CCFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_cc_hsproj.py"

python $PYCMD -n ${NIRHSPRJFILES[$SGE_TASK_ID-1]} -s ${SWIRHSPRJFILES[$SGE_TASK_ID-1]} -c ${CCFILES[$SGE_TASK_ID-1]} --nb 1 --sb 1 --nm 2 --sm 2
