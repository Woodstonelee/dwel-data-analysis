#!/usr/bin/env python
"""
tranform point clouds according to their transformation matrices, and merge them
together.

Zhan Li, zhanli86@bu.edu
Thu Jun  4 12:26:21 EDT 2015
"""

import sys
import argparse

import numpy as np

def getCmdArgs():
    p = argparse.ArgumentParser(description='Transform point clouds and merge them into one single file')

    # p.add_argument('-i', '--infiles', dest='infiles', nargs='+', default=['/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt', '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt'], help='One or multiple ASCII point cloud files to be transformed and merged. Tip: for the model point cloud, give a 4 by 4 eye matrix for the transformation matrix')
    # p.add_argument('--tmfiles', dest='tmfiles', nargs='+', default=['/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/tmpdir-single-scan-trkctr/manual_match_trkctr_tm_pts_icp_hfhd20140503_c2c.txt', '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/tmpdir-single-scan-trkctr/manual_match_trkctr_tm_pts_icp_hfhd20140503_e2c.txt'], help='One or multiple ASCII files of transformation matrix')
    # p.add_argument('-o', '--outfile', dest='outfile', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt', help='Output ASCII file of merged point cloud after transformation')

    p.add_argument('-i', '--infiles', dest='infiles', required=True, nargs='+', default=None, help='One or multiple ASCII point cloud files to be transformed and merged.')
    p.add_argument('--tmfiles', dest='tmfiles', required=True, nargs='+', default=None, help='One or multiple ASCII files of transformation matrix, must correspond to point cloud files one by one in order. Tip: for the model point cloud, give a 4 by 4 eye matrix for the transformation matrix.')
    p.add_argument('-o', '--outfile', dest='outfile', required=True, default=None, help='Output ASCII file of merged point cloud after transformation')
    
    p.add_argument('--pts_header', dest='pts_header', type=int, default=3, help='Line number of column header names in all the ASCII point cloud files, with the first line being 1. Default: 3')

    p.add_argument('--tm_skip_header', dest='tm_skip_header', type=int, default=0, help='Number of header lines to skip in the file of transformation matrix. Default: 0')

    p.add_argument('--addscanid', dest='addscanid', action='store_true', help='Append scan id as a column')

    p.add_argument('--xbbox', dest='xbbox', type=float, nargs=2, default=None, help='Bounding box of X coordinates. Default: None')
    p.add_argument('--ybbox', dest='ybbox', type=float, nargs=2, default=None, help='Bounding box of Y coordinates. Default: None')

    cmdargs = p.parse_args()

    if (cmdargs.infiles is None) or (cmdargs.tmfiles is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Input files of point clouds, transformation matrix, and output file are required!"
        sys.exit()

    if (len(cmdargs.infiles) != len(cmdargs.tmfiles)):
        p.print_help()
        print "Number of input files of point clouds must be the same as the number of files of transformation matrix."
        sys.exit()

    return cmdargs

def writeTransformed(infobj, tm, outfobj, addscanid=False, scan_id=0, \
                         xbbox=None, ybbox=None):
    for n, line in enumerate(infobj):
        linetokens = line.strip().split(',')
        xyz = [ float(lt) for lt in linetokens[0:3] ]
        newxyz = np.dot(tm[0:3, 0:3], np.array(xyz).T) + tm[0:3, 3]
        if xbbox is not None and ybbox is not None:
            # subset the points with a given bounding box
            if (newxyz[0]>=xbbox[0]) and (newxyz[0]<=xbbox[1]) and \
                    (newxyz[1]>=ybbox[0]) and (newxyz[1]<=ybbox[1]):
                if addscanid:
                    outline = "{0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{1:s},{2:d}\n".format(newxyz, ','.join(linetokens[3:]), scan_id)
                else:
                    outline = "{0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{1:s}\n".format(newxyz, ','.join(linetokens[3:]))
                outfobj.write(outline)
        else:
            if addscanid:
                outline = "{0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{1:s},{2:d}\n".format(newxyz, ','.join(linetokens[3:]), scan_id)
            else:
                outline = "{0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{1:s}\n".format(newxyz, ','.join(linetokens[3:]))
            outfobj.write(outline)


def main(cmdargs):
    # read transformation matrix
    tm_list = [ np.genfromtxt(f, comments=None, skip_header=cmdargs.tm_skip_header) for f in cmdargs.tmfiles ]
    # get the name of header line of point cloud ascii file
    preheader = ""
    with open(cmdargs.infiles[0], 'r') as infobj:
        for n, line in enumerate(infobj):
            if n == cmdargs.pts_header-1: # the header line
                headerstr = line
                break
            elif n == 0:
                preheader = preheader + "{0:s} [Multi-scan merged after registration transformation]\n".format(line.rstrip())
            else:
                preheader = preheader + line
    with open(cmdargs.outfile, 'w') as outfobj:
        outfobj.write(preheader)
        if cmdargs.addscanid:
            outfobj.write("{0:s},scan_id\n".format(headerstr.rstrip()))
        else:
            outfobj.write("{0:s}\n".format(headerstr.rstrip()))
        for n, inf in enumerate(cmdargs.infiles):
            sys.stdout.write("Transforming and writing the {0:d} file: {1:s}\n".format(n+1, inf))
            with open(inf, 'r') as infobj:
                # skip the first few lines before the header. actual data starts
                # after the header line
                for i in range(cmdargs.pts_header):
                    infobj.readline()
                writeTransformed(infobj, tm_list[n], outfobj, \
                                     addscanid=cmdargs.addscanid, scan_id=n+1, \
                                     xbbox=cmdargs.xbbox, ybbox=cmdargs.ybbox)


if __name__=="__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
