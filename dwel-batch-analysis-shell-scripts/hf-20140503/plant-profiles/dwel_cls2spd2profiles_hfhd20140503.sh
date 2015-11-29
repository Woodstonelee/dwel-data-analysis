#!/bin/bash
#$ -V
#$ -l mem_total=8
#$ -l h_rt=24:00:00
#$ -pe omp 4
#$ -m ae
#$ -N dwel-cls2spd2profiles-hfhd20140503
#$ -t 1-5

################################################################################
# convert classified point cloud in ascii to spd files
INFILENAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
)

INSHEIGHTS=( \
1.37 1.33 1.24 1.42 1.21 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"

python $PYCMD -i ${INFILENAMES[$SGE_TASK_ID-1]} --agh ${INSHEIGHTS[$SGE_TASK_ID-1]} --inres 0.115 --nrow 1022 --ncol 3142

################################################################################
# calculate pgap and plant profiles from spd files

OUTNAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_c_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_e_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_n_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_s_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_w_dual" \
)

MINZEN=10.0 # degree
MAXZEN=35.0 # degree
MAXHEIGHT=30.0 # meter
LEAFIALIM="0.9 0.99"
WOODIALIM="0.9 0.99"

PAI=1.11

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"

BASENAME=${INFILENAMES[$SGE_TASK_ID-1]}

NIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_nir.spd"
SWIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_swir.spd"

OUTPREFIX=${OUTNAMES[$SGE_TASK_ID-1]}

# python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --plot --savetemp

python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --plot --savetemp --pai $PAI
