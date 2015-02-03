#!/bin/bash

python get_plant_profiles.py -d '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2' -z 'midzeniths.txt' -H 'heights.txt' -g 'pgapz_total_nir.txt' -f 'profile_total_nir.txt'

python get_plant_profiles.py -d '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2' -z 'midzeniths.txt' -H 'heights.txt' -g 'pgapz_leaf_nir.txt' -f 'profile_leaf_nir.txt'

python get_plant_profiles.py -d '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2' -z 'midzeniths.txt' -H 'heights.txt' -g 'pgapz_branch_nir.txt' -f 'profile_branch_nir.txt'

python get_plant_profiles.py -d '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2' -z 'midzeniths.txt' -H 'heights.txt' -g 'pgapz_total_swir.txt' -f 'profile_total_swir.txt'

python get_plant_profiles.py -d '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2' -z 'midzeniths.txt' -H 'heights.txt' -g 'pgapz_leaf_swir.txt' -f 'profile_leaf_swir.txt'

python get_plant_profiles.py -d '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2' -z 'midzeniths.txt' -H 'heights.txt' -g 'pgapz_branch_swir.txt' -f 'profile_branch_swir.txt'