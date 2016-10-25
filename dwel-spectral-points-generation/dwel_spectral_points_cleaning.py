#!/usr/bin/env python
"""
Clean a dual-wavelength spectral point cloud with a simple apparent refletance
intensity at both wavelengths.
"""

import argparse
import sys

import numpy as np

def getCmdArgs():
    p = argparse.ArgumentParser(description="Clean dual-wavelength spectral point cloud")

    p.add_argument('-i', '--inpts', dest='inptsfile', default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt", help="Input spectral point cloud file")
    p.add_argument('-t', '--thresh', dest='thresh', default=0.075, type=float, help="Threshold for apparent reflectance")
    p.add_argument('-o', '--outpts', dest='outptsfile', default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_signal.txt", help="Output cleaned spectral point cloud file")
    p.add_argument('-v', '--verbose', dest='verbose', default=False, action="store_true", help="verbose")

    cmdargs = p.parse_args()

    if (cmdargs.inptsfile is None) or (cmdargs.outptsfile is None):
        p.print_help()
        print "Input and output files must be set!"
        sys.exit()

    return cmdargs

def main(cmdargs):
    inptsfile = cmdargs.inptsfile
    outptsfile = cmdargs.outptsfile
    thresh = cmdargs.thresh * 1e3 # conver to unit of 1e3

    verbose = cmdargs.verbose

    cind = {'x':0, 'y':1, 'z':2, \
                'd_i_nir':3, 'd_i_swir':4, \
                'number_of_returns':6, 'range':8, \
                'fwhm_nir':13, 'fwhm_swir':14, \
                'qa':15}
    
    with open(inptsfile, 'r') as inpts, open(outptsfile, 'w') as outpts:
        for i in range(3):
            outpts.write(inpts.readline())
        for i, line in enumerate(inpts):
            linetokens = line.rstrip('\r\n').split(',')
            if int(linetokens[cind['number_of_returns']])==0:
                outpts.write(line)
            else:
                if (float(linetokens[cind['d_i_nir']]) > thresh) \
                        or (float(linetokens[cind['d_i_swir']]) > thresh):
                    outpts.write(line)
            if verbose:
                if i % 100 == 0:
                    sys.stdout.write('Cleaning line {0:d}       \r'.format(i))
                    sys.stdout.flush()

if __name__=="__main__":
    cmdargs=getCmdArgs()
    main(cmdargs)
