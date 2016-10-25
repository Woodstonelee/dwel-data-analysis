"""
Find the difference between two point clouds and output the difference point
cloud, given a distance threshold to determine if two points are at the same
location.

Zhan Li, zhanli86@bu.edu
Thu Jun  4 17:33:38 EDT 2015
"""

import sys
import argparse
import time

import numpy as np
from sklearn.neighbors import NearestNeighbors

def getCmdArgs():
    p = argparse.ArgumentParser(description='Find and output the difference between two point clouds, given a distance threshold to determine if two points are at the same location')

    p.add_argument('--pts1', dest='pts1', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt', help='File of the first point cloud. The difference = pts1 - pts2')
    p.add_argument('--pts2', dest='pts2', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/tmpdir-single-scan-trkctr/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_xyz_ground.txt', help='File of the second point cloud. The difference = pts1 - pts2')
    p.add_argument('-o', '--outfile', dest='outfile', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_noground.txt', help='Output file of the difference point cloud')

    cmdargs = p.parse_args()

    if (cmdargs.pts1 is None) or (cmdargs.pts2 is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Two input point cloud files and one output files are required!"
        sys.exit()

    return cmdargs

def main(cmdargs):
    pts1header = 3
    pts2header = 0
    # load first point cloud
    pts1 = np.genfromtxt(cmdargs.pts1, comments=None, skip_header=pts1header, delimiter=',', usecols=(0,1,2,23))
    # remove all zero-hit points
    nonzerohit_ind = np.where(pts1[:, 3]>0)[0]
    pts1 = pts1[nonzerohit_ind, :]
    # load second point cloud
    pts2 = np.genfromtxt(cmdargs.pts2, comments=None, skip_header=pts2header)

    npts1 = len(pts1)
    # combine the two point clouds
    ptsall = np.vstack((pts1[:, 0:3], pts2))

    # create a sklearn nearest neighbor object
    nbrs = NearestNeighbors(n_neighbors=2).fit(ptsall)
    distances, indices = nbrs.kneighbors(ptsall)
    unique_ind = np.where(distances[:, 1]>1e-6)[0]
    # indices of difference points in the first point cloud
    diff_ind = nonzerohit_ind[unique_ind[0:(len(unique_ind) if len(unique_ind)<npts1 else npts1)]]
    ndiff_ind = len(diff_ind)
    with open(cmdargs.pts1, 'r') as infobj, open(cmdargs.outfile, 'w') as outfobj:
        for i in range(pts1header):
            outfobj.write(infobj.readline())
        i=0
        for n, line in enumerate(infobj):
            if n==diff_ind[i]:
                outfobj.write(line)
                i += 1
            if i>=ndiff_ind:
                break

if __name__=="__main__":
    st = time.time()
    cmdargs = getCmdArgs()
    main(cmdargs)
    print "time: {0:.3f} seconds".format(time.time()-st)
