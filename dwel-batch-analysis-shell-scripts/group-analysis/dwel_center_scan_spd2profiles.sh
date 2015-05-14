#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-center-scan-spd2profiles
#$ -V
#$ -m ae
#$ -t 1-4

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
)

# OUTNAMES=( \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering-profiles/pgap-by-scaling/maxzen-30/hfhd_20140421_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/maxzen-30/hfhd_20140503_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering-profiles/pgap-by-scaling/maxzen-30/hfhd_20140608_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/maxzen-30/hfhd_20140919_c_dual" \
# )

# OUTNAMES=( \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering-profiles/pgap-by-scaling/maxzen-70/hfhd_20140421_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/maxzen-70/hfhd_20140503_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering-profiles/pgap-by-scaling/maxzen-70/hfhd_20140608_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/maxzen-70/hfhd_20140919_c_dual" \
# )

OUTNAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140421_c_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_c_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering-profiles/pgap-by-scaling/hfhd_20140608_c_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/hfhd_20140919_c_dual" \
)

# OUTNAMES=( \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering-profiles/pgap-by-normalization/maxzen-30/hfhd_20140421_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-normalization/maxzen-30/hfhd_20140503_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering-profiles/pgap-by-normalization/maxzen-30/hfhd_20140608_c_dual" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-normalization/maxzen-30/hfhd_20140919_c_dual" \
# )

MINZEN=10.0 # degree
MAXZEN=35.0 # degree
MAXHEIGHT=30.0 # meter
LEAFIALIM="0.9 0.99"
WOODIALIM="0.9 0.99"

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

NIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_nir.spd"
SWIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_swir.spd"

OUTPREFIX=${OUTNAMES[$SGE_TASK_ID-1]}

# python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --plot --savetemp

python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --plot --usetemp