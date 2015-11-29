#!/usr/bin/env python
"""
Slice DWEL point cloud according to bounding box given by one or multiple of
azimuth, zenith, range, x, y, or z

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu
"""

import sys
import argparse
import numpy as np
import csv

# def slice_points(points, boundbox={'azimuth':[0.0, 360.0]}, cind={'azimuth':10}):
def slice_points(points, boundbox={}, cind={}):
    """
    Slice point cloud with given bounding box.

    Args:

        points (2D numpy array, [npts, nrecs]): points from DWEL scans. npts
        points (rows), nrecs records (columns).

        boundbox (dict): bounding box for slicing. {'field_name':[field_min,
        field_max]}.

        cind (dict): column indexes of the fields used in slicing, with 0 being
        the first. {'field_name':column_index}. 'field_name' should be the same
        with that in boundbox.

    Returns:

        (1D numpy array): boolean row index of sliced points given the bounding
        box.
    
    """

    npts = points.shape[0]
    selectflag = np.ones(npts, dtype=np.bool_)

    if len(boundbox) == 0:
        return selectflag
    else:
        for k in boundbox:
            if k in cind:
                selectflag = np.logical_and(selectflag, \
                                                points[:, cind[k]] >= boundbox[k][0])
                selectflag = np.logical_and(selectflag, \
                                                points[:, cind[k]] <= boundbox[k][1])
            else:
                if k == "hrange":
                    if not (("xidx" in cind) and ("yidx" in cind)):
                        raise RuntimeError("xidx or yidx not exist in cind for slicing with horizontal range")
                    hrange = np.sqrt(points[:, cind['xidx']]**2 + points[:, cind['yidx']]**2)
                    selectflag = np.logical_and(selectflag, \
                                                    hrange >= boundbox[k][0])
                    selectflag = np.logical_and(selectflag, \
                                                    hrange <= boundbox[k][1])
                else:
                    raise RuntimeError("Slicing condition not implemented yet!")

    return selectflag

def main(cmdargs):
    """
    Takes in inputs from command line and pass them to the correct functions.
    """

    # set some parameters
    headerlines = cmdargs.skip_header # number of header lines

    # read inputs from command line
    infile = cmdargs.infile
    outfile = cmdargs.outfile

    boundbox = dict()
    cind=dict()
    cind['numreturnidx'] = cmdargs.numreturnidx
    # set up slicing conditions
    if cmdargs.azimuth:
        minaz = cmdargs.minaz
        maxaz = cmdargs.maxaz
        azind = cmdargs.azidx-1
        boundbox['azimuth'] = [minaz, maxaz]
        cind['azimuth'] = azind
    if cmdargs.hrange:
        minhr = cmdargs.minhr
        maxhr = cmdargs.maxhr
        boundbox['hrange'] = [minhr, maxhr]
        cind['x'] = cmdargs.xidx
        cind['y'] = cmdargs.yidx
        cind['z'] = cmdargs.zidx

    # read points from text file
    points = np.loadtxt(infile, delimiter=',', skiprows=headerlines, comments=None)
    rowflag = slice_points(points, boundbox, cind)

    with open(infile, 'r') as infobj, open(outfile, 'wt') as outfobj:
        for i in range(headerlines):
            outfobj.write(infobj.readline())
        for i, line in enumerate(infobj):
            if rowflag[i] or points[i, cind['numreturnidx']]==0:
                outfobj.write(line)
            if i % 1000 == 0:
                sys.stdout.write("Processed {0:d} lines               \r".format(i))

    # # get the original header lines to the slice point cloud file.
    # with open(infile, 'r') as infobj:
    #     headerstr = ""
    #     for i in range(headerlines):
    #         headerstr = headerstr + infobj.readline()

    # # write sliced points
    # np.savetxt(outfile, points[rowflag, :], delimiter=',', fmt='%.3f', \
    #     header=headerstr.rstrip())

def getCmdArgs():
    p = argparse.ArgumentParser(description="Slice a point cloud given conditions")
    # p.add_argument("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt", help="Input csv file of DWEL point cloud data")
    # p.add_argument("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed_small_test.txt", help=("Output csv file of sliced DWEL point cloud"))

    p.add_argument("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt", help="Input csv file of DWEL point cloud data")
    p.add_argument("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed_small_test.txt", help=("Output csv file of sliced DWEL point cloud"))

    p.add_argument("--skip_header", dest="skip_header", type=int, default=3, help="The number of lines to skip at the beginning of the file. Default: 3.")
    
    p.add_argument("--azimuth", dest="azimuth", default=False, action="store_true", help="Turn on slicing through azimuth")
    p.add_argument("--azidx", dest="azidx", type=int, default=None, help="Column index of azimuth, with first column being 1. [default: None]")
    p.add_argument("--minaz", dest="minaz", type=float, default=0.0, help="Minimum azimuth, unit, deg. [default: 0.0]")
    p.add_argument("--maxaz", dest="maxaz", type=float, default=360.0, help="Maximum azimuth, unit, deg. [default: 360.0]")

    p.add_argument("--hrange", dest="hrange", default=False, action="store_true", help="Turn on slicing through horizontal range")
    p.add_argument("--minhr", dest="minhr", type=float, default=0.0, help="Minimum horizontal range, unit, same with input. Default: 0.0")
    p.add_argument("--maxhr", dest="maxhr", type=float, default=None, help="Maximum horizontal range, unit, same with input. Default: none, maximum of input data")
    p.add_argument("--xidx", dest="xidx", type=int, default=1, help="Column index of X coordinates, with first column being 1. Default: 1")
    p.add_argument("--yidx", dest="yidx", type=int, default=2, help="Column index of Y coordinates, with first column being 1. Default: 2")
    p.add_argument("--zidx", dest="zidx", type=int, default=3, help="Column index of Z coordinates, with first column being 1. Default: 3")

    p.add_argument("--numreturnidx", dest="numreturnidx", type=int, default=7, help="Column index of number of returns, with first column being 1. Default: 7")

    cmdargs = p.parse_args()
    if (cmdargs.infile is None) | (cmdargs.outfile is None):
        p.print_help()
        print "Both input and output file names are required."
        sys.exit()
    if (cmdargs.azimuth) and (cmdargs.azidx is None):
        p.print_help()
        print "Column index of azimuth must be defined if you want to slice data with azimuth."
        sys.exit()

    return cmdargs

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)

