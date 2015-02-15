#!/usr/bin/env python
"""
Generate random samples from a projection image of DWEL data. Currently only
support simply random sampling design.

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu
"""

import sys
import os
import optparse

from osgeo import gdal

import numpy as np

gdal.AllRegister()

def dwel_image_random_sampling(maskfile, outfile, numsamples=100, \
                                   maskb=1, ancfile=None, ancb=1):
    """
    Generate random samples from a mask image file of DWEL data. Currently only
    support simply random sampling design.

    Args:

        maskfile: mask image file. 1 (not 0) is valid pixels where random
        samples will be drawn from.

        maskb (int): band index of mask in the mask file, with first band being
        1.

        ancb (int): band index of anciilary attribute to attach to random
        samples, with first band being 1.
    
    Returns:

    """
    # read mask file
    maskds = gdal.Open(maskfile, gdal.GA_ReadOnly)
    maskband = maskds.GetRasterBand(maskb)
    mask = maskband.ReadAsArray(0, 0, maskband.XSize, maskband.YSize).astype(np.int)
    # read ancillary attribute band if it is given
    addatt = False
    if not (ancfile is None):
        ancds = gdal.Open(ancfile, gdal.GA_ReadOnly)
        ancband = ancds.GetRasterBand(ancb)
        if (ancband.XSize != maskband.XSize) or (ancband.YSize != maskband.YSize):
            print "Warning: Dimension of ancillary attribute image differs from input mask image."
            print "No attribute will be added"
        else:
            ancatt = ancband.ReadAsArray(0, 0, ancband.XSize, ancband.YSize)
            addatt = True
        ancds = None

    # get the indices of valid samples
    validind = np.ravel_multi_index(np.nonzero(mask), \
                                        (maskband.YSize, maskband.XSize))
    if len(validind) >= numsamples:
        randind = np.random.permutation(len(validind))[:numsamples]
    else:
        print "Error: number of valid pixels is fewer than requested number of samples"
        print "No samples are generated. Exit"
        maskds = None
        return ()
    
    sampleind = validind[randind]
    if addatt:
        ancatt = np.ravel(ancatt, order='C')
        sampleatt = ancatt[randind]
    samplepos = np.unravel_index(sampleind, (maskband.YSize, maskband.XSize), order='C')

    # write sampels to output file and attribute if they are supplied
    headerstr = \
        "Random samples from " + maskfile + "\n" + \
        "Band of mask = {0:d}\n".format(maskb) + \
        "Number of samples = {0:d}\n".format(numsamples)
    if addatt:
        outmat = np.hstack(( samplepos[1].reshape(numsamples, 1), \
                                 samplepos[0].reshape(numsamples, 1), \
                                 sampleatt.reshape(numsamples, 1) ))
        headerstr = headerstr + \
            "Attributes from " + ancfile + "\n" + \
            "Band of attribute = {0:d}\n".format(ancb) + \
            "X, Y, Attribute"
        fmtstr = ['%d', '%d', '%.3f']
    else:
        outmat = np.hstack(( samplepos[1].reshape(numsamples, 1), \
                                 samplepos[0].reshape(numsamples, 1) ))
        headerstr = headerstr + \
            "Attributes None\n" + \
            "Band of attribute = None\n" + \
            "X, Y"
        fmtstr = ['%d', '%d']

    np.savetxt(outfile, outmat, fmt=fmtstr, delimiter=',', header=headerstr)

    maskds = None

def main(cmdargs):
    maskfile = cmdargs.maskfile
    outfile = cmdargs.outfile
    numsamples = cmdargs.numsamples
    maskb = cmdargs.maskb
    ancfile = cmdargs.ancfile
    ancb = cmdargs.ancb
    
    dwel_image_random_sampling(maskfile, outfile, numsamples=numsamples, \
                                   maskb=maskb, ancfile=ancfile, ancb=ancb)

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        # p.add_option("-m", "--mask", dest="maskfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_nir_hsp2.img", help="Input projection file where a mask is read, *.img associated with *.hdr")
        # p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/test_hfhd20140919_c_dual_random_samples.txt", help="Output csv file of random samples")
        # p.add_option("-a", "--ancfile", dest="ancfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class_NDI_thresh_0.503.txt", help="Input DWEL projection image of ancillary attributes to be added to random samples, *.img associated with *.hdr. If not given, no attributes will be added to random samples")

        
        p.add_option("-m", "--mask", dest="maskfile", default=None, help="Input projection file where a mask is read, *.img associated with *.hdr")
        p.add_option("-o", "--output", dest="outfile", default=None, help="Output csv file of random samples")
        p.add_option("-a", "--ancfile", dest="ancfile", default=None, help="Input DWEL projection image of ancillary attributes to be added to random samples, *.img associated with *.hdr. If not given, no attributes will be added to random samples")

        p.add_option("--maskband", dest="maskb", default=1, type=int, help="Band index of mask in the mask file, with first band being 1. Default: 1")
        p.add_option("-n", "--numsamples", dest="numsamples", default=100, type=int, help="Number of random samples to be drawn. Default: 100")
        p.add_option("--ancband", dest="ancb", default=1, type=int, help="Band index of a layer in the ancillary image where random samples' attribute will be assigned from, with first band being 1. Default: 1")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.maskfile is None) | (self.outfile is None):
            p.print_help()
            print "Both mask and output file names are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
