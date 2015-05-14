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
import optparse
import numpy as np
import csv

def slice_points(points, boundbox={'azimuth':[0.0, 360.0]}, cind={'azimuth':10}):
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
    for k in cind:
        selectflag = np.logical_and(selectflag, \
            points[:, cind[k]] >= boundbox[k][0])
        selectflag = np.logical_and(selectflag, \
            points[:, cind[k]] <= boundbox[k][1])

    return selectflag

def main(cmdargs):
    """
    Takes in inputs from command line and pass them to the correct functions.
    """

    # set some parameters
    headerlines = 3

    # read inputs from command line
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    minaz = cmdargs.minaz
    maxaz = cmdargs.maxaz
    azind = cmdargs.azx-1

    # set up bounding box
    boundbox = {'azimuth':[minaz, maxaz]}
    cind={'azimuth':azind}

    # read points from text file
    points = np.loadtxt(infile, delimiter=',', skiprows=headerlines, comments=None)
    rowflag = slice_points(points, boundbox, cind)

    # get the original header lines to the slice point cloud file.
    with open(infile, 'r') as inf:
        headerstr = ""
        for i in range(headerlines):
            headerstr = headerstr + inf.readline()

    # write sliced points
    np.savetxt(outfile, points[rowflag, :], delimiter=',', fmt='%.3f', \
        header=headerstr.rstrip())

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()
        p.add_option("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.550.txt", help="Input csv file of DWEL point cloud data")
        p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.550_small.txt", help=("Output csv file of sliced DWEL point cloud"))
        p.add_option("--azx", dest="azx", type="int", default=11, help="Column index of azimuth, with first column being 1. [default: 11")
        p.add_option("--minaz", dest="minaz", type="float", default=0.0, help="Minimum azimuth, unit, deg. [default: 0.0]")
        p.add_option("--maxaz", dest="maxaz", type="float", default=360.0, help="Maximum azimuth, unit, deg. [default: 360.0]")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.infile is None) | (self.outfile is None):
            p.print_help()
            print "Both input and output file names are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)

