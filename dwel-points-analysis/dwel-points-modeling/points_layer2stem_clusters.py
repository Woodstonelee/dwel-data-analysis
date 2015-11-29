#!/usr/bin/env python
"""
Cluster a layer of points above ground into individual stems as point clusters.

Zhan Li, zhanli86@bu.edu
Sun Jun  7 16:58:07 EDT 2015
"""

import sys
import argparse

import itertools

import numpy as np
import skimage.feature as skf
import scipy.ndimage as spyimg

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

def getCmdArgs():
    p = argparse.ArgumentParser(description="Cluster a layer of points above ground into individual stems as point clusters.")

    p.add_argument('-i', '--infile', dest='infile', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/arrT_HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_xyz.txt', help='input file name of a layer of points above ground')
    p.add_argument('--cellsize', dest='cellsize', type=float, default=0.05, help='cell size to rasterize the XoY projection of points')
    p.add_argument('--minptsnum', dest='minptsnum', type=int, default=9, help='minimum number of points in a cluster')
    p.add_argument('-o', '--outfile', dest='outfile', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/new_arrT_HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_xyz.txt', help='output file name of points with cluster labels')

    cmdargs = p.parse_args()

    if (cmdargs.infile is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Input and output file names are required."
        sys.exit()

    return cmdargs

def rasterizePts(inptsfile, cellsize=0.05, projdir='Z'):
    """
    Project points along an axis given by projdir and rasterize the points to an image on the plane perpendicular to the projection axis.

    Args:

        inptsfile (string): file name of input points

    Keywords:

        cellsize (scalar, float): cell size to rasterize the points. default: 0.05.

        projdir (string): name of axis along which the points are projected. default: 'Z'

    Returns:

        ptsimg (2D numpy array, int): image from rasterizing points. Each pixel value is the number of points inside the pixel.
    """
    # define the indices of projected plane
    if projdir=='Z':
        xdimind = 0
        ydimind = 1
    elif projdir=='X':
        xdimind = 1
        ydimind = 2
    elif projdir=='Y':
        xdimind = 0
        ydimind = 2
    else:
        raise RuntimeError("Unknown name of projection axis")

    # read points
    pts = np.genfromtxt(inptsfile, comments=None, skip_header=0, usecols=(0,1,2))
    # get extent of the points
    minxyz = pts.min(axis=0)
    maxxyz = pts.max(axis=0)
    nrows = np.fix((maxxyz[ydimind] - minxyz[ydimind])/cellsize + 0.5) + 1
    ncols = np.fix((maxxyz[xdimind] - minxyz[xdimind])/cellsize + 0.5) + 1
    ptsimg = np.zeros((nrows, ncols), dtype=np.int)

    rind = (np.fix((pts[:, ydimind] - minxyz[ydimind])/cellsize + 0.5) ).astype(np.int)
    cind = (np.fix((pts[:, xdimind] - minxyz[xdimind])/cellsize + 0.5)).astype(np.int)

    for r, c in itertools.izip(rind, cind):
        ptsimg[r, c]+=1

    return ptsimg

def main(cmdargs):
    ptsimg = rasterizePts(cmdargs.infile, cellsize=cmdargs.cellsize)
    labelimg, nfeatures = spyimg.label(ptsimg, structure=np.ones((3,3)))

    # # check the image processing results
    # fig, ax = plt.subplots()
    # ax.imshow(labelimg)
    # ax.set_aspect('equal')
    # plt.show()

    labels = np.unique(labelimg)
    label_npts = np.array([ np.sum(labelimg==l) for l in labels ])
    for l, n in itertools.izip(labels, label_npts):
        if n < cmdargs.minptsnum:
            labelimg[labelimg==l]=-1

    # read points
    pts = np.genfromtxt(cmdargs.infile, comments=None, skip_header=0, usecols=(0,1,2))
    # get extent of the points
    minxyz = pts.min(axis=0)
    maxxyz = pts.max(axis=0)
    xdimind = 0
    ydimind = 1
    cellsize = cmdargs.cellsize
    rind = (np.fix((pts[:, ydimind] - minxyz[ydimind])/cellsize + 0.5) ).astype(np.int)
    cind = (np.fix((pts[:, xdimind] - minxyz[xdimind])/cellsize + 0.5)).astype(np.int)
    ptslabels = labelimg[rind, cind]

    # write labeled points
    np.savetxt(cmdargs.outfile, np.hstack((pts, np.reshape(ptslabels, (len(ptslabels), 1)))), \
                   fmt="%.3f,%.3f,%.3f,%d", header="x,y,z,tree_no", comments='')

    return 0

if __name__=="__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
