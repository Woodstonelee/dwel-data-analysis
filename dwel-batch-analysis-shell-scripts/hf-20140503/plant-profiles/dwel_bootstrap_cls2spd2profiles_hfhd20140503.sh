#!/bin/bash
#$ -q "geo*"
#$ -V
#$ -l mem_total=8
#$ -l h_rt=12:00:00
# #$ -pe omp 4
# #$ -m ae
#$ -N dwel-bootstrap-cls2spd2profiles-hfhd20140503
#$ -e "/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-batch-analysis-shell-scripts/hf-20140503/plant-profiles/bootstrapping-dump"
#$ -o "/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-batch-analysis-shell-scripts/hf-20140503/plant-profiles/bootstrapping-dump"
#$ -t 1:1000

INFILENAMES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
)

BOOTSTRAPOUTDIR="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/bootstrapping-classification"

CLASSCODE="1 2"
USERACCURACY="0.908 0.466"
INSHEIGHTS=( \
1.37 1.33 1.24 1.42 1.21 \
)

MINZEN=10.0 # degree
MAXZEN=35.0 # degree
MAXHEIGHT=30.0 # meter
LEAFIALIM="0.9 0.99"
WOODIALIM="0.9 0.99"
PAI=1.11

for i in `seq 1 ${#INFILENAMES[@]}`
do
    f=${INFILENAMES[$i-1]}
    # resample classification
    BASENAME=$(basename "$f")
    CLSFILE="$TMPDIR/${BASENAME%.*}.$JOB_ID.$SGE_TASK_ID.txt"
    PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_resample_classification.py"
    python $PYCMD -i $f -o $CLSFILE --classcode $CLASSCODE --useraccuracy $USERACCURACY

    # convert to spd files
    PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"
    python $PYCMD -i $CLSFILE --agh ${INSHEIGHTS[$i-1]} --inres 0.115 --nrow 1022 --ncol 3142

    # calculate plant profiles, biggest time-consumer
    PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-profile/one-band-a-time/dwel_pgap_foliage_profile.py"
    NIRFILENAME="$TMPDIR/${BASENAME%.*}.$JOB_ID.$SGE_TASK_ID""_nir.spd"
    SWIRFILENAME="$TMPDIR/${BASENAME%.*}.$JOB_ID.$SGE_TASK_ID""_swir.spd"
    OUTPREFIX="$BOOTSTRAPOUTDIR/${BASENAME%.*}_"$JOB_ID"_"$SGE_TASK_ID
    python $PYCMD -n $NIRFILENAME -s $SWIRFILENAME -o $OUTPREFIX --maxheight $MAXHEIGHT --minzenith $MINZEN --maxzenith $MAXZEN --fwhm 0.547 0.547 --leafIalim $LEAFIALIM --woodIalim $WOODIALIM --pai $PAI

done