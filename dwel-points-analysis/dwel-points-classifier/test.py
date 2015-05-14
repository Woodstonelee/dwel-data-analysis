#/usr/bin/env python

import sys
import numpy as np
import collections

def closest_points(ind1, ind2, value1, value2, thresh):
    """
    Find a point pair that has value difference less than thresh, if one point
    has more than one corresponding point, choose the closest one.
    
    value1 and value2 have to be sorted in ascending sequence.
    """

    v1, v2 = np.meshgrid(value1, value2, indexing='ij')
    vdiff = np.fabs(v1-v2)
    vflag = vdiff<=thresh
    c_ind = (vflag).nonzero()
    if c_ind[0].size == 0:
        return ()

    vdiff = vdiff[vflag]
    c_ind1 = c_ind[0]
    c_ind2 = c_ind[1]
    min_ind = np.argmin(vdiff)
    flag = np.logical_and(c_ind1 != c_ind1[min_ind], c_ind2 != c_ind2[min_ind])
    min_ind1 = ind1[c_ind1[min_ind]]
    min_ind2 = ind2[c_ind2[min_ind]]
    min_value1 = value1[c_ind1[min_ind]]
    min_value2 = value2[c_ind2[min_ind]]
    shift_value = min_value1 - min_value2
    if np.count_nonzero(flag) == 0:
        return  [min_ind1], [min_ind2]

    # check the remaining points and align them
    c_ind1 = np.unique(c_ind1[flag])
    c_ind2 = np.unique(c_ind2[flag])

    ind1 = ind1[c_ind1]
    ind2 = ind2[c_ind2]
    value1 = value1[c_ind1]
    value2 = value2[c_ind2] + shift_value
    new_thresh = thresh - np.fabs(shift_value)
    # check each left point's neighboring range, see if we can find a point pair
    # for it
    # check left side of closest point pair
    flag1 = value1 < min_value1
    flag2 = value2 < min_value2
    n1 = np.count_nonzero(flag1)
    n2 = np.count_nonzero(flag2)
    leftind1 = collections.deque([ min_ind1 ])
    leftind2 = collections.deque([ min_ind2 ])
    # if n1 and n2:
    #     i2 = 0
    #     for i1 in range(n1):
    #         if i2 >= n2:
    #             break
    #         x = value1[flag1][i1]
    #         tmpvdiff = np.fabs(value2[flag2][i2:n2] - x)
    #         tmpind = np.argmin(tmpvdiff)
    #         if tmpvdiff[tmpind] < new_thresh:
    #             leftind1.append(ind1[flag1][i1])
    #             leftind2.append(ind2[flag2][i2:n2][tmpind])
    #             i2 += 1
    if n1 and n2:
        i2 = n2 - 1
        i1 = n1 - 1
        while i1 >= 0:
            if i2 < 0:
                break
            tmpvlow = min([value1[flag1][i1]-new_thresh, value2[flag2][i2]-new_thresh])
            tmpvhigh = max([value1[flag1][i1]+new_thresh, value2[flag2][i2]+new_thresh])
            tmpind1 = np.where( \
                np.logical_and(value1[flag1]>=tmpvlow, value1[flag1]<tmpvhigh))[0]
            tmpind2 = np.where( \
                np.logical_and(value2[flag2]>=tmpvlow, value2[flag2]<tmpvhigh))[0]
            tmpci1, tmpci2, tmpdiff = cp(value1[flag1][tmpind1], value2[flag2][tmpind2])
            if tmpdiff<new_thresh:
                leftind1.appendleft(ind1[flag1][tmpind1][tmpci1])
                leftind2.appendleft(ind2[flag2][tmpind2][tmpci2])
                i1 = tmpind1[tmpci1] - 1
                i2 = tmpind2[tmpci2] - 1
            else:
                i1 = i1 - 1
    # check right side of closest point pair
    flag1 = value1 > min_value1
    flag2 = value2 > min_value2
    n1 = np.count_nonzero(flag1)
    n2 = np.count_nonzero(flag2)
    rightind1 = []
    rightind2 = []
    # if n1 and n2:
    #     i2 = 0
    #     for i1 in range(n1):
    #         if i2 >= n2:
    #             break
    #         x = value1[flag1][i1]
    #         tmpvdiff = np.fabs(value2[flag2][i2:n2] - x)
    #         tmpind = np.argmin(tmpvdiff)
    #         if tmpvdiff[tmpind] < new_thresh:
    #             leftind1.append(ind1[flag1][i1])
    #             leftind2.append(ind2[flag2][i2:n2][tmpind])
    #             i2 += 1
    if n1 and n2:
        i2 = 0
        i1 = 0
        while i1 < n1:
            if i2 >= n2:
                break
            tmpvlow = min([value1[flag1][i1]-new_thresh, value2[flag2][i2]-new_thresh])
            tmpvhigh = max([value1[flag1][i1]+new_thresh, value2[flag2][i2]+new_thresh])
            tmpind1 = np.where( \
                np.logical_and(value1[flag1]>=tmpvlow, value1[flag1]<tmpvhigh))[0]
            tmpind2 = np.where( \
                np.logical_and(value2[flag2]>=tmpvlow, value2[flag2]<tmpvhigh))[0]
            tmpci1, tmpci2, tmpdiff = cp(value1[flag1][tmpind1], value2[flag2][tmpind2])
            if tmpdiff<new_thresh:
                rightind1.append(ind1[flag1][tmpind1][tmpci1])
                rightind2.append(ind2[flag2][tmpind2][tmpci2])
                i1 = tmpind1[tmpci1] + 1
                i2 = tmpind2[tmpci2] + 1
            else:
                i1 = i1 + 1

    return list(leftind1)+rightind1, list(leftind2)+rightind2

def cp(value1, value2, thresh):
    """
    Utility function used by closest_points
    """
    v1, v2 = np.meshgrid(value1, value2, indexing='ij')
    vdiff = np.fabs(v1-v2)
    i1, i2 = np.where(vdiff <= thresh)
    if len(i1) <= 0:
        return None, None, None
    vdiff = vdiff[i1, i2]
    return i1, i2, vdiff

def closest_points2(ind1, ind2, value1, value2, thresh):
    """
    A second version of point pairing. Aims to be more accurate, maybe slower.
    
    Find a point pair that has value difference less than thresh, if one point
    has more than one corresponding point, choose the closest one.
    
    value1 and value2 have to be sorted in ascending sequence.
    """

    # Find the closest point pair. Check if their difference in values are
    # smaller than given threshold. If not, stop and return. If yes, this is a
    # point pair we need. Store them and remove them from the original
    # lists. Repeat this procedure until stop and return.
    npair = max(len(value1), len(value2))
    pairind = np.zeros((npair, 2), dtype=int)
    pairvalue = np.zeros((npair, 2), dtype=float)
    paircnt = 0
    while ( (len(value1)>0) and (len(value2)>0) ):
        i1, i2, vdiff = cp(value1, value2, thresh)
        if i1 is None:
            break
        if len(vdiff)>1:
            sortind = np.argsort(vdiff)
            i1 = i1[sortind]
            i2 = i2[sortind]
            vdiff = vdiff[sortind]
        foundflag = False
        for ti1, ti2, tvdiff in zip(i1, i2, vdiff):
            pairind[paircnt, :] = [ind1[ti1], ind2[ti2]]
            pairvalue[paircnt, :] = [value1[ti1], value2[ti2]]
            # sort the two value lists and make sure value1 and value2 in point
            # pairs have the same order. The value1 and value2 in new point pair
            # have to be on the same side of existing point pair, that is value1 and
            # value2 should beeither both larger than existing point pair or both
            # smaller, cannot be one is larger and the other is smaller.
            sortind1 = np.argsort(pairvalue[0:paircnt+1, 0])
            sortind2 = np.argsort(pairvalue[0:paircnt+1, 1])
            if np.sum(sortind1 - sortind2) == 0:
                # only if this point pair qualifies, we record it in the point pair
                # by incrementing point pair counter
                paircnt += 1
                tmpmask = np.ones_like(ind1, dtype=np.bool_)
                tmpmask[ti1] = False
                ind1 = ind1[tmpmask]
                value1 = value1[tmpmask]
                tmpmask = np.ones_like(ind2, dtype=np.bool_)
                tmpmask[ti2] = False
                ind2 = ind2[tmpmask]
                value2 = value2[tmpmask]
                foundflag = True
                break
        if not foundflag:
            break

    if paircnt>0:
        pairind = pairind[0:paircnt, :]
        pairvalue = pairvalue[0:paircnt, :]
        sortind1 = np.argsort(pairvalue[:, 0])
        sortind2 = np.argsort(pairvalue[:, 1])
        # final check
        if np.sum(sortind1 - sortind2) != 0:
            print "Something is wrong with closest point pair searching"
            return ()
        pairind = pairind[sortind1, :]
        return pairind[:, 0], pairind[:, 1]
    else:
        return ()

if __name__ == "__main__":
    ind1 = np.array(range(4, 0, -1))
    ind2 = np.array(range(9, 4, -1))
    value1 = np.array([1.6, 2, 3, 4.11])
    value2 = np.array([1.5, 3.05, 4.05, 4.1, 4.15])
    i1, i2 = closest_points2(ind1, ind2, value1, value2, 0.3)
    import pdb; pdb.set_trace()
    print "test done!"
