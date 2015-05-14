"""
Detrend NDI with a given piecewise linear function.

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:
    Zhan Li, zhanli86@bu.edu
"""

import sys
import optparse
import functools
import time

import numpy as np

def main(cmdargs):
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    parfile = cmdargs.parfile

    indexcol = cmdargs.index - 1 
    rangecol = cmdargs.range - 1 

    print "input file" + infile
    print "output file" + outfile
    print "parameter file" + parfile
    print "column of index" + str(indexcol)
    print "column of range" + str(rangecol)
    
    # read parameter file and construct a function list
    par = np.loadtxt(parfile, dtype=np.float, comments=None, delimiter=',', \
                         skiprows=1)
    funclist = []
    npieces = par.shape[0]
    for p in range(npieces):
        funclist.append(functools.partial(np.polyval, par[p, 2:]))

    # read points
    print "Loading input point cloud"
    data = np.loadtxt(infile, dtype=np.float32, delimiter=',', comments=None, \
                          skiprows=3)
    # construct a condition list
    condlist = []
    par[0, 0] = 0.0
    par[-1, 1] = np.max(data[:, rangecol])+1
    for p in range(npieces):
        condlist.append(np.logical_and( \
                np.greater_equal(data[:, rangecol], par[p, 0]), \
                    np.less(data[:, rangecol], par[p, 1])) )

    indextrend = np.piecewise(data[:, rangecol], condlist, funclist)

#    import pdb; pdb.set_trace()
    # detrend index!
    detrendindex = data[:, indexcol] - indextrend
    # write detrended index
    print "Writing detrended point cloud"
    outmat = np.hstack((data, detrendindex.reshape(len(detrendindex), 1)))
    prefixstr = "[DWEL Dual-wavelength Point Cloud Classification After Detrending index" \
        + ". Label, 1=others, 2=leaves] " \
        + "[Predefined threshold = "+"{0:.3f}".format(-1.0)+"]\n" \
        + "Run made at: " + time.strftime("%c")+"\n"
    headerstr = prefixstr + "x,y,z,d_I_nir,d_I_swir,shot_number,range,theta," \
        +"phi,sample,line,fwhm_nir,fwhm_swir,multi-return,sindex,label,R,G,B,dt_sindex"
    # write to file
    print "Saving classification by after detrending index"
    fmtstr = "%.3f "*5 + "%d " + "%.3f "*3 + "%d "*2 + "%.3f "*2 + "%d " \
        + "%.3f " + "%d "*4 + "%.3f"
    fmtstr = fmtstr.strip().split(" ")
    np.savetxt(outfile, \
                   outmat, \
                   delimiter=',', \
                   fmt=fmtstr, \
                   header=headerstr.rstrip())

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        p.add_option("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_small_class_NDI_thresh_0.550.txt", help="csv file, input point cloud with spectral index added in a column")
        p.add_option("-p", "--par", dest="parfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/tmp_ndi_summary_pwreg1st_range_vs_ndi.txt", help="csv file, parameters of piecewise linear function to detrend spectral index")
        p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_small_class_NDI_thresh_0.550_detrend.txt", help="csv file, output point cloud with detrended spectral index in an add-on column")
        p.add_option("-x", "--index", dest="index", default=15, type="int", help="Column index of spectral index in input files, with first column being 1. Default: 15")
        p.add_option("-r", "--range", dest="range", default=7, type="int", help="Column index of range in input files, with first column being 1. Default: 7")


        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.infile is None) | (self.outfile is None):
            p.print_help()
            print "Both input file and output file are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
