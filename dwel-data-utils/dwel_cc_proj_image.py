#!/usr/bin/env python
"""
Generate a color composite image from NIR and SWIR projection images with SWIR
as red, NIR as green and dark as blue.

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:
    Zhan Li, zhanli86@bu.edu
"""

import sys
import os
import optparse
import time

import numpy as np

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

from osgeo import gdal

gdal.AllRegister()

def main(cmdargs):
    nirfile = cmdargs.nirfile
    swirfile = cmdargs.swirfile
    ccfile = cmdargs.ccfile
    nbind = cmdargs.nirband
    sbind = cmdargs.swirband
    nmind = cmdargs.nirmask
    smind = cmdargs.swirmask

    print "Read input images"
    # read nir band
    nirds = gdal.Open(nirfile, gdal.GA_ReadOnly)
    nirband = nirds.GetRasterBand(nbind)
    nirdata = nirband.ReadAsArray(0, 0, nirband.XSize, nirband.YSize).astype(np.float32)
    nirmaskband = nirds.GetRasterBand(nmind)
    nirmask = nirmaskband.ReadAsArray(0, 0, nirmaskband.XSize, nirmaskband.YSize).astype(np.bool_)
    # read swir band
    swirds = gdal.Open(swirfile, gdal.GA_ReadOnly)
    swirband = swirds.GetRasterBand(nbind)
    if (swirband.XSize != nirband.XSize) or (swirband.YSize != nirband.YSize):
        print "Error, dimension of input NIR and SWIR images do not agree."
        return
    swirdata = swirband.ReadAsArray(0, 0, swirband.XSize, swirband.YSize).astype(np.float32)
    swirmaskband = swirds.GetRasterBand(smind)
    swirmask = swirmaskband.ReadAsArray(0, 0, swirmaskband.XSize, swirmaskband.YSize).astype(np.bool_)

    # close datasets
    nirds = None
    swirds = None

    mask = np.logical_and(nirmask, swirmask)
    inv_mask = np.logical_not(mask)
    nirdata[inv_mask] = 255
    swirdata[inv_mask] = 255

    # Generate RGB information with 2% linear stretch, default setting in ENVI
    nirrgb = image_stretch(nirdata, mask, 2)
    swirrgb = image_stretch(swirdata, mask, 2)
    nirrgb[inv_mask] = 255
    swirrgb[inv_mask] = 255
    darkrgb = np.zeros_like(swirrgb) + 255 # white background
    darkrgb[mask] = 0
    alphargb = np.zeros_like(swirrgb) + 255
    # create dark blue band
    darkdata = np.zeros_like(swirdata, dtype=np.float32) + 255 # white background
    darkdata[mask] = 0

    print "Write color composite image"

    dpi = 300
    outimage = np.dstack((swirrgb, nirrgb, darkrgb, alphargb))
    outpngfile = ".".join(ccfile.split('.')[:-1])+".png"
    mpl.image.imsave(outpngfile, outimage, dpi=dpi, format='png')
    
    # write color composite image
    outformat = "ENVI"
    driver = gdal.GetDriverByName(outformat)
    outds = driver.Create(ccfile, darkdata.shape[1], darkdata.shape[0], 3, gdal.GDT_Float32)
    outband = outds.GetRasterBand(1)
    outband.WriteArray(swirdata)
    outband.SetDescription("SWIR")
    outds.FlushCache()
    outband = outds.GetRasterBand(2)
    outband.WriteArray(nirdata)
    outband.SetDescription("NIR")
    outds.FlushCache()
    outband = outds.GetRasterBand(3)
    outband.WriteArray(darkdata)
    outband.SetDescription("Dark constant")
    outds.FlushCache()
    # ENVI meta data
    envi_meta_dict = dict(create_time=time.strftime("%c"), \
                          source_files="{{{0:s}, \n{1:s}}}".format(swirfile, nirfile), \
                          source_bands="{{{0:d}, \n{1:d}}}".format(sbind, nbind))
    for kw in envi_meta_dict.keys():
        outds.SetMetadataItem(kw, envi_meta_dict[kw], "ENVI")

    # close the dataset
    outds = None

def image_stretch(image, mask, q):
    validpix = image[mask]
    rgb = np.zeros_like(image, dtype=np.uint8)
    lb = np.percentile(validpix, q)
    ub = np.percentile(validpix, 100-q)
    blackpixmask = validpix<lb
    whitepixmask = validpix>ub
    graypixmask = np.logical_and(validpix>=lb, validpix<=ub)
    rgbvec = rgb[mask]
    rgbvec[blackpixmask] = 0
    rgbvec[whitepixmask] = 255
    rgbvec[graypixmask] = ((validpix[graypixmask]-lb)/(ub-lb)*255).astype(np.int)
    rgb[mask] = rgbvec
    return rgb


class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        p.add_option("-n", "--nirfile", dest="nirfile", default=None, help="Input projection image of DWEL scan at NIR band")
        p.add_option("-s", "--swirfile", dest="swirfile", default=None, help="Input projection image of DWEL scan at SWIR band")
        p.add_option("-c", "--ccfile", dest="ccfile", default=None, help="Output color composite image of DWEL scan")

        p.add_option("--nb", dest="nirband", default=1, type="int", help="Index of band in NIR image file for color composite image, with first band being 1. Default: 1")
        p.add_option("--sb", dest="swirband", default=1, type="int", help="Index of band in SWIR image file for color composite image, with first band being 1. Default: 1")

        p.add_option("--nm", dest="nirmask", default=2, type="int", help="Index of mask band in NIR image file for color composite image, with first band being 1. Default: 2")
        p.add_option("--sm", dest="swirmask", default=2, type="int", help="Index of mask band in SWIR image file for color composite image, with first band being 1. Default: 2")

        p.add_option("--linear_strech_pct", dest="linear_strech_pct", type="float", default=2.0, help="Percentile, a% of pixel values for linear stretch, i.e. a% percentile to (100-a)% percentile of pixel values will be stretched to darkest to brightest. Default: 2.0")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.nirfile is None) | (self.swirfile is None) | (self.ccfile is None):
            p.print_help()
            print "Both input and output file names are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
