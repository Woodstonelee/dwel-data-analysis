#!/bin/bash
#$ -V
#$ -l mem_total=8
#$ -l h_rt=24:00:00
#$ -pe omp 4
#$ -m ae
#$ -N dwel-pts2spd2profiles-hfhd20140919
#$ -t 1-5

################################################################################
# convert classified point cloud in ascii to spd files
INFILENAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_fake_leaf_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_fake_leaf_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_fake_leaf_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_fake_leaf_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_fake_leaf_class.txt" \
)

INSHEIGHTS=( \
1.30 1.40 1.10 1.12 1.36 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"

python $PYCMD -i ${INFILENAMES[$SGE_TASK_ID-1]} --agh ${INSHEIGHTS[$SGE_TASK_ID-1]} --inres 0.115 --nrow 1022 --ncol 3142

################################################################################
# calculate pgap and plant profiles from spd files

OUTNAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/zen-5-65/hfhd_20140919_c_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/zen-5-65/hfhd_20140919_e_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/zen-5-65/hfhd_20140919_n_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/zen-5-65/hfhd_20140919_s_dual" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/zen-5-65/hfhd_20140919_w_dual" \
)

MINZEN=5.0 # degree
MAXZEN=65.0 # degree
MAXHEIGHT=40.0 # meter
LEAFIALIM="0.9 0.99"
WOODIALIM="0.9 0.99"
PAI=1.0

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"

BASENAME=${INFILENAMES[$SGE_TASK_ID-1]}

NIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_nir.spd"
SWIRFILENAME=${BASENAME:0:${#BASENAME}-4}"_swir.spd"

OUTPREFIX=${OUTNAMES[$SGE_TASK_ID-1]}

python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --plot --savetemp --pai $PAI

# python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --plot --usetemp
