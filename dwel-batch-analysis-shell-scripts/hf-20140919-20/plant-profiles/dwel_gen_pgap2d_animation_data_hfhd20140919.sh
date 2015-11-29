#!/bin/bash
#$ -q "geo*"
#$ -V
#$ -l mem_total=8
#$ -l h_rt=12:00:00
# #$ -pe omp 4
# #$ -m ae
#$ -N dwel-pgap2d-animation-data-hfhd20140919
#$ -e "/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-batch-analysis-shell-scripts/hf-20140919-20/plant-profiles/pgap2d-animation-data-dump"
#$ -o "/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-batch-analysis-shell-scripts/hf-20140919-20/plant-profiles/pgap2d-animation-data-dump"
#$ -t 1:50

INFILENAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
)

ANIMATIONDATAOUTDIR="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering-profiles/pgap-by-scaling/pgap2d-animation-data"

OUTNAMES=( \
"hfhd_20140919_c_dual" \
"hfhd_20140919_e_dual" \
"hfhd_20140919_n_dual" \
"hfhd_20140919_s_dual" \
"hfhd_20140919_w_dual" \
)

CLASSCODE="1 2"
USERACCURACY="0.733 0.756"
INSHEIGHTS=( \
1.30 1.40 1.10 1.12 1.36 \
)

MINZEN=10.0 # degree
MAXZEN=35.0 # degree
MAXHEIGHT=30.0 # meter
LEAFIALIM="0.9 0.99"
WOODIALIM="0.9 0.99"
PAI=3.42

FIDX=0

f=${INFILENAMES[$FIDX]}
# resample classification
BASENAME=$(basename "$f")
DIRNAME=$(dirname "$f")

# convert to spd files
PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"
# python $PYCMD -i $f --agh ${INSHEIGHTS[$i-1]} --inres 0.115 --nrow 1022 --ncol 3142

# calculate plant profiles, biggest time-consumer
PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"

NIRFILENAME=$DIRNAME"/"${BASENAME:0:${#BASENAME}-4}"_nir.spd"
SWIRFILENAME=$DIRNAME"/"${BASENAME:0:${#BASENAME}-4}"_swir.spd"

# create a folder for one range location if it does not exist
if [ ! -d "$ANIMATIONDATAOUTDIR/MAXRG-$SGE_TASK_ID" ]; then
    mkdir -p "$ANIMATIONDATAOUTDIR/MAXRG-$SGE_TASK_ID"
fi

OUTPREFIX="$ANIMATIONDATAOUTDIR/MAXRG-$SGE_TASK_ID/${OUTNAMES[$FIDX]}"
python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --pai $PAI --pgap2dmaxrg $SGE_TASK_ID --savetemp


# for i in `seq 1 ${#INFILENAMES[@]}`
# do
# done