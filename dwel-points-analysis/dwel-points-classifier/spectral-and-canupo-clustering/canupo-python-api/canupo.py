#!/usr/bin/env python

# canupo.py: call an external executable "canupo" from the CANUPO
# package to calculate multi-scale features and output .msc file
# (multi-scale components). 

import os
import sys
import argparse

import subprocess32

def main(cmdargs):
    if cmdargs.data_core is None:
        data_core = cmdargs.data
        sys.stdout.write("Using the same points as input data as the data_core.\n")
    else:
        data_core = cmdargs.data_core

    cmdstr = "{0:s} {1:f}:{2:f}:{3:f} : {4:s} {5:s} {6:s} {7:d}".format(cmdargs.canupo, cmdargs.scale_min, cmdargs.scale_inc, cmdargs.scale_max, cmdargs.data, data_core, cmdargs.msc, 1 if cmdargs.add_field else 0)
    print subprocess32.check_call(cmdstr, shell=True)
    return 0

def getCmdArgs():
    p = argparse.ArgumentParser("Call external executable \"canupo\" to generate multi-scale component .msc file.")
    
    p.add_argument("--canupo", dest="canupo", default="../bin/canupo", help="Path to the canupo executable. Default: \"../bin/canupo\"")

    p_scale = p.add_argument_group("Scale parameters", "Scales at which to perform the analysis A scale correspond to a diameter for neighbor research.")
    p_scale.add_argument("--scale_min", dest="scale_min", type=float, default=None, help="Minimum scale value")
    p_scale.add_argument("--scale_max", dest="scale_max", type=float, default=None, help="Maximum scale value")
    p_scale.add_argument("--scale_inc", dest="scale_inc", type=float, default=None, help="Increment of scale values")

    p.add_argument("--data", dest="data", default=None, help="Whole point cloud to process.")
    p.add_argument("--data_core", dest="data_core", default=None, help="Points at which to do the computation. It is not necessary that these points match entries in data.xyz: This means data_core.xyz need not be (but can be) a subsampling of data.xyz, a regular grid is OK. You can also take exactly the same file, or put more core points than data points, the core points need only lie in the same region as data. Tip: use core points at least at max_scale distance from the scene boundaries in order to avoid spurious multi-scale relations. Default: the same as input to \"--data\".")
    p.add_argument("--msc", dest="msc", default=None, help="Output path to the msc file")
    p.add_argument("--add_field", dest="add_field", action="store_true", help="Turn on this option to add an additionnal field into the output msc file for each core point: the angle (0<=a<=90 deg) between the vertical and the normal of the best 2D plane fit at that core point, at the largest given scale. 0 thus means a perfectly horizontal plane, 90 means a perfectly vertical one.")

    cmdargs = p.parse_args()
    if (cmdargs.scale_min is None) or (cmdargs.scale_max is None) or (cmdargs.scale_inc is None):
        p.print_help()
        sys.stdout.write("Input for scale parameters is required. \n")
        sys.exit()
    if cmdargs.data is None:
        p.print_help()
        sys.stdout.write("Input for \"--data\" is required. \n")
        sys.exit()
    if cmdargs.msc is None:
        p.print_help()
        sys.stdout.write("Input for \"--msc\" is required. \n")
        sys.exit()

    return cmdargs

if __name__=="__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
