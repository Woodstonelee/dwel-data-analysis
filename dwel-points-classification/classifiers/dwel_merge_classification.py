#!/usr/bin/env python

import os
import sys

import argparse
import itertools

import numpy as np

# add parent folder to Python path
addpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if addpath not in sys.path:
    sys.path.append(addpath)
import utils.dwel_points_utils as dpu

def getSkipLines(ptsfile, skip_header=0, comments="//"):
    with open(ptsfile) as fobj:
        for i in range(skip_header):
            fobj.readline()
        cmtline_cnt = 0
        while fobj.readline().lstrip().find(comments) == 0:
            cmtline_cnt = cmtline_cnt + 1
        return cmtline_cnt + skip_header

def getColumnIdx(ptsfile, name_line, colname, 
                 delimiter=",", comments="//"):
    with open(ptsfile) as fobj:
        for i in range(name_line):
            linestr = fobj.readline().strip()
    col_list = linestr.lstrip(comments).split(delimiter)
    for i, colstr in enumerate(col_list):
        if colstr.lower() == colname.lower():
            return i
    return -1

def extractColumnStr(linestr, colind, delimiter=","):
    col_list = linestr.split(delimiter)
    return col_list[colind], delimiter.join(col_list[0:colind]+col_list[colind+1:])

def unionColumnNames(colnames_list):
    cns_set_list = [set(cns) for cns in colnames_list]
    uset = cns_set_list[0].union(*cns_set_list[1:])
    uset_loc = list()
    for i, cns in enumerate(colnames_list):
        if len(uset) == 0:
            break
        for j, cn in enumerate(cns):
            if cn in uset:
                uset_loc.append((i, j))
                uset.remove(cn)
    return uset_loc

def intersectColumnNames(colnames_list):
    cns_set_list = [set(cns) for cns in colnames_list]
    iset = cns_set_list[0].intersection(*cns_set_list[1:])
    iset_loc = list()
    for i, cns in enumerate(colnames_list):
        if len(iset) == 0:
            break
        for j, cn in enumerate(cns):
            if cn in iset:
                iset_loc.append((i, j))
                iset.remove(cn)
    return iset_loc

def getCmdArgs():
    p = argparse.ArgumentParser(description="Merge multiple point classifications according to specified classes of interests in each classification")

    p.add_argument("-i", "--infiles", dest="infiles", required=True, nargs="+", default=None, help="Classification files to be merges with the first file with the highest priority and the last the lowest priority in the merging procedure.")
    p.add_argument("--names", dest="class_names", required=False, nargs="+", default=None, help="Column names of class labels for the given classification files. Default: 'class' for every input file.")
    p.add_argument("--select_classes", dest="select_classes", required=False, nargs="+", default=None, help="Sets of class labels to be merged, one set per each classification file. Multiple classes in one set from one classification is separated with comma, ','. Default: all classes in each file are included in the output file.")
    p.add_argument("--output_classes", dest="output_classes", required=False, nargs="+", default=None, help="Labels of output classes after the merge, in the order with each one corresponding to the classes given to the option --select_classes. Default: 1 to number of output classes.")
    p.add_argument("--output_source", dest="output_source", required=False, default="union", help="Option to choose columns besides the merged class to output in the merged file, 'union', 'intersect', or the index to the input files on which the output file is based upon except the class column, with the first input file being 1. Default: 'union'.")
    p.add_argument("-o", "--output", dest="output", required=True, default=None, help="Output file of merged classification")

    p.add_argument("-v", "--verbose", dest='verbose', default=False, action='store_true', help='Turn on verbose. Default: false')

    cmdargs = p.parse_args()

    if (cmdargs.select_classes is not None) and (len(cmdargs.infiles)!=len(cmdargs.select_classes)):
        p.print_help()
        print "Number of input files to be merged is not the same with the number of the sets of class labels to be merges."
        sys.exit()

    if cmdargs.output_source != "union" and cmdargs.output_source != "intersect":
        try:
            cmdargs.output_source = int(cmdargs.output_source)
        except ValueError:
            p.print_help()
            print "Invalid option for output_source!"
            sys.exit()
        if cmdargs.output_source < 0 or cmdargs.output_source > len(cmdargs.infiles):
            p.print_help()
            print "Output source chosen to be an input file but the index to the file is out of bound."
            sys.exit()

    return cmdargs

def main(cmdargs):
    clsfiles = cmdargs.infiles
    clsnames = cmdargs.class_names
    clslabels_list = cmdargs.select_classes
    out_clslabels = cmdargs.output_classes
    out_clsfile = cmdargs.output
    if cmdargs.output_source != "union" and cmdargs.output_source != "intersect":
        srcf_idx = cmdargs.output_source - 1
    else:
        srcf_idx = cmdargs.output_source
    verbose = cmdargs.verbose

    if clsnames is None:
        clsnames = ["class" for clsf in clsfiles]

    cls_list = [dpu.loadPoints(clsf, usecols=[clsn]) for clsf, clsn in zip(clsfiles, clsnames)]
    for i, cls in enumerate(cls_list):
        if not isinstance(cls.item(0), basestring):
            cls_list[i] = cls.flatten().astype(int).astype(str)

    npts_list = [len(cls) for cls in cls_list]
    if len(np.unique(npts_list)) > 1:
        raise RuntimeError("Input point classification files have different number of points!")

    if clslabels_list is None:
        clslabels_list = [np.unique(cls) for cls in cls_list]
    else:
        tmp = [[cl.strip() for cl in clsl.split(",") if len(cl.strip())>0] for clsl in clslabels_list]
        clslabels_list = tmp

    if out_clslabels is None:
        nout_clslabels = np.sum([len(clsl) for clsl in clslabels_list])
        out_clslabels = np.array(["{0:d}".format(cls) for cls in np.arange(nout_clslabels)])
    else:
        out_clslabels = np.array(out_clslabels)
        nout_clslabels = len(out_clslabels)

    npts = len(cls_list[0])
    nfiles = len(clsfiles)
    out_cls = np.empty(npts, dtype=out_clslabels.dtype)
    # reverse the order of cls_list and clslabels_list for the
    # following assignment procedure.
    out_icls = nout_clslabels - 1
    for i, (cls, slt_cls) in enumerate(itertools.izip(reversed(cls_list), reversed(clslabels_list))):
        for sc in reversed(slt_cls):
            tmpind = np.where(cls==sc)[0]
            out_cls[tmpind] = out_clslabels[out_icls]
            out_icls = out_icls - 1
    
    # write lines with merged class labels to the output file
    # find the line number of the first data line for each file, i.e. non-comment lines
    skiplines_list = [getSkipLines(clsf, skip_header=dpu._dwel_points_ascii_scheme["skip_header"], 
                                   comments=dpu._dwel_points_ascii_scheme["comments"]) for clsf in clsfiles]
    clsidx_list = [getColumnIdx(clsf, dpu._dwel_points_ascii_scheme["skip_header"]+1, clsn, 
                                comments=dpu._dwel_points_ascii_scheme["comments"], 
                                delimiter=dpu._dwel_points_ascii_scheme["delimiter"]) for clsf, clsn in zip(clsfiles, clsnames)]
    tmpflag = np.array(clsidx_list)==-1
    if np.any(tmpflag):
        tmpind = np.where(tmpflag)[0]
        msgstr = "Class names not found in the following input files: \n{0:s}".format("\n".join(np.array(clsfiles)[tmpind]))
        raise RuntimeError(msgstr)

    prgr_unit_cnt = int(0.1*npts)    
    if srcf_idx == "union" or srcf_idx == "intersect":
        fobj_list = [open(clsf) for clsf in clsfiles]
        linestr_list = [fobj.readline().lstrip(dpu._dwel_points_ascii_scheme["comments"]).strip() for fobj in fobj_list]
        collist_list = [lstr.split(dpu._dwel_points_ascii_scheme["delimiter"]) for lstr in linestr_list]
        collist_list = [cl[0:ci]+cl[ci+1:] for cl, ci in itertools.izip(collist_list, clsidx_list)]
        if srcf_idx == "union":
            outcol_loc = unionColumnNames(collist_list)
        else:
            outcol_loc = intersectColumnNames(collist_list)
        out_header_str = "{0:s} ".format(dpu._dwel_points_ascii_scheme["comments"]) \
                         + dpu._dwel_points_ascii_scheme["delimiter"].join([collist_list[ocl[0]][ocl[1]] for ocl in outcol_loc]) \
                         + ",class\n"
        for fobj, sl in itertools.izip(fobj_list, skiplines_list):
            for i in range(sl-1):
                fobj.readline()
        # a local function to process each line from all the input files
        def genOutLineStr(linestr_list):
            collist_list = [lstr.split(dpu._dwel_points_ascii_scheme["delimiter"]) for lstr in linestr_list]
            collist_list = [cl[0:ci]+cl[ci+1:] for cl, ci in itertools.izip(collist_list, clsidx_list)]
            linestr = dpu._dwel_points_ascii_scheme["delimiter"].join([collist_list[ocl[0]][ocl[1]] for ocl in outcol_loc])
            return linestr
        with open(out_clsfile, "w") as outfobj:
            outfobj.write(out_header_str)
            if verbose:
                sys.stdout.write("writting progress: ")
                sys.stdout.flush()
            for i in range(npts):
                linestr_list = [fobj.readline().strip() for fobj in fobj_list]
                linestr = "{0:s},{1:s}\n".format(genOutLineStr(linestr_list), out_cls[i])
                outfobj.write(linestr)
                if verbose and (i % prgr_unit_cnt == 0):
                    sys.stdout.write("{0:d}...".format(int(i*100/npts)))
                    sys.stdout.flush()
            sys.stdout.write("100\n")
            sys.stdout.flush()                
        _ = [fobj.close() for fobj in fobj_list]
    else:
        with open(out_clsfile, "w") as outfobj, open(clsfiles[srcf_idx]) as fobj:
            name_linestr = fobj.readline().strip()
            tmp = extractColumnStr(name_linestr, clsidx_list[srcf_idx], delimiter=dpu._dwel_points_ascii_scheme["delimiter"])
            out_header_str = "{0:s},class\n".format(tmp[1])
            outfobj.write(out_header_str)
            for i in range(skiplines_list[srcf_idx]-1):
                fobj.readline()
            if verbose:
                sys.stdout.write("writing progress: ")
                sys.stdout.flush()
            for i, linestr in enumerate(fobj):
                outfobj.write("{0:s},{1:s}\n".format(extractColumnStr(linestr.strip(), clsidx_list[srcf_idx], 
                                                                      delimiter=dpu._dwel_points_ascii_scheme["delimiter"])[1], 
                                                     out_cls[i]))
                if verbose and (i % prgr_unit_cnt == 0):
                    sys.stdout.write("{0:d}...".format(int(i*100/npts)))
                    sys.stdout.flush()
            sys.stdout.write("100\n")
            sys.stdout.flush()

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
