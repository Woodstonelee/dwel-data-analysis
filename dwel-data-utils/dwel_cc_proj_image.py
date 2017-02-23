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

    # Generate RGB information with 2% linear stretch, default setting in ENVI
    nirrgb = image_stretch(nirdata, mask, 2)
    swirrgb = image_stretch(swirdata, mask, 2)
    darkrgb = np.zeros_like(swirrgb)
    alphargb = np.zeros_like(swirrgb)
    alphargb[mask] = 255
    # create dark blue band
    darkdata = np.zeros_like(swirdata, dtype=np.float32)

    print "Write color composite image"

    dpi = 72
    outimage = np.dstack((swirrgb, nirrgb, darkrgb, alphargb))
    outpngfile = ".".join(ccfile.split('.')[:-1])+".png"
    mpl.image.imsave(outpngfile, outimage, dpi=dpi, format='png')
    
    # write color composite image
    outformat = "ENVI"
    driver = gdal.GetDriverByName(outformat)
    outds = driver.Create(ccfile, darkdata.shape[1], darkdata.shape[0], 3, gdal.GDT_Float32)
    outds.GetRasterBand(1).WriteArray(swirdata)
    outds.FlushCache()
    outds.GetRasterBand(2).WriteArray(nirdata)
    outds.FlushCache()
    outds.GetRasterBand(3).WriteArray(darkdata)
    outds.FlushCache()
    # close the dataset
    outds = None
    # Now write envi header file manually. NOT by gdal...which can't do this
    # job...  set header file
    # get header file name
    strlist = ccfile.rsplit('.')
    hdrfile = ".".join(strlist[0:-1]) + ".hdr"
    if os.path.isfile(hdrfile):
        os.remove(hdrfile)
        print "Old header file removed: " + hdrfile 
    hdrfile = ccfile + ".hdr"
    hdrstr = \
        "ENVI\n" + \
        "description = {\n" + \
        "Color composite projection image of DWEL data from, \n" + \
        nirfile + ", \n" + \
        swirfile + ", \n" + \
        "Create, [" + time.strftime("%c") + "]}\n" + \
        "samples = " + "{0:d}".format(darkdata.shape[1]) + "\n" \
        "lines = " + "{0:d}".format(darkdata.shape[0]) + "\n" \
        "bands = 3\n" + \
        "header offset = 0\n" + \
        "file type = ENVI standard\n" + \
        "data type = 4\n" + \
        "interleave = bsq\n" + \
        "sensor type = Unknown\n" + \
        "byte order = 0\n" + \
        "wavelength units = unknown\n" + \
        "band names = {SWIR, NIR, DARK}"
    with open(hdrfile, 'w') as hdrf:
        hdrf.write(hdrstr)

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
