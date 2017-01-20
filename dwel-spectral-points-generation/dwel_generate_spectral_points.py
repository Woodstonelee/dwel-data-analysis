#!/usr/bin/env python
"""
Generate a dual-wavelength spectral point cloud from two point clouds at the two
wavelengths out of DWEL scans. Create a single point cloud with dual-wavelength
intensities from union of the two point clouds. If one point at one wavelength
has no couterpart at the other, shot-by-shot NDI image is used to sythesize the
point intensity at the wavelength of no return.

USAGE:

    dwel_spectral_points_generator.py --nir <string> --swir <string> -o <string>
    [-r <float>]

OPTIONS:

    --nir <string>
    (required) name of input point cloud file of NIR band.

    --swir <string>
    (required) name of input point cloud file of SWIR band.

    -o <string>, --output <string>
    (required) name of output dual-wavelength point cloud file

    -r <float>, --rdiff <float>
    a threshold of range difference between the two wavelengths to determine if
    two points are common points from the same target. [default: 0.75 m]

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu

"""

import sys
import time
import argparse

from dwel_spectral_points import DWELSpectralPoints

def getCmdArgs():
    p = argparse.ArgumentParser(description="Generate dual-wavelength spectral point cloud from two point clouds at two wavelengths from a DWEL scan")
    
    p.add_argument("-n", "--nir", dest="nirfile", required=True, default=None, help="Input point cloud file of NIR band")
    p.add_argument("-s", "--swir", dest="swirfile", required=True, default=None, help="Input point cloud file of SWIR band")
    p.add_argument("-o", "--output", dest="outfile", required=True, default=None, help="Output dual-wavelength point cloud file")

    p.add_argument("-R", "--rdiff", dest="rdiff_thresh", type=float, default=0.96, help="a threshold of range difference between the two wavelengths to determine if two points are common points from the same target. [default: 0.96 m]")
    p.add_argument("-c", "--cols", dest="ncols", type=int, default=1022, help="Number of columns (samples) in the AT projection where points are generated. [default: 1022]")
    p.add_argument("-r", "--rows", dest="nrows", type=int, default=3142, help="Number of rows (lines) in the AT projection where points are generated. [default: 3142]")

    p.add_argument("--union", dest="union", default=False, action="store_true", help="Add more points in the output spectral point cloud with union of two point clouds. Point intensity will be synthesized with shot-by-shot NDI for points which have return at one wavelength but no return at the other. If set, must provide an NDI image for intensity synthesis. Default: false")
    p.add_argument("--ndi", dest="ndiimgfile", default=None, help="Shot-by-shot NDI image file for point intensity synthesis")
    
    p.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Turn on verbose. Default: false")

    cmdargs = p.parse_args()

    if (cmdargs.nirfile is None) or (cmdargs.swirfile is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Two input point cloud files and one output file are required"
        sys.exit()

    if (cmdargs.union) and (cmdargs.ndiimgfile is None):
        p.print_help()
        print "NDI image file is required for spectral point cloud from union of two point clouds"
        sys.exit()

    return cmdargs

def main(cmdargs):
    nirfile = cmdargs.nirfile
    swirfile = cmdargs.swirfile
    outfile = cmdargs.outfile
    rdiff_thresh = cmdargs.rdiff_thresh
    nrows = cmdargs.nrows
    ncols = cmdargs.ncols

    union = cmdargs.union
    ndiimgfile = cmdargs.ndiimgfile

    spectral_points_obj = DWELSpectralPoints(nirfile, swirfile, rdiff_thresh, \
                                                 nrows=nrows, ncols=ncols, verbose=cmdargs.verbose)
    spectral_points_obj.generateSpectralPoints(outfile, union=union, ndiimgfile=ndiimgfile)

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
