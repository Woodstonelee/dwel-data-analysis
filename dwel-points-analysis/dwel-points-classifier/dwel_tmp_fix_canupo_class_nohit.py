#!/usr/bin/env python
"""
Temporarily fix no-hit points in the canupo class point cloud. In the old
dwel_merge_points_cluster.py, some (could be a lot) no-hit points are lost if
the merge uses a threshold to further remove some low reflectance points and all
points from a pulse are removed with such a threshold.

Now this routine is to temporarily add those missing no-hit points back to
classification point cloud by comparing it with the original dual-wavelength
point cloud before classification. In this way, we avoid redoing all the
classification procedures again!

Zhan Li, zhanli86@bu.edu
Created: Tue Jun 16 14:37:58 EDT 2015
"""

import sys
import argparse

import numpy as np

def getCmdArgs():
    p = argparse.ArgumentParser(description="A temporary fix of missing no-hit points in the point cloud of CANUPO class")

    p.add_argument('--classpts', dest='classpts', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt', help='ASCII point cloud file of classification')
    p.add_argument('--dualpts', dest='dualpts', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt', help='ASCII dual-wavelength point cloud file used for classification')
    p.add_argument('--fixed', dest='fixed', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt', help='Fixed ASCII point cloud file of classification')

    p.add_argument("-c", "--cols", dest="ncols", type=int, default=1022, help="Number of columns (samples) in the AT projection where points are generated. [default: 1022]")
    p.add_argument("-r", "--rows", dest="nrows", type=int, default=3142, help="Number of rows (lines) in the AT projection where points are generated. [default: 3142]")

    cmdargs = p.parse_args()

    if (cmdargs.classpts is None) or (cmdargs.dualpts is None) or (cmdargs.fixed is None):
        p.print_help()
        print "Classified point cloud, original dual-wavelength point cloud and output fixed file name are required!"
        sys.exit()

    return cmdargs

def main(cmdargs):
    # zero-based index
    cind = {'sample':11, 'line':12, 'shot_number':7, \
                'number_of_returns':6, 'theta':9, 'phi':10, \
                'ndi':19, 'clabel':20, 'cluster_class':21, 'class':23}

    dualpts_shotind = np.genfromtxt(cmdargs.dualpts, comments=None, delimiter=',', skip_header=3, usecols=(cind['shot_number']))
    classpts_shotind = np.genfromtxt(cmdargs.classpts, comments=None, delimiter=',', skip_header=3, usecols=(cind['shot_number']))

    missing_shot_lineind = np.where(np.in1d(dualpts_shotind, classpts_shotind, invert=True))[0]
    missing_shotind = dualpts_shotind[missing_shot_lineind]
    # get unique missing shot number
    missing_shotind, unique_ind = np.unique(missing_shotind, return_index=True)
    missing_shot_lineind = missing_shot_lineind[unique_ind]
    nmissing_shot = len(missing_shot_lineind)
    
    with open(cmdargs.dualpts, 'r') as dualfobj, \
            open(cmdargs.classpts, 'r') as classfobj, \
            open(cmdargs.fixed, 'w') as fixedfobj:
        # skip the first three lines
        for i in range(3):
            dualfobj.readline()
            fixedfobj.write(classfobj.readline())
        missing_pointer = 0
        for i, classline in enumerate(classfobj):
            linetokens = classline.rstrip('\r\n').split(',')
            tmp_shotind = int(linetokens[cind['shot_number']])
            while (missing_pointer<nmissing_shot) and (missing_shotind[missing_pointer] < tmp_shotind):
                # read the line of this missing shot from dual points
                if missing_pointer == 0:
                    target_dualline_ind = missing_shot_lineind[missing_pointer]
                else:
                    target_dualline_ind = missing_shot_lineind[missing_pointer] - missing_shot_lineind[missing_pointer-1] - 1
                for n, dualline in enumerate(dualfobj):
                    if n == target_dualline_ind:
                        missing_line = dualline
                        break
                missing_pointer += 1
                # double check the missing shot number
                missinglinetokens = missing_line.rstrip('\r\n').split(',')
                if missing_shotind[missing_pointer-1] != int(missinglinetokens[cind['shot_number']]):
                    raise RuntimeError('Read the wrong line of missing no-hit point from dual-wavelength point cloud')
                # insert this missing line to the output fixed file
                outlinetokens = ['0' for _ in range(len(linetokens))]
                outlinetokens[cind['shot_number']] = missinglinetokens[cind['shot_number']]
                outlinetokens[cind['theta']] = missinglinetokens[cind['theta']]
                outlinetokens[cind['phi']] = missinglinetokens[cind['phi']]
                outlinetokens[cind['sample']] = missinglinetokens[cind['sample']]
                outlinetokens[cind['line']] = missinglinetokens[cind['line']]
                outlinetokens[cind['ndi']] = "{0:d}".format(-2)
                outlinetokens[cind['clabel']] = "{0:d}".format(-1)
                outlinetokens[cind['cluster_class']] = "{0:d}".format(-1)
                outlinetokens[cind['class']] = "{0:d}".format(-1)
                outline = ",".join(outlinetokens)+"\n"
                fixedfobj.write(outline)
            # copy the line in the classified point cloud
            fixedfobj.write(classline)
            if i % 100 == 0:
                sys.stdout.write("Fixing progress: {0:d} lines          \r".format(i))

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
