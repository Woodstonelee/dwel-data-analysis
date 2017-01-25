#!/usr/bin/env python
"""Segment DWEL point cloud based on an export ASCII file of point
cloud segment from CloudCompare, via the return number and shot number
in the DWEL point cloud.


Zhan Li, zhanli86@bu.edu
Created: Tue Oct  4 16:50:21 EDT 2016

"""

import argparse

import numpy as np

def readCcSeg(cc_seg_file):
    return np.genfromtxt(cc_seg_file, delimiter=',', skip_header=1, \
                         usecols=(0,1,2,3,4), \
                         dtype="f,f,f,i,i", \
                         names=('x', 'y', 'z', 'return_number', 'shot_number'))

def readDwel(dwel_pts_file, delimiter=',', \
             skip_header=0, names=True, \
             usecols=None, dtype=np.float):
    return np.genfromtxt(dwel_pts_file, delimiter=delimiter, \
                         skip_header=0, names=True, case_sensitive="lower", 
                         comments="//", usecols=['x', 'y', 'z', 'return_number', 'shot_number'], \
                         dtype="f,f,f,i,i")

def ccSeg2DwelSeg(dwel_pts_file, cc_seg_file, dwel_seg_file):
    """Segment a DWEL point cloud, *dwel_pts_file*, based on the points
    given by a point segment from CloudCompare, *cc_seg_file*, via the
    provided return number and shot number in DWEL point clouds.

    Parameters: **dwel_pts_file**, *str*
                  File name of the input DWEL point cloud to be segmented.
                **cc_seg_file**, *str*
                  File name of the ASCII file of exported point cloud
                  segment from CloudCompare, providing the points to
                  be searched and extracted from *dwel_pts_file*.
                **dwel_seg_file**, *str*
                  File name of the output segment of input DWEL point
                  cloud *dwel_pts_file*, with all the attributed in
                  the *dwel_pts_file* attached to the segmented
                  points.
    """
    cc_seg_pts = readCcSeg(cc_seg_file)
    dwel_pts = readDwel(dwel_pts_file)

    in_flag = np.in1d(dwel_pts[['return_number', 'shot_number']], cc_seg_pts[['return_number', 'shot_number']])

    # # a quick debug to make sure we extracted the correct points from
    # # input DWEL point cloud.
    # cc_view = cc_seg_pts[['x', 'y', 'z']].view(cc_seg_pts.dtype['x']).reshape(cc_seg_pts[['x', 'y', 'z']].shape+(-1,))
    # dwel_view = dwel_pts[in_flag][['x', 'y', 'z']].view(dwel_pts.dtype['x']).reshape(dwel_pts[in_flag][['x', 'y', 'z']].shape+(-1,))
    # print np.sum(cc_view - dwel_view)

    skip_header = 3
    with open(dwel_pts_file, 'r') as dfobj, open(dwel_seg_file, 'w') as sfobj:
        # sfobj.write("{0:s} [CloudCompare segmentation extraction]\n".format(dfobj.readline().rstrip()))
        sfobj.write("{0:s}".format(dfobj.readline()))
        for i in range(1, skip_header):
            dfobj.readline()
        for flag in in_flag:
            line = dfobj.readline()
            if flag:
                sfobj.write(line)

def getCmdArgs():
    p = argparse.ArgumentParser(description="Segment DWEL point cloud based on an export ASCII file of point cloud segment from CloudCompare via the return number and shot number in the DWEL point cloud")

    p.add_argument("--inpts", dest="inpts", required=True, default=None, help="Input DWEL point cloud where a subset of points to be segemented from.")
    p.add_argument("--ccseg", dest="ccseg", required=True, default=None, help="ASCII file of point cloud segment from CloudCompare, providing return number and shot number as the two scalar fields in the file.")
    p.add_argument("--outpts", dest="outpts", required=True, default=None, help="Output DWEL point cloud segment of points given by the CloudCompare segment with all the attributes in the input point cloud.")

    cmdargs = p.parse_args()

    return cmdargs

def main(cmdargs):
    dwel_pts_file = cmdargs.inpts
    cc_seg_file = cmdargs.ccseg
    dwel_seg_file = cmdargs.outpts

    ccSeg2DwelSeg(dwel_pts_file, cc_seg_file, dwel_seg_file)

if __name__=="__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
