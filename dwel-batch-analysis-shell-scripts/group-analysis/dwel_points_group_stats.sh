#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-pts-group-stats
#$ -V
#$ -m ae
#$ -t 1-6

LISTFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/spectralpcdfilelist_hfhd20140421.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/spectralpcdfilelist_hfhd20140503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/spectralpcdfilelist_hfhd20140608.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/spectralpcdfilelist_hfhd20140919.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/spectralpcdfilelist_hfhm20140609.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/spectralpcdfilelist_hfhm20140920.txt" \
)

OUTPREFIX=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/ndi_summary_hfhd20140421" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/ndi_summary_hfhd20140503" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/ndi_summary_hfhd20140608" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/ndi_summary_hfhd20140919" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/ndi_summary_hfhm20140609" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/ndi_summary_hfhm20140920" \
)

RMIN=( \
1.5 \
1.5 \
0.0 \
0.0 \
0.0 \
0.0 \
)

RMAX=( \
30.0 \
30.0 \
20.0 \
20.0 \
20.0 \
20.0 \
)

RBREAK=( \
"4 9 40" \
"4 9 40" \
"2 3 9 20" \
"2 3 9 20" \
"2 3 9 20" \
"2 3 9 20" \
)

# start Zhan Li's python environment
module load anaconda
source activate zhanli_py27

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_points_group_summary.py"

# python $PYCMD -l ${LISTFILES[$SGE_TASK_ID-1]} -o ${OUTPREFIX[$SGE_TASK_ID-1]} -x 15 -r 7 --rmin=${RMIN[$SGE_TASK_ID-1]} --rmax=${RMAX[$SGE_TASK_ID-1]} --rbreak="${RBREAK[$SGE_TASK_ID-1]}"
# python $PYCMD -l ${LISTFILES[$SGE_TASK_ID-1]} -o ${OUTPREFIX[$SGE_TASK_ID-1]} -x 15 -r 7 --rmin=${RMIN[$SGE_TASK_ID-1]} --rmax=${RMAX[$SGE_TASK_ID-1]}
python $PYCMD -l ${LISTFILES[$SGE_TASK_ID-1]} -o ${OUTPREFIX[$SGE_TASK_ID-1]} --rmin=0.0 --rbreak ${RBREAK[$SGE_TASK_ID-1]}
