#!/usr/bin/env python
"""
Convert and simplify a point cloud file from IDL DWEL preprocessing programs to
an ASCII format, space separated text file,
x y z intensity

USAGE:

    dwel_points2ascii.py -i <string> -o <string> [--cx <integer> --cy <integer>
    --cz <integer> --ci <integer>]

OPTIONS:

    -i <string>, --input <string>
    (required) input csv file name

    -o <string>, --output <string>
    (required) output space-separated ascii file name

    --cx <integer>
    column index of x coordinate of a point, first column is indexed 1.
    [default: 1]

    --cy <integer>
    column index of y coordinate of a point, first column is indexed 1.
    [default: 2]

    --cz <integer>
    column index of z coordinate of a point, first column is indexed 1.
    [default: 3]

    --ci <integer>
    column index of intensity of a point, first column is indexed 1.
    [default: 4]

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu

"""

import sys
import optparse
import csv
import numpy as np
from StringIO import StringIO

def points2ascii(infile, outfile, cind={'x':1, 'y':2, 'z':3, 'I':4}):
    """
    Actual function to execute conversion from csv file to ascii file

    Args:
        infile (string): name of input csv file of DWEL point cloud.

        outfile (string): name of output space-separated ascii file of DWEL
        point cloud.

        cind (dict): column indexes of x, y, z and intensity, first column is
        indexed 1, e.g. {'x':1, 'y':2, 'z':3, 'I':4}.

    Returns:
        (integer), error code of function running. 
    """

    ind = [cind['x'], cind['y'], cind['z'], cind['I']]
    with open(infile, 'r') as incsv:
        with open(outfile, 'w') as outascii:
            ptsreader = csv.reader(incsv, delimiter=',')
            ptswriter = csv.writer(outascii, delimiter=' ')
            # skip the first three line
            for i in range(3):
                ptsreader.next()
            for row in ptsreader:
                ptswriter.writerow([ row[i] for i in ind ])
    return 0

def main(cmdargs):
    """
    Take inputs from command line and pass them to correct functions
    """

    infile = cmdargs.infile
    outfile = cmdargs.outfile
    cind = {'x':int(cmdargs.cind_x)-1, 'y':int(cmdargs.cind_y)-1,
            'z':int(cmdargs.cind_z)-1, 'I':int(cmdargs.cind_i)-1}

    points2ascii(infile, outfile, cind)

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()
        p.add_option("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt", help="Input csv file of DWEL point cloud data")
        p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_ascii.txt", help=("Out""put space-separated ascii file of simplified DWEL point cloud"))
        p.add_option("--cx", dest="cind_x", default="1", help="column index of x coordinate of a point, first column is indexed 1. [default: 1]")
        p.add_option("--cy", dest="cind_y", default="2", help="column index of y coordinate of a point, first column is indexed 1. [default: 2]")
        p.add_option("--cz", dest="cind_z", default="3", help="column index of z coordinate of a point, first column is indexed 1. [default: 3]")
        p.add_option("--ci", dest="cind_i", default="4", help="column index of intensity of a point, first column is indexed 1. [default: 4]")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        # if (self.infile is None) | (self.outfile is None):
        #     p.print_help()
        #     print "Both input and output file names are required."
        #     sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
