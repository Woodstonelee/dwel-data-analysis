"""Add no-hit points in the original DWEL point cloud before
classification back to the classified point cloud which has been
generated from a point cloud without no-hit points.

Zhan Li, zhanli86@bu.edu
Created: Tue Oct 25 22:14:25 EDT 2016
"""

import sys
import argparse
import itertools

import numpy as np

import dwel_points_utils as dpu

def stackPtsFiles(infiles, outfile, \
                  srcf_idx="union", fill_str="-9999", \
                  nrows=3142, ncols=1022, \
                  verbose=False):
    skip_header = dpu._dwel_points_ascii_scheme["skip_header"]
    comments = dpu._dwel_points_ascii_scheme["comments"]
    delimiter = dpu._dwel_points_ascii_scheme["delimiter"]

    inpts_list = [dpu.loadPoints(fname, usecols=["range", "sample", "line", "return_number", "number_of_returns", "shot_number"]) for fname in infiles]
    fidx = np.vstack([np.zeros((len(pts), 1))+i for i, pts in enumerate(inpts_list)]).astype(int)
    lidx = np.vstack([np.reshape(np.arange(len(pts)), (len(pts), 1)) for i, pts in enumerate(inpts_list)]).astype(int)

    print "Sorting points according to shot locations and ranges ..."
    sortind, num_of_returns, return_num, shot_num = sortPoints(np.vstack([pts[:, 0:3] for pts in inpts_list]), nrows=nrows, ncols=ncols)
    # Data sanity check
    tmp = np.vstack([pts[:, 3:6] for pts in inpts_list])
    if (np.abs(np.sum(tmp[sortind, 0]-return_num)) > 1e-10) \
       or (np.abs(np.sum(tmp[sortind, 1]-num_of_returns)) > 1e-10) \
       or (np.abs(np.sum(tmp[sortind, 2]-shot_num)) > 1e-10):
        msgstr = "Inconsistent indices of return_number, number_of_returns and shot_number\n" \
                 + "after stacking and sorting points from input files given the nrows and ncols.\n" \
                 + "Check possible causes:\n" \
                 + "1. Wrong nrows or ncols.\n" \
                 + "2. Duplicate records of points between input files.\n" \
                 + "3. Input files have wrong indices of return_number, number_of_returns and shot_number."
        raise RuntimeError(msgstr)
    fidx = fidx[sortind, :]
    lidx = lidx[sortind, :]

    skiplines_list = [getSkipLines(fname, skip_header=skip_header, comments=comments) for fname in infiles]

    fobj_list = [open(fname) for fname in infiles]
    linestr_list = [fobj.readline().lstrip(comments).strip() for fobj in fobj_list]
    collist_list = [lstr.split(delimiter) for lstr in linestr_list]
    if srcf_idx == "union":
        outcol_loc, outcolidx_list = unionColumnNames(collist_list)
    elif srcf_idx == "intersect":
        outcol_loc, outcolidx_list = intersectColumnNames(collist_list)    
    else:
        outcol_loc = [[srcf_idx, i] for i in range(len(collist_list[srcf_idx]))]
        outcolidx_list = [[getIndex(cns, ucn) for ucn in collist_list[srcf_idx]] for cns in collist_list]

    out_header_str = "{0:s} ".format(comments) \
                     + delimiter.join([collist_list[ocl[0]][ocl[1]] for ocl in outcol_loc]) \
                     + "\n"
    for fobj, sl in itertools.izip(fobj_list, skiplines_list):
        for i in range(sl-1):
            fobj.readline()
    with open(outfile, "w") as outfobj:
        outfobj.write(out_header_str)
        templinestr_list = [dict() for i in range(len(infiles))]
        templinenum_list = [-1 for i in range(len(infiles))] # maximum line number of lines stored in our temporary memoray
        readlinenum_list = [0 for i in range(len(infiles))] # line number to be read by file object's readline() function
        nout = len(fidx)
        prgr_cnt_unit = int(0.1*nout)
        if verbose:
            sys.stdout.write("writing progress percent: ")
        for k, (fnum, lnum) in enumerate(itertools.izip(fidx.flat, lidx.flat)):
            if lnum == readlinenum_list[fnum]:
                linestr = fobj_list[fnum].readline().strip()
                readlinenum_list[fnum] = readlinenum_list[fnum] + 1
            elif lnum <= templinenum_list[fnum]:
                try:
                    linestr = templinestr_list[fnum][lnum]
                    templinestr_list[fnum].pop(lnum, None)
                except KeyError:
                    msgstr = "Can't get the line {0:d} from the file {1:s} to output from the temporary memory".format(lnum, infiles_list[fnum])
                    raise RuntimeError(msgstr)
            else:                    
                for i in range(readlinenum_list[fnum], lnum):
                    templinestr_list[fnum][i] = fobj_list[fnum].readline().strip()
                linestr = fobj_list[fnum].readline().strip()
                readlinenum_list[fnum] = lnum+1
                templinenum_list[fnum] = lnum-1
            lineitems = linestr.split(delimiter)
            outlinestr = delimiter.join([lineitems[i] if i>-1 else fill_str for i in outcolidx_list[fnum]]) + "\n"
            outfobj.write(outlinestr)
            if verbose and (k % prgr_cnt_unit == 0):
                sys.stdout.write("{0:d}...".format(int(k*100/nout)))
        if verbose:
            sys.stdout.write("100\n")                
    _ = [fobj.close() for fobj in fobj_list]


def sortPoints(points, nrows=3142, ncols=1022):
    """
    Count the number of returns and update return number of each point
    according to the shot location (line, column) and range.

    Args:

        points (2D numpy array, float): [npts, 3], range, sample, line

    Returns:

        sortind (1D numpy array, int): indices that will sort the shot indices.

        num_of_returns (1D numpy array, int)

        return_num (1D numpy array, int)

        shotind (1D numpy array, int)
    """
    shotind = (points[:, 1:2]-1)*nrows + points[:, 2:3]
    tmppts = np.hstack((shotind, points[:, 0:1]))
    ptsview = tmppts.view(dtype=np.dtype([('shotind', tmppts.dtype), ('range', tmppts.dtype)]))
    sortind = np.argsort(ptsview, order=('shotind', 'range'), axis=0).squeeze()
    ptsview = ptsview[sortind]

    ushotind, uinvind, ucount = np.unique(shotind.squeeze(), return_inverse=True, return_counts=True)
    num_of_returns = ucount[uinvind][sortind]
    return_num = np.zeros(len(ptsview), dtype=int)
    i = 0
    while i<len(ptsview):
        tmpcount = num_of_returns[i]
        return_num[i:i+tmpcount] = np.arange(tmpcount, dtype=int)+1
        i += tmpcount
    tmpflag = np.less(ptsview['range'], 1e-10).squeeze()
    num_of_returns[tmpflag] = 0
    return_num[tmpflag] = 0

    return sortind, num_of_returns, return_num, shotind.squeeze()[sortind]

def getSkipLines(ptsfile, skip_header=0, comments="//"):
    with open(ptsfile) as fobj:
        for i in range(skip_header):
            fobj.readline()
        cmtline_cnt = 0
        while fobj.readline().lstrip().find(comments) == 0:
            cmtline_cnt = cmtline_cnt + 1
        return cmtline_cnt + skip_header

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
    ucolnames = [colnames_list[usl[0]][usl[1]] for usl in uset_loc]
    uset_idx_list = [[getIndex(cns, ucn) for ucn in ucolnames] for cns in colnames_list]
        
    return uset_loc, uset_idx_list

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
    icolnames = [colnames_list[isl[0]][isl[1]] for isl in iset_loc]
    iset_idx_list = [[getIndex(cns, icn) for icn in icolnames] for cns in colnames_list]

    return iset_loc, iset_idx_list

def getIndex(mylist, myval):
    try:
        return mylist.index(myval)
    except ValueError:
        return -1

def getCmdArgs():
    p = argparse.ArgumentParser(description="Add no-hit points in the original DWEL point cloud back to the return-only point cloud for reprojection of points to images.")

    p.add_argument("-i", "--infiles", dest="infiles", required=True, nargs="+", default=None, help="Input point cloud ASCII files to stack together.")
    p.add_argument('-o', '--outfile',dest='outfile', required=True, default=None, help='Output ASCII point cloud file after adding no-hit points back.')
    p.add_argument("--ncols", dest="ncols", type=int, default=1022, help="Number of columns (samples) in the AT projection where points are generated. [default: 1022]")
    p.add_argument("--nrows", dest="nrows", type=int, default=3142, help="Number of rows (lines) in the AT projection where points are generated. [default: 3142]")
    p.add_argument("--output_source", dest="output_source", required=False, default="union", help="Option to choose columns to output in the stacked file, 'union', 'intersect', or the index to the input files on which the output file is based upon, with the first input file being 1. Default: 'union'.")
    p.add_argument("--fill_str", dest="fill_str", required=False, default="-9999", help="A string to fill missing columns in the stacked output file for lines from any input file. Default: -9999")

    p.add_argument("-v", "--verbose", dest='verbose', default=False, action='store_true', help='Turn on verbose. Default: false')

    cmdargs = p.parse_args()

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
    infiles = cmdargs.infiles
    outfile = cmdargs.outfile
    ncols = cmdargs.ncols
    nrows = cmdargs.nrows
    if cmdargs.output_source != "union" and cmdargs.output_source != "intersect":
        srcf_idx = cmdargs.output_source - 1
    else:
        srcf_idx = cmdargs.output_source
    fill_str = cmdargs.fill_str
    verbose = cmdargs.verbose

    stackPtsFiles(infiles, outfile, srcf_idx=srcf_idx, fill_str=fill_str, \
                  nrows=nrows, ncols=ncols, verbose=verbose)

if __name__ == '__main__':
    cmdargs = getCmdArgs()
    main(cmdargs)
