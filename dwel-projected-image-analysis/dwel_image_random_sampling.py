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
import argparse
import warnings

from osgeo import gdal

import numpy as np

gdal.AllRegister()

def dwel_image_random_sampling(maskfile, outfile, classes=None, numsamples=100, \
                                   maskb=1, ancfile=None, ancb=1, \
                                   maskcircle=None):
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

        maskcircle (tuple): 3-element tuple giving (center_x, center_y, radius)
        of a circle within which random samples are drawn from.
    
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

    maskds = None

    validx, validy = np.nonzero(mask)
    # if a circle is given to define the area for random samples
    if maskcircle is not None:
        tmpflag = (validx - maskcircle[0])**2 + (validy - maskcircle[1])**2 <= maskcircle[2]**2
        validx = validx[tmpflag]
        validy = validy[tmpflag]

    # get the indices of valid samples for all classes
    validind = np.ravel_multi_index((validx, validy), \
                                        (maskband.YSize, maskband.XSize))
    if classes is None:
        if len(validind) >= numsamples:
            randind = np.random.permutation(len(validind))[:numsamples]
        else:
            print "Error: number of valid pixels is fewer than requested number of samples"
            print "No samples are generated. Exit"
            maskds = None
            return ()
        sampleind = validind[randind]
    else:
        numclass = len(classes)
        if numclass != len(numsamples):
            maskds = None
            raise RuntimeError('Number of classes is {0:d} while only {1:d} numbers for sample counts are given!'.format(numclass, len(numsamples)))
        else:
            mask_vec = mask.flatten()[validind]
            sampleind = [ draw_samples(validind[mask_vec==cls], ns) for cls, ns in zip(classes, numsamples) ]
            sampleind = np.hstack(sampleind)


    if addatt:
        ancatt = np.ravel(ancatt, order='C')
        sampleatt = ancatt[sampleind]
    samplepos = np.unravel_index(sampleind, (maskband.YSize, maskband.XSize), order='C')

    # convert pixel location to default coordinates for a raster in QGIS.
    ypos = samplepos[0].astype(float)*(-1) - 0.5
    xpos = samplepos[1].astype(float) + 0.5

    # write sampels to output file and attribute if they are supplied
    headerstr = \
        "Random samples from " + maskfile + "\n" + \
        "Band of mask = {0:d}\n".format(maskb) + \
        "Class code = "
    for cls in classes:
        headerstr += "{0:d}, ".format(cls)
    headerstr = headerstr.rstrip(', ') + "\nNumber of samples = "
    for ns in numsamples:
        headerstr += "{0:d}, ".format(ns)
    headerstr = headerstr.rstrip(', ') + "\n"

    numsamples = len(sampleind)
    if addatt:
        outmat = np.hstack(( xpos.reshape(numsamples, 1), \
                                 ypos.reshape(numsamples, 1), \
                                 sampleatt.reshape(numsamples, 1) ))
        headerstr = headerstr + \
            "Attributes from " + ancfile + "\n" + \
            "Band of attribute = {0:d}\n".format(ancb) + \
            "X, Y, Attribute"
        fmtstr = ['%.3f', '%.3f', '%.3f']
    else:
        outmat = np.hstack(( xpos.reshape(numsamples, 1), \
                                 ypos.reshape(numsamples, 1) ))
        headerstr = headerstr + \
            "Attributes None\n" + \
            "Band of attribute = None\n" + \
            "X, Y"
        fmtstr = ['%.3f', '%.3f']

    np.savetxt(outfile, outmat, fmt=fmtstr, delimiter=',', header=headerstr, comments="")


def draw_samples(pop_vec, num_samp):
    """
    Draw num_sample samples from a vector pop_vec. If number of elements in
    pop_vec is fewer than num_samp, raise an warning and use all elements in the
    pop_vec.
    """
    if len(pop_vec) < num_samp:
        warnings.warn("Number of samples {0:d} requested are larger than number of available samples {1:d}. \nAll available samples are used.".format(num_samp, len(pop_vec)), RuntimeWarning)
        return pop_vec
    else:
        randind = np.random.permutation(len(pop_vec))[:num_samp]
        return pop_vec[randind]

def main(cmdargs):
    maskfile = cmdargs.maskfile
    outfile = cmdargs.outfile
    classes = cmdargs.classes
    numsamples = cmdargs.numsamples
    maskb = cmdargs.maskb
    ancfile = cmdargs.ancfile
    ancb = cmdargs.ancb

    if cmdargs.center is None or cmdargs.radius is None:
        maskcircle = None
    else:
        maskcircle = (cmdargs.center[0], cmdargs.center[1], cmdargs.radius)
    dwel_image_random_sampling(maskfile, outfile, classes=classes, numsamples=numsamples, \
                                   maskb=maskb, ancfile=ancfile, ancb=ancb, \
                                   maskcircle=maskcircle)

def getCmdArgs():
    p = argparse.ArgumentParser(description="Generate random samples from a mask file")

    p.add_argument("-m", "--mask", dest="maskfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img", help="Input projection file where a mask is read, *.img associated with *.hdr")
    p.add_argument("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt", help="Output csv file of random samples")
    p.add_argument("-a", "--ancfile", dest="ancfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img", help="Input DWEL projection image of ancillary attributes to be added to random samples, *.img associated with *.hdr. If not given, no attributes will be added to random samples")
    
    # p.add_argument("-m", "--mask", dest="maskfile", default=None, help="Input projection file where a mask is read, *.img associated with *.hdr")
    # p.add_argument("-o", "--output", dest="outfile", default=None, help="Output csv file of random samples")
    # p.add_argument("-a", "--ancfile", dest="ancfile", default=None, help="Input DWEL projection image of ancillary attributes to be added to random samples, *.img associated with *.hdr. If not given, no attributes will be added to random samples")

    p.add_argument("--maskband", dest="maskb", default=1, type=int, help="Band index of mask in the mask file, with first band being 1. Default: 1")
    p.add_argument("-c", "--classes", dest="classes", type=int, nargs='+', default=None, help="Class codes for which random samples are generated. If none, use simple random sampling for all classess together and '--numsamples' should give one value. Otherwise, use stratified random sampling and number of class codes must be the same for the number of values for number of samples. Default: none")
    p.add_argument("-n", "--numsamples", dest="numsamples", type=int, nargs='+', default=(100), help="Number of random samples to be drawn for each class by a stratified random sampling. If only one value is given, simple random sampling for all classes together. Default: 100")
    p.add_argument("--ancband", dest="ancb", default=1, type=int, help="Band index of a layer in the ancillary image where random samples' attribute will be assigned from, with first band being 1. Default: 1")

    p.add_argument("--center", dest='center', type=int, nargs=2, metavar=('center_x', 'center_y'), default=None, help='Location of the center of a circle within which random samples are drawn from')
    p.add_argument("-r", "--radius", dest='radius', type=int, default=None, help='Radius of a circle within which random samples are drawn from')

    cmdargs = p.parse_args()
    if (cmdargs.maskfile is None) | (cmdargs.outfile is None):
        p.print_help()
        print "Both mask and output file names are required."
        sys.exit()

    return cmdargs

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
