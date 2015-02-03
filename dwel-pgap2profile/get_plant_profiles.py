
import optparse
import sys
import os
import numpy as np
import csv

def get_plant_profiles(rowmidzeniths,heights,pgapz):

    # Initialise output dictionary
    profiles = dict()
    profiles["heights"] = heights
    
    # Hinge point PAI    
    # hingeindex = np.argmin(np.abs(rowmidzeniths - np.arctan(np.pi / 2)))
    # profiles["hingePAI"] = -1.1 * np.log(pgapz[hingeindex,:])

    #import pdb; pdb.set_trace();
    
    # Linear model PAI
    kthetal = -np.log(pgapz) #* np.cos(rowmidzeniths)
    xtheta = 2 * np.tan(rowmidzeniths) / np.pi
    PAIv = np.zeros(len(heights))
    PAIh = np.zeros(len(heights))
    for i,h in enumerate(heights):    
        A = np.vstack([xtheta, np.ones(xtheta.size)]).T
        y = kthetal[:,i]
        if y.any():
            Lv, Lh = np.linalg.lstsq(A, y)[0]        
            PAIv[i] = Lv
            PAIh[i] = Lh
    profiles["ePAI"] = PAIv + PAIh
    profiles["MLA"] = 90 - np.degrees(np.arctan2(PAIv,PAIh))

    # get PAVD
    profiles["ePAVD"] = ( (profiles["ePAI"])[1:len(heights)-1]-(profiles["ePAI"])[0:len(heights)-2] ) / \
                        (heights[1:len(heights)-1]-heights[0:len(heights)-2])

    # print, the total LAI on screen
    print('Total LAI up to the given maximum height: '+str(profiles["ePAI"][len(heights)-1]))
    
    return profiles

# def __main__():
#     midzeniths=[]
#     fzen = open('midzeniths.txt', 'r')
#     for line in fzen:
#         midzeniths.append(float(line))
#     fzen.close()
#     fzen = np.array(fzen)
    
#     heights=[]
#     fheights = open('heights.txt', 'r')
#     for line in fheights:
#         heights.append(float(line))
#     fheights.close()
#     heights = np.array(heights)

#     pgapz_leaf = []
#     with open('pgapz_leaf.txt', 'r') as leaffile:
#         leafreader = csv.reader(leaffile, delimiter=',')
#         for row in leafreader:
#             pgapz_leaf.append([float(x) for x in row])
#     pgapz_leaf = np.array(pgapz_leaf)

#     pgapz_branch = []
#     with open('pgapz_branch.txt', 'r') as branchfile:
#         branchreader = csv.reader(branchfile, delimiter=',')
#         for row in branchreader:
#             pgapz_branch.append([float(x) for x in row])
#     pgapz_branch = np.array(pgapz_branch)
    
#     leaf = get_plant_profiles(midzeniths, heights, pgapz_leaf)
#     with open('leafprofile.txt', 'w') as leafprofile:
#         for i in np.arange(heights.size-2):
#             leafprofile.write( str(heights[i])+','+str(leaf["ePAI"][i])+','+str(leaf["MLA"][i])+','+str(leaf["ePAVD"][i])+'\n' )

#     branch = get_plant_profiles(midzeniths, heights, pgapz_branch)
#     with open('branchprofile.txt', 'w') as branchprofile:
#         for i in np.arange(heights.size-2):
#             branchprofile.write( str(heights[i])+','+str(branch["ePAI"][i])+','+str(branch["MLA"][i])+','+str(branch["ePAVD"][i])+'\n' )

def __main__(cmdargs):
    midzeniths=[]
    fzen = open(os.path.join(cmdargs.datadir, cmdargs.zenfile), 'r')
    for line in fzen:
        midzeniths.append(float(line))
    fzen.close()
    midzeniths = np.array(midzeniths)
    
    heights=[]
    fheights = open(os.path.join(cmdargs.datadir, cmdargs.hfile), 'r')
    for line in fheights:
        heights.append(float(line))
    fheights.close()
    heights = np.array(heights)

    pgapz = []
    with open(os.path.join(cmdargs.datadir, cmdargs.pgapfile), 'r') as pgapfile:
        pgapreader = csv.reader(pgapfile, delimiter=',')
        for row in pgapreader:
            pgapz.append([float(x) for x in row])
    pgapz = np.array(pgapz)

    if cmdargs.lowzen is not None:
        tmpflag = midzeniths>float(cmdargs.lowzen);
        midzeniths = midzeniths[tmpflag]
        pgapz = pgapz[tmpflag, :]

    if cmdargs.upzen is not None:
        tmpflag = midzeniths<float(cmdargs.upzen);
        midzeniths = midzeniths[tmpflag]
        pgapz = pgapz[tmpflag, :]
        
    profiles = get_plant_profiles(midzeniths, heights, pgapz)
    with open(os.path.join(cmdargs.datadir, cmdargs.profile), 'w') as outprofile:
        for i in np.arange(heights.size-2):
            outprofile.write( str(heights[i])+','+str(profiles["ePAI"][i])+','+str(profiles["MLA"][i])+','+str(profiles["ePAVD"][i])+'\n' )

# Command arguments
class CmdArgs:
  def __init__(self):
    p = optparse.OptionParser()
    p.add_option("-d","--datadir", dest="datadir", default=None, help="Input data directory for inputs and outputs")
    p.add_option("-z","--zenith", dest="zenfile", default=None, help="Input zenith data file")
    p.add_option("-H","--height", dest="hfile", default=None, help="Input height data file")
    p.add_option("-g","--pgap", dest="pgapfile", default=None, help="Input pgap data file")
    p.add_option("-f","--profile", dest="profile", default="profile.txt",
                 help="Output profile data file")
    p.add_option("-l","--lowzen", dest="lowzen", default=None, help="Lower boundary of the zenith range used in PAI calculation")
    p.add_option("-u","--upzen", dest="upzen", default=None, help="Upper boundary of the zenith range used in PAI calculation")
    (options, args) = p.parse_args()
    self.__dict__.update(options.__dict__)
    
    if (self.datadir is None) | (self.zenfile is None) | (self.hfile is None) | (self.pgapfile is None):
        p.print_help()
        print "Input filenames must be set."
        sys.exit()

# Run the script
if __name__ == "__main__":
    cmdargs = CmdArgs()
    __main__(cmdargs)
