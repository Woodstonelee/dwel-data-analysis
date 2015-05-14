#!/usr/bin/env python
"""
Cacluate NDI image from AT projection images of two wavelengths and fill gaps in
the NDI image where no returns from a laser shot at one wavelength.

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:

    Zhan Li, zhali86@bu.edu
"""

import sys, os, argparse
import time

from osgeo import gdal

import numpy as np

from sklearn import neighbors

# import matplotlib as mpl
# mpl.use('TkAgg')
# import matplotlib.pyplot as plt

gdal.AllRegister()

def getCmdArgs():
    p = argparse.ArgumentParser(description=("Calculate NDI image from AT projection images of two wavelengths and fill gap shots of no return at one wavelength using K-nearest-neighbor algorithm"))

    p.add_argument("-n", "--nirimg", dest="nirimg", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140608_C_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img", help="AT projection of pcinfo (apparent reflectance) at NIR band")
    p.add_argument("-s", "--swirimg", dest="swirimg", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140608_C_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img", help="AT projection of pcinfo (apparent reflectance) at SWIR band")
    p.add_argument("-o", "--outimg", dest="outimg", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140608_C_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi_gapfilled.img", help="AT projection of gap-filled NDI image")

    p.add_argument("-k", dest="knn", type=int, default=3, help="Number of nearest neighbors to fill the gap")

    cmdargs = p.parse_args()
    if (cmdargs.nirimg is None) or (cmdargs.swirimg is None) or (cmdargs.outimg is None):
        p.print_help()
        print("Input image files and output image files must be set.")
        sys.exit()

    return cmdargs
        
def main(cmdargs):
    nirimg = cmdargs.nirimg
    swirimg = cmdargs.swirimg
    outimg = cmdargs.outimg
    knn = cmdargs.knn
    
    ndigapfillobj = dwelNDIImgGapFill(nirimg, swirimg, outimg)
    print "Filling NDI gaps ..."
    ndigapfillobj.fillNDIGap(knn)
    print "Writing NDI to ENVI image"
    ndigapfillobj.writeNDI(outimg)

class dwelNDIImgGapFill:
    """
    Generate gap-filled NDI image from DWEL scans using K-nearest-neighbors
    regressor. "Gaps" here means one wavelength has returns while the other has
    none.
    """
    def __init__(self, nirfile, swirfile, outfile, \
                     rhoband=2, nhitsband=1, maskband=13):
        """
        Args:

            rhoband: band index of apparent reflectance, with first being 1.
        """
        self.nirfile = nirfile
        self.swirfile = swirfile
        self.outfile = outfile

        self.rhoband = rhoband
        self.nhitsband = nhitsband
        self.maskband = maskband

        self.ndi = None
        self.mask = None

    def readImage(self, imgfile, band):
        """
        Read a band from an image file
        """
        imgds = gdal.Open(imgfile, gdal.GA_ReadOnly)
        imgband = imgds.GetRasterBand(band)
        imgdata = imgband.ReadAsArray(0, 0, imgband.XSize, imgband.YSize)
        imgds = None
        return imgdata

    def fillGap(self, X, y, T, knn):
        """
        Fill gaps at locations given by T from data points of y at locations
        given by X, using KNN regressor.
        """
        knnobj = neighbors.KNeighborsRegressor(knn)
        return knnobj.fit(X, y).predict(T)

    def fillNDIGap(self, knn):
        """
        Main function of gap filling.
        Cacluate NDI image, find gaps and fill them.

        Returns:

            ndi (2D numpy array): gap-filled NDI

            mask (2D numpy array): 0, invalid shot if both NIR and SWIR claim
            invalid; 1, measured NDI; 2: filled NDI; 3: no-return but valid
            shots
        """
        nirrho = self.readImage(self.nirfile, self.rhoband).astype(np.float_)
        nirnhits = self.readImage(self.nirfile, self.nhitsband).astype(np.int)
        nirmask = self.readImage(self.nirfile, self.maskband).astype(np.bool_)
        
        swirrho = self.readImage(self.swirfile, self.rhoband).astype(np.float_)
        swirnhits = self.readImage(self.swirfile, self.nhitsband).astype(np.int)
        swirmask = self.readImage(self.swirfile, self.maskband).astype(np.bool_)

        hitmask = np.logical_and(np.greater(nirnhits, 0), np.greater(swirnhits, 0))
        if not hitmask.any():
            # no valid hit at all!
            print "Error, no shot has returns! Check your data"
            sys.exit()
        xhit, yhit = np.where(hitmask)
        nirrhohit = nirrho[hitmask]/nirnhits[hitmask]
        swirrhohit = swirrho[hitmask]/swirnhits[hitmask]

        ndi = np.zeros_like(nirrho)
        mask = np.zeros_like(nirrho, dtype=int) + 3
        tmpflag = np.logical_and(np.invert(nirmask), np.invert(swirmask))
        mask[tmpflag] = 0
        
        ndihit = (nirrhohit - swirrhohit) / (nirrhohit + swirrhohit)
        ndi[hitmask] = ndihit
        mask[hitmask] = 1
        
        nirgapmask = np.logical_and(np.equal(nirnhits, 0), np.greater(swirnhits, 0))
        swirgapmask = np.logical_and(np.greater(nirnhits, 0), np.equal(swirnhits, 0))

        if (not nirgapmask.any()) and (not swirgapmask.any()):
            # no gap
            print "No fillable gap."
            return ndi, mask

        gapmask = np.logical_or(nirgapmask, swirgapmask)
        xgap, ygap = np.where(gapmask)

        X = np.hstack((xhit.reshape(len(xhit), 1), yhit.reshape(len(yhit), 1))).astype(np.float32)
        T = np.hstack((xgap.reshape(len(xgap), 1), ygap.reshape(len(ygap), 1))).astype(np.float32)
        ndigap = self.fillGap(X, ndihit, T, knn)
        ndi[gapmask] = ndigap
        mask[gapmask] = 2

        self.ndi = ndi
        self.mask = mask
        
        return ndi, mask

    def writeNDI(self, outfile):
        """write gap-filled NDI to an ENVI image file"""
        if self.ndi is None or self.mask is None:
            print "Error, gap filled ndi is not computed yet. Use fillNDIGap to generate a NDI array first"
            return 1
        outformat = "ENVI"
        driver = gdal.GetDriverByName(outformat)
        outds = driver.Create(outfile, self.ndi.shape[1], self.ndi.shape[0], 2, gdal.GDT_Float32)
        outds.GetRasterBand(1).WriteArray(self.ndi)
        outds.FlushCache()
        outds.GetRasterBand(2).WriteArray(self.mask)
        outds.FlushCache()
        outds = None
        # write header file
        hdrfile = ".".join(outfile.rsplit('.')[0:-1]) + ".hdr"
        if os.path.isfile(hdrfile):
            os.remove(hdrfile)
            print "Default ENVI header file generated by gdal is removed: \n{0:s}".format(hdrfile)
        hdrfile = outfile + ".hdr"
        hdrstr = \
            "ENVI\n" + \
            "description = {\n" + \
            "NDI image with one-band-no-return shots filled from files, \n" + \
            self.nirfile + ", \n" + \
            self.swirfile + ", \n" + \
            "Create, [" + time.strftime("%c") + "]}\n" + \
            "samples = " + "{0:d}".format(self.ndi.shape[1]) + "\n" \
            "lines = " + "{0:d}".format(self.ndi.shape[0]) + "\n" \
            "bands = 2\n" + \
            "header offset = 0\n" + \
            "file type = ENVI standard\n" + \
            "data type = 4\n" + \
            "interleave = bsq\n" + \
            "sensor type = Unknown\n" + \
            "byte order = 0\n" + \
            "wavelength units = unknown\n" + \
            "band names = {NDI, mask}"
        with open(hdrfile, 'w') as hdrf:
            hdrf.write(hdrstr)

        print "NDI writing done!"
        return 0


if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
