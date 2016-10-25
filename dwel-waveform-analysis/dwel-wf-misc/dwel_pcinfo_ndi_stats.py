#!/usr/bin/env python
"""
Calculate NDI from total_d band of pcinfo image from DWEL preprocessing. Select
those single-return hits and generate the stats of NDI of these hits.

Zhan Li, zhanli86@bu.edu
Created: 20150202
"""

import optparse
import sys
import os

import numpy as np
from osgeo import gdal, gdalconst
import struct

import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
#from mpldatacursor import datacursor # a module to create a simple data cursor
# widget equivalent to MATLAB's datacursormode.

# register dataset formatl
gdal.AllRegister()

def dwel_ndi_image(nir_scan, swir_scan, mask):
    """
    Calculate NDI from total_d band of pcinfo image from DWEL
    preprocessing. Select those single-return hits and generate the stats of NDI
    of these hits.

    Parameters
    ----------
    nir_scan: numpy array
        NIR scanning image, should have the same dimension with swir_scan and
    mask. 
    swir_scan: numpy array
        SWIR scanning image, should have the same dimension with nir_scan and
    mask. 
    mask: numpy array
        mask of scanning image, 1 is good shot and 0 is bad shot, should have
    the same dimension with nir_scan and swir_scan
    
    Returns
    -------

    Raises
    ------ 
    """
    
    # calculate the NDI
    ndi = np.ones(shape=nir_scan.shape) * np.nan
    nonzero_ind = mask.nonzero()
    ndi[nonzero_ind] = np.float_(nir_scan[nonzero_ind] -
        swir_scan[nonzero_ind]) / np.float_(nir_scan[nonzero_ind] +
        swir_scan[nonzero_ind]) 
    return {'NDI':ndi, 'NO_DATA':np.nan}

def main(cmdargs):
    # nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHL_20140609_C_1064_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    # swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHL_20140609_C_1548_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    # nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_1064_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    # swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_1548_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    # site_name = ("Sierra Site 305 scan on 20130614")
    # intbandind = 5
    # maskbandind = 4
    # zenithbandind = 2
    # angle_scale = 10.0
    
    # nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp4_ptcl_pcinfo.img"
    # swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp4_ptcl_pcinfo.img"
    # site_name = ("Harvard Forest hardwood center scan on 20140919")

    nir_ancfile = cmdargs.nirfile
    swir_ancfile = cmdargs.swirfile

    outdir = cmdargs.outdir
    
    dual_ancfiles = {'nir':nir_ancfile, 'swir':swir_ancfile}

    nhitbandind = 1
    intbandind = 2
    maskbandind = 13
    zenithbandind = 9
    rgbandind = 7
    angle_scale = 100.0
    rg_scale = 100.0

    rgdiff_thresh = 0.75
    
    min_zenith = 0.0
    max_zenith = 115.0

    dual_ads = dict()
    # open the ancillary files of two bands
    for f in dual_ancfiles:
        dual_ads[f] = gdal.Open(dual_ancfiles[f], gdal.GA_ReadOnly)

    # read the waveform mean intensity band
    dual_wfmean = dict()
    for f in dual_ads:
        wfmean_band = dual_ads[f].GetRasterBand(intbandind)
        dual_wfmean[f] = wfmean_band.ReadAsArray(0, 0, wfmean_band.XSize, wfmean_band.YSize).astype(np.float_)

    # read the mask band
    dual_mask = dict()
    for f in dual_ads:
        mask_band = dual_ads[f].GetRasterBand(maskbandind)
        dual_mask[f] = mask_band.ReadAsArray(0, 0, mask_band.XSize, mask_band.YSize).astype(np.bool_)

    # read the band of number of hits
    dual_nhit = dict()
    for f in dual_ads:
        nhit_band = dual_ads[f].GetRasterBand(nhitbandind)
        dual_nhit[f] = nhit_band.ReadAsArray(0, 0, nhit_band.XSize, nhit_band.YSize).astype(np.int_)

    # read the band of mean range
    dual_meanrg = dict()
    for f in dual_ads:
        rg_band = dual_ads[f].GetRasterBand(rgbandind)
        dual_meanrg[f] = rg_band.ReadAsArray(0, 0, rg_band.XSize, rg_band.YSize).astype(np.float_)
        dual_meanrg[f] = dual_meanrg[f]/100.0
        
    # select nhit==1 shots, i.e. single-return shots, and the difference in the
    # mean range at the two wavelengths needs to be smaller than 0.75 m.
    mask_all = np.ones_like(dual_mask['nir'], dtype='bool_')
    mask_all = np.logical_and(mask_all, np.less(np.fabs(dual_meanrg['nir'] - dual_meanrg['swir']), rgdiff_thresh*np.ones_like(dual_meanrg['nir'])))
    for f in dual_mask:
        mask_all = np.logical_and(mask_all, dual_mask[f])
        mask_all = np.logical_and(mask_all, dual_nhit[f]==1)
    
    # calculate NDI image
    ndi = dwel_ndi_image(dual_wfmean['nir'], dual_wfmean['swir'], mask_all) 
    
    # plot intensity against range
    for f in dual_wfmean:
        plt.figure()
        plt.plot(dual_meanrg[f][mask_all].flatten(), dual_wfmean[f][mask_all].flatten(), '.')
        plt.xlabel(("mean range, meter"))
        plt.ylabel(("total_d, app refl"))
        plt.title(("peak intensity of single-return shots from pcinfo image, "+f))
        plt.savefig(os.path.join(outdir, "single_return_intensity_vs_range_"+f+".png"))
        plt.clf()

    # plot ndi against range
    plt.figure()
    plt.plot((dual_meanrg['nir'][mask_all]+dual_meanrg['swir'][mask_all]).flatten()/2.0, ndi['NDI'][mask_all].flatten(), '.')
    plt.xlabel(("mean range, meter"))
    plt.ylabel(("NDI"))
    plt.title(("NDI of single-return shots from pcinfo image, "))
    plt.savefig(os.path.join(outdir, "single_return_ndi_vs_range.png"))
    plt.clf()
    
    # close gdal datasets
    for f in dual_ads:
        dual_ads[f] = None

# Command arguments
class CmdArgs:
  def __init__(self):
    p = optparse.OptionParser()
    p.add_option("-n","--nirfile", dest="nirfile", default=None, help="DWEL pcinfo file of NIR")
    p.add_option("-s","--swirfile", dest="swirfile", default=None, help="DWEL pcinfo file of SWIR")
    p.add_option("--outdir", dest="outdir", default=os.getcwd(), help="Directory to store output results")
    (options, args) = p.parse_args()
    self.__dict__.update(options.__dict__)
    
    if (self.nirfile is None) | (self.swirfile is None):
        p.print_help()
        print "Both NIR and SWIR input filenames must be set."
        sys.exit()

# Run the script
if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
