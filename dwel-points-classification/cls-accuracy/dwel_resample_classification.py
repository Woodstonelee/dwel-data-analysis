#!/usr/bin/env python
"""
Generate a resample of the classification of a DWEL point cloud by permutating
labels of points according to classification accuracy.
"""

import sys
import os
import argparse

import itertools

import numpy as np

# add parent folder to Python path
addpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if addpath not in sys.path:
    sys.path.append(addpath)
import utils.dwel_points_utils as dpu

def getCmdArgs():
    p = argparse.ArgumentParser(description="Generate a resample of classification of a DWEL point cloud.")

    p.add_argument("-i", "--infile", dest="infile", default=None, help="Input ASCII file of DWEL classified point cloud.")
    p.add_argument("-o", "--outfile", dest="outfile", default=None, help="Output ASCII file of resampled classification")
    p.add_argument("--useraccuracy", dest="useraccuracy", nargs='+', type=float, default=None, help="User's accuracy of each class listed in the classcode.")

    p.add_argument("--classcode", dest="classcode", nargs='+', type=int, default=(1, 2), help="Code of classes in the classified point cloud file. Default: 1, 2")

    cmdargs = p.parse_args()
    if (cmdargs.infile is None) or (cmdargs.outfile is None) or (cmdargs.useraccuracy is None):
        p.print_help()
        print("Input and output file names and user's accuracy must be set.")
        sys.exit()
    if len(cmdargs.classcode) != len(cmdargs.useraccuracy):
        p.print_help()
        print("classcode and useraccuracy must have the same number of elements, one-to-one correspondent.")
        sys.exit()

    return cmdargs

def resample_unknown_class(cmdargs):
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    classcode = cmdargs.classcode
    useraccuracy = cmdargs.useraccuracy

    # # get meta data for reading ascii point cloud file
    # with open(infile, 'r') as infobj:
    #     for i, line in enumerate(infobj):
    #         if i==2:
    #             headerstr_list = line.strip('\r\n ').split(',')
    #             cind = { hstr.strip():i for i, hstr in enumerate(headerstr_list) }
    #             break

    class_label = dpu.loadPoints(infile, usecols=['class']).squeeze()
    class_label = class_label.astype(np.int)
    classcode = np.array(classcode).astype(np.int)

def resample_known_class(cmdargs):
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    classcode = cmdargs.classcode
    useraccuracy = cmdargs.useraccuracy

    # # get meta data for reading ascii point cloud file
    # with open(infile, 'r') as infobj:
    #     for i, line in enumerate(infobj):
    #         if i==2:
    #             headerstr_list = line.strip('\r\n ').split(',')
    #             cind = { hstr.strip():i for i, hstr in enumerate(headerstr_list) }
    #             break

    class_label = dpu.loadPoints(infile, usecols=['class']).squeeze()
    class_label = class_label.astype(np.int)
    classcode = np.array(classcode).astype(np.int)
    class_ind_list = [ np.where(class_label==c)[0] for c in classcode ]
    class_npts = np.array([ len(ci) for ci in class_ind_list ])
    relabel_npts = np.array([ np.fix(npts*(1-ua)) for npts, ua in itertools.izip(class_npts, useraccuracy) ]).astype(np.int)
    relabel_ind = np.hstack([ ci[np.random.choice(npts, size=rnpts, replace=False)] for ci, npts, rnpts in itertools.izip(class_ind_list, class_npts, relabel_npts) ])
    for i, cls in enumerate(classcode[:-1]):
        select_relabel_ind = relabel_ind[np.random.choice(np.sum(relabel_npts[i:]).astype(np.int), size=relabel_npts[i], replace=False)]
        class_label[select_relabel_ind] = cls
        relabel_ind = relabel_ind[np.in1d(relabel_ind, select_relabel_ind, invert=True)]
    class_label[relabel_ind] = classcode[-1]
    
    with open(infile, 'r') as infobj, open(outfile, 'w') as outfobj:
        sys.stdout.write("Write resampled classification\n")

        for i in range(dpu._dwel_points_ascii_scheme["skip_header"]):
            line = infobj.readline()
            outfobj.write(line)

        line = infobj.readline()
        linestr_list = line.strip().lstrip(dpu._dwel_points_ascii_scheme["comments"]).split(dpu._dwel_points_ascii_scheme["delimiter"])
        linestr_list = [lstr.strip() for lstr in linestr_list]
        class_colidx = len(linestr_list)
        outlist = [None for i in range(class_colidx)]
        try:
            class_colidx = linestr_list.index("class")
            line = dpu._dwel_points_ascii_scheme["delimiter"].join(linestr_list) + "\n"
        except ValueError:
            line = dpu._dwel_points_ascii_scheme["delimiter"].join(linestr_list) + ",class\n"
            outlist.append(None)
        outfobj.write(dpu._dwel_points_ascii_scheme["comments"]+line)

        lineoffset = 0
        for i, line in enumerate(infobj):
            if line.strip().find(dpu._dwel_points_ascii_scheme["comments"])>-1:
                outfobj.write(line)
                lineoffset = lineoffset + 1
            else:
                linestr_list = line.strip().split(dpu._dwel_points_ascii_scheme["delimiter"])
                outlist[0:len(linestr_list)] = linestr_list
                outlist[class_colidx] = "{0:d}".format(class_label[i-lineoffset])
                newline = dpu._dwel_points_ascii_scheme["delimiter"].join(outlist) + "\n"
                outfobj.write(newline)

def main(cmdargs):
    resample_known_class(cmdargs)

if __name__=="__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
