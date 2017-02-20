#!/usr/bin/env python
"""

Separate the no-hit points from the original DWEL point clouds and
output two ascii files, no-hit points and return points.

"""

import sys
import os
import argparse

import numpy as np

def sepDwelPcl(infile, outdir=None, skip_header=3, col_num_ret=7, verbose=False):
    """
    Separate the no-hit points from the original DWEL point clouds and
    output two ascii files, no-hit points and return points.
    """
    nreturns = np.genfromtxt(infile, delimiter=',', skip_header=skip_header, usecols=(col_num_ret-1)).astype(int)
    nohit_bool = nreturns == 0
    npts = len(nreturns)

    basename = ".".join(os.path.basename(infile).split('.')[0:-1])
    indir = os.path.dirname(infile)
    if outdir is None:
        outdir = indir    

    ret_outfile = os.path.join(outdir, "{0:s}_return.txt".format(basename))
    nohit_outfile = os.path.join(outdir, "{0:s}_nohit.txt".format(basename))

    with open(infile, 'r') as infobj, open(ret_outfile, 'w') as rfobj, open(nohit_outfile, 'w') as nfobj:
        for i in range(skip_header):
            line = infobj.readline()
            rfobj.write(line)
            nfobj.write(line)
        
        for i, line in enumerate(infobj):
            if nohit_bool[i]:
                nfobj.write(line)
            else:
                rfobj.write(line)
            if verbose and (i % 1000 == 0):
                sys.stdout.write("Sorting and writing {0:.2f} %   \r".format((i+1)/float(npts)*100))

def getCmdArgs():
    p = argparse.ArgumentParser(description="Separate original DWEL into return points and no-hit points")

    p.add_argument("-i", "--infile", dest="infile", required=True, default=None, help="Input original DWEL point cloud")
    p.add_argument("-o", "--outdir", dest="outdir", required=False, default=None, help="Output directory")

    p.add_argument("--skip_header", dest="skip_header", required=False, type=int, default=3, help="The number of lines to skip at the beginning of the file. Default: 3")
    p.add_argument("--col_num_ret", dest="col_num_ret", required=False, type=int, default=7, help="Column index of the number of returns, with the first column as 1. Default: 7")
    
    p.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Turn on verbose. Default: false")

    cmdargs =p.parse_args()

    return cmdargs

def main(cmdargs):
    infile = cmdargs.infile
    outdir = cmdargs.outdir
    skip_header = cmdargs.skip_header
    col_num_ret = cmdargs.col_num_ret
    verbose = cmdargs.verbose

    sepDwelPcl(infile, outdir, skip_header, col_num_ret, verbose)

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
