"""
Module to calculate Pgap profile and foliage profile from DWEL data. Currently
take in spd files. Synthesize waveforms from point data and calculate Pgap.

AUTHORS:
    Zhan Li, zhanli86@bu.edu
"""

import sys, os
import time
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
# plt.ion()

#from spdtlstools import spdtlsfile
import nu_spdtlsfile as spdtlsfile
from spddwelerrors import *
from spdtlstools.spdtlserrors import *

class DWELClassProfile:
    """
    Some methods to calculate Pgap and foliage profiles of leaves and woodies
    from single classified DWEL scan. One wavelength is used in the estimation
    here, i.e. mulitple wavelengths can be processed separately using the same
    methods here as long as points are classified.
    """

    def __init__(self, inspdfile, bandlabel, pgapmethod=None, \
                     zenithbinsize=5.0, \
                     minzenith=5.0, maxzenith=70.0, \
                     minazimuth=0.0, maxazimuth=360, \
                     maxht=34.0, htbinsize=0.5, \
                     rgres=0.075, savevar=False, tempprefix=None, \
                     verbose=False):
        
        self.inspdfile = inspdfile
        self.bandlabel = bandlabel.lower()
        self.pgapmethod = pgapmethod
        
        self.zenithbinsize = zenithbinsize
        self.minzenith = minzenith
        self.maxzenith = maxzenith
        self.minazimuth = minazimuth
        self.maxazimuth = maxazimuth
        self.maxht = maxht
        self.htbinsize = htbinsize

        self.rgres = rgres
        self.rglimit = 100.0 # range limit, 100 m
        self.waveformsynrange = np.arange(0.0, 100.0, rgres)
        self.nrgbins = len(np.arange(0.0, 100.0, rgres))

        # If we save intermediate variables to a numpy data file for faster
        # future processing.
        self.savevar = savevar
        self.tempprefix = tempprefix

        self.verbose = verbose

        self.ptsampscale = 1000.0 # scale of point intensity amplitude
        self.leaflabel = 10
        self.woodlabel = 11
        self.PgapZenRgView = None
        self.PgapZenAzView = None

        # Set some default parameter values for member functions.

        # For phase_theta_g, rho_d, min_Ia, max_Ia, each row: a class; each
        # column: a wavelength band. Here, two rows, first row is woodies (class
        # label is 11), second row is leaves (class label is 10); two columns:
        # first column is NIR, second column is SWIR. Class label definition is
        # from SPDCommon.h in spdlib

        # FWHM of pulse model, in unit of meter, a vector, each value is for one
        # wavelength band. Here two values, first value is NIR, second value is
        # SWIR in unit of meter here default is for NSF DWEL iterated pulse
        # model FYI, Oz DWEL iterated pulse model fwhm = np.array([0.65117910,
        # 0.65117910])

        # Currently the Z in DWEL point cloud is corrected for sensor height,
        # that is the Z value has added sensor height. Thus the de-facto sensor
        # height for DWEL point cloud is always zero at present in SPD file.

        # marker name to plot plant profiles.
        self.favdclass = {'leaf_'+bandlabel.lower():'-g', \
                              'wood_'+bandlabel.lower():'-r', \
                              'total_'+bandlabel.lower():'-k', \
                              'plant_'+bandlabel.lower():'--m'}
        # self.rwood = 0
        # self.rleaf = 1
        # self.cnir = 0
        # self.cswir = 1
        # self.__defaultPar__ = { \
        #     'phase_theta_g':np.array([[0.25, 0.25], [0.25, 0.25]]), \
        #         'rho_d':np.array([[0.541, 0.540], [0.413, 0.284]]), \
        #         'min_Ia':np.array([[0.6, 0.6], [0.6, 0.6]]), \
        #         'max_Ia':np.array([[0.95, 0.95], [0.95, 0.95]]), \
        #         'fwhm':np.array([0.54665703, 0.54665703]), \
        #         'sensorheight':0.0}

    def getSolidAnglePlantProfileClass(self, PgapProfileClass, PAI=None):
        """
        Calculate plant profiles with solid angle average by Jupp et al. (2009)
        for all classes of Pgap profiles.

        Args:

            PAI (scalar, float): PAI from hemiphotos or other approaches,
            including both leaves and woodies.
        """
        self.PlantProfileClass = {'height':PgapProfileClass['height'], \
                                      'classname':list(PgapProfileClass['classname'])}
        wood2leaf = self.calcWoodToLeafRatio(PgapProfileClass)
        if PAI is None:
            PAI_dict = {'leaf_'+self.bandlabel:1.0/(wood2leaf+1.0), \
                       'wood_'+self.bandlabel:wood2leaf/(wood2leaf+1.0), \
                       'plant_'+self.bandlabel:1.0}
        else:
            PAI_dict = {'leaf_'+self.bandlabel:PAI*1.0/(wood2leaf+1.0), \
                       'wood_'+self.bandlabel:PAI*wood2leaf/(wood2leaf+1.0), \
                       'plant_'+self.bandlabel:PAI}
        for name in PgapProfileClass['classname']:
            if not (name in PAI_dict.keys()):
                tmpPAI = 1.0
            else:
                tmpPAI = PAI_dict[name]
            self.PlantProfileClass[name] = self.calcSolidAnglePlantProfile(PgapProfileClass[name], \
                                                                           PgapProfileClass['zenith'], \
                                                                           PgapProfileClass['height'], \
                                                                           name, PAI=tmpPAI)

        self.PlantProfileClass['classname'].append('total_'+self.bandlabel)
        self.PlantProfileClass['total_'+self.bandlabel] = np.copy(self.PlantProfileClass['leaf_'+self.bandlabel]).view(np.recarray)
        self.PlantProfileClass['total_'+self.bandlabel].PAI = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAI + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAI
        self.PlantProfileClass['total_'+self.bandlabel].PAVD = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAVD + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAVD

        self.PlantProfileClass['total_'+self.bandlabel].MLA = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAVD*self.PlantProfileClass['leaf_'+self.bandlabel].MLA + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAVD*self.PlantProfileClass['wood_'+self.bandlabel].MLA
        self.PlantProfileClass['total_'+self.bandlabel].MLA = \
            self.PlantProfileClass['total_'+self.bandlabel].MLA/self.PlantProfileClass['total_'+self.bandlabel].PAVD

        self.PlantProfileClass['total_'+self.bandlabel].residual = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAVD*self.PlantProfileClass['leaf_'+self.bandlabel].residual + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAVD*self.PlantProfileClass['wood_'+self.bandlabel].residual
        self.PlantProfileClass['total_'+self.bandlabel].residual = \
            self.PlantProfileClass['total_'+self.bandlabel].residual/self.PlantProfileClass['total_'+self.bandlabel].PAVD

        return self.PlantProfileClass

        
    def calcSolidAnglePlantProfile(self, pgapprofile, zeniths, heights, pgapname, PAI=None):
        """
        Calculate the Jupp et al. (2009) solid angle weighted PAVD

        Args:

            pgapprofile (2D numpy array, float): [n_zenith_bins, n_height_bins]
        """

        rowmidzenithsrad = np.radians(zeniths)
        w = 2 * np.pi * np.sin(rowmidzenithsrad) * np.radians(self.zenithbinsize)
        validzenbins_ind = np.where(pgapprofile[:,-1]<1)[0]
        wn = w / np.sum(w[validzenbins_ind])
        ratio = np.zeros(heights.size)
        for i in range(zeniths.size):
            if (pgapprofile[i,-1] < 1):
                ratio += wn[i] * np.log(pgapprofile[i,:]) / np.log(pgapprofile[i,-1])

        if PAI is None:
            # just output relative foliage profile, i.e. PAI up to canopy top = 1
            PAI = 1.0

        PAI = PAI * ratio
        PAVD = self.deriv(heights, PAI)
        MLA = np.empty(heights.size)
        MLA.fill(np.nan)
        residual = np.empty(heights.size)
        residual.fill(np.nan)
        profile = np.vstack((PAI, PAVD, MLA, residual)).T.copy()
        profileview = profile.view(dtype=[('PAI', profile.dtype), ('PAVD', profile.dtype), ('MLA', profile.dtype), ('residual', profile.dtype)]).view(np.recarray)
        return profileview.copy()

    def calcWoodToLeafRatio(self, PgapProfileClass):
        """
        Calculate the ratio between leaves and woodies with contact frequency
        per unit length of leaves and woodies at different zenith angle. The
        contact frequency at different zenith angle is weighted by the solid
        angle.

        Returns:

            wood2leaf_ratio (scalar, float): wood to leaf ratio of the whole
            canopy.
        """
        # leaf contact frequency per unit path length from minimum zenith angle
        # to maximum zenith angle.
        leaf_K = self.calcSolidAngleContact(PgapProfileClass['leaf_'+self.bandlabel], \
                                       PgapProfileClass['zenith'])
        # woody contact frequency per unit path length
        wood_K = self.calcSolidAngleContact(PgapProfileClass['wood_'+self.bandlabel], \
                                       PgapProfileClass['zenith'])

        return wood_K[-1]/leaf_K[-1]
        

    def calcSolidAngleContact(self, pgapprofile, zeniths):
        """
        Calculate contact frequency per unit length at farthest range (out of
        canopy) of a given zenith range by average of Phit from different zenith
        rings weighted by solid angle. With the assumption that G-function of
        leaves and woodies are the same, the contact frequency per unit length
        can be used to estimate the ratio between leaves and woodies.

        Returns:

            K (1D numpy array, float): average contact frequency in the given
            zenith angle range up to different canopy heights.
        """

        rowmidzenithsrad = np.radians(zeniths)
        w = 2 * np.pi * np.sin(rowmidzenithsrad) * np.radians(self.zenithbinsize)
        validzenbins_ind = np.where(pgapprofile[:,-1]<1)[0]
        wn = w / np.sum(w[validzenbins_ind])
        K = np.zeros(pgapprofile.shape[1])
        for i in range(zeniths.size):
            if (pgapprofile[i, -1]<1):
                K += wn[i] * (-1*np.log(pgapprofile[i, :])*np.cos(rowmidzenithsrad[i]))

        return K

    def getWoodToLeafProfile(self, PgapProfileClass):
        """
        Calculate the height profile of wood to leaf ratio at different zenith
        rings to see if there is any consistent relationship between this ratio
        and heights at different zenith angle
        """
        leafpgapprofile = PgapProfileClass['leaf_'+self.bandlabel]
        woodpgapprofile = PgapProfileClass['wood_'+self.bandlabel]
        validzenbins_ind = np.where(np.logical_and(leafpgapprofile[:, -1]<1, woodpgapprofile[:, -1]<1))[0]
        leafpgapprofile = leafpgapprofile[validzenbins_ind, :]
        woodpgapprofile = woodpgapprofile[validzenbins_ind, :]
        zeniths = PgapProfileClass['zenith'][validzenbins_ind]

        W2L = np.log(woodpgapprofile)/np.log(leafpgapprofile)

        return W2L, zeniths, PgapProfileClass['height']

    def plotWoodToLeafProfile(self, W2L, zeniths, heights, outfile=None):
        # plot
        numcolor = 7
        minW2L = 0.0
        maxW2L = np.nanmax(W2L)
        if maxW2L > 10.0:
            maxW2L = 10.0
        if len(zeniths) > numcolor:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
            linelist = ax1.plot(W2L[0:numcolor, :].T, heights)
            labellist = ["{0:.1f} deg".format(zen) for zen in zeniths[0:numcolor]]
            ax1.set_xlabel("wood to leaf ratio")
            ax1.set_ylabel("height, meter")
            ax1.set_xlim([minW2L, maxW2L])
            ax1.legend(linelist, labellist)

            linelist = ax2.plot(W2L[numcolor:, :].T, heights)
            labellist = ["{0:.1f} deg".format(zen) for zen in zeniths[numcolor:]]
            ax2.set_xlabel("wood to leaf ratio")
            ax2.set_ylabel("height, meter")
            ax2.set_xlim([minW2L, maxW2L])
            ax2.legend(linelist, labellist)
        else:
            fig, ax = plt.subplots(figsize=(8, 5))
            linelist = ax.plot(W2L.T, heights)
            labellist = ["{0:.1f} deg".format(zen) for zen in zeniths]
            ax.set_xlabel("wood to leaf ratio")
            ax.set_ylabel("height, meter")
            ax.set_xlim([minW2L, maxW2L])
            ax.legend(linelist, labellist)

        if outfile is None:
            plt.show()
        else:
            plt.savefig(outfile, bbox_inches='tight')


    def getLinearPlantProfileClass(self, PgapProfileClass, plot=False):
        self.PlantProfileClass = {'height':PgapProfileClass['height'], \
                                      'classname':list(PgapProfileClass['classname'])}
        for name in PgapProfileClass['classname']:
            self.PlantProfileClass[name] = self.calcLinearPlantProfile(PgapProfileClass[name], \
                                                                           PgapProfileClass['zenith'], \
                                                                           PgapProfileClass['height'], \
                                                                           name, plot)

        self.PlantProfileClass['classname'].append('total_'+self.bandlabel)
        self.PlantProfileClass['total_'+self.bandlabel] = np.copy(self.PlantProfileClass['leaf_'+self.bandlabel]).view(np.recarray)
        self.PlantProfileClass['total_'+self.bandlabel].PAI = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAI + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAI
        self.PlantProfileClass['total_'+self.bandlabel].PAVD = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAVD + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAVD

        self.PlantProfileClass['total_'+self.bandlabel].MLA = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAVD*self.PlantProfileClass['leaf_'+self.bandlabel].MLA + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAVD*self.PlantProfileClass['wood_'+self.bandlabel].MLA
        self.PlantProfileClass['total_'+self.bandlabel].MLA = \
            self.PlantProfileClass['total_'+self.bandlabel].MLA/self.PlantProfileClass['total_'+self.bandlabel].PAVD

        self.PlantProfileClass['total_'+self.bandlabel].residual = \
            self.PlantProfileClass['leaf_'+self.bandlabel].PAVD*self.PlantProfileClass['leaf_'+self.bandlabel].residual + \
            self.PlantProfileClass['wood_'+self.bandlabel].PAVD*self.PlantProfileClass['wood_'+self.bandlabel].residual
        self.PlantProfileClass['total_'+self.bandlabel].residual = \
            self.PlantProfileClass['total_'+self.bandlabel].residual/self.PlantProfileClass['total_'+self.bandlabel].PAVD

        return self.PlantProfileClass

    def calcLinearPlantProfile(self, pgapprofile, zeniths, heights, pgapname, plot=False):
        """
        Calculate the linear model PAI/PAVD

        Args:

            pgapprofile (2D numpy array, float): [n_zenith_bins, n_height_bins]
        """
        
        kthetal = -np.log(pgapprofile)
        xtheta = 2 * np.tan(np.radians(zeniths)) / np.pi
        PAIv = np.zeros(heights.size)
        PAIh = np.zeros(heights.size)
        residual = np.zeros(heights.size)
        for i,h in enumerate(heights):
            A = np.vstack([xtheta, np.ones(xtheta.size)]).T
            y = kthetal[:,i]
            if y.any():
                solution = np.linalg.lstsq(A, y)
                Lv, Lh = solution[0]
                PAIv[i] = Lv
                PAIh[i] = Lh
                residual[i] = np.sqrt(solution[1][0])
        
        PAI = PAIv + PAIh
        PAVD = self.deriv(heights,PAI)
        MLA = np.zeros_like(PAI)
        tmpind = np.where(PAIv>1e-6)[0]
        MLA[tmpind] = 1./(PAIh[tmpind]/PAIv[tmpind]+1)*np.pi*0.5
        MLA = np.degrees(MLA)
        profile = np.vstack((PAI, PAVD, MLA, residual)).T.copy()
        profileview = profile.view(dtype=[('PAI', profile.dtype), ('PAVD', profile.dtype), ('MLA', profile.dtype), ('residual', profile.dtype)]).view(np.recarray)

        if plot:
            miny = np.min(kthetal)
            maxy = np.max(kthetal)
            linex = np.array([xtheta[0], xtheta[-1]])
            liney = np.vstack((PAIv*xtheta[0]+PAIh, PAIv*xtheta[-1]+PAIh))
            print "Saving {0:d} plots of linear fitting at all heights. Be patient ...".format(len(heights))
            for i, h in enumerate(heights):
                fig,ax = plt.subplots(figsize=(6, 4.5))
                ax.plot(xtheta, kthetal[:, i], 'o')
                plt.hold(True)
                ax.plot(linex, liney[:, i], '-')
                ax.set_ylim([miny, maxy])
                ax.set_title(pgapname.replace('_', '\_'))
                plt.xlabel(r"$X(\theta)$")
                plt.ylabel(r"$-\ln{P_{gap}}$")
                plt.title("height: {0:.3f} m".format(h))
                plt.savefig(self.tempprefix+"_linear_profile_"+pgapname+"_{0:03d}".format(i)+".png")
                plt.close(fig)

        return profileview.copy()

    
    def getPgapProfileClass(self, PgapZenRgView, sensorheight):
        """
        Get Pgap profile for leavies, woodies and total foliage elements along
        canopy height at different zenith angle bins from a 2D view of Pgap on
        Zenith-Range plane.
        """

        self.heights = np.arange(0, self.maxht, self.htbinsize) + self.htbinsize
        self.midzeniths = np.arange(self.minzenith, self.maxzenith, self.zenithbinsize) + self.zenithbinsize*0.5

        self.PgapProfileClass = {'height':self.heights, 'zenith':self.midzeniths}
        for name in PgapZenRgView['classname']:
            self.PgapProfileClass[name] = np.ones((self.heights.size, self.midzeniths.size))
        self.PgapProfileClass['classname'] = list(PgapZenRgView['classname'])
        
        zeniths = PgapZenRgView['zenith']
        validzenind = np.where(np.logical_and(zeniths>=self.minzenith, zeniths<=self.maxzenith))[0]
        zeniths = zeniths[validzenind]
        rgs = PgapZenRgView['range']
        validmidzen = dict()
        for name in PgapZenRgView['classname']:
            pgapzenrgview = PgapZenRgView[name][validzenind, :]
            # further check invalid shots in a zenith row. I guess this could
            # happen. Just in case.
            validpgapind = np.where(np.all(pgapzenrgview>=0.0, axis=1))[0]
            self.PgapProfileClass[name], validmidzen[name] = self.getPgapZenHtView(pgapzenrgview[validpgapind,:], zeniths[validpgapind], rgs, sensorheight)

        # double check the validity of zenith ring, if there is any valid shot in a zenith ring
        tmplen = np.array([len(zen) for zen in validmidzen.values()], dtype=int)
        if ((tmplen - tmplen[0]) !=0 ).any():
            raise RuntimeError("DWELClassProfile.getPgapProfileClass: valid zenith rings for different foliage classes are different while being expected the same. Check PgapZenRgView.")
        tmpzen = np.array(validmidzen.values())
        tmpzen = tmpzen - np.tile(validmidzen.values()[0], (len(validmidzen.values()), 1))
        if (tmpzen > 1e-10).any():
            raise RuntimeError("DWELClassProfile.getPgapProfileClass: valid zenith rings for different foliage classes are different while being expected the same. Check PgapZenRgView.")

        self.PgapProfileClass['zenith'] = validmidzen.values()[0]

        if self.savevar:
            np.savez((self.tempprefix+"_"+self.bandlabel.lower()+"_PgapProfileClass.npz"), \
                         PgapProfileClass=self.PgapProfileClass)

        return self.PgapProfileClass
        
    def getPgapZenHtView(self, pgapzenrgview, zeniths, rgs, sensorheight):
        """
        Get Pgap profile along canopy height at different zenith angle bins
        from a 2D view of Pgap on Zenith-Range plane.
        """
        zenmesh, rgmesh = np.meshgrid(zeniths, rgs, indexing='ij')
        htmesh = rgmesh * np.cos(np.radians(zenmesh)) + sensorheight

        splitind = [ np.where(zeniths<=midzen+self.zenithbinsize*0.5)[0][-1] for midzen in self.midzeniths ]
        splitind = splitind[:-1]
        htmeshlist = np.split(htmesh, splitind, axis=0)
        pgapzenrgviewlist = np.split(pgapzenrgview, splitind, axis=0)

        validzenind = np.where(np.array([len(ht)>0 for ht in htmeshlist], dtype=np.bool_))[0]

        htmeshlist = [htmeshlist[ind] for ind in validzenind]
        pgapzenrgviewlist = [pgapzenrgviewlist[ind] for ind in validzenind]
        
        pgapzenhtview = np.ones((len(self.midzeniths[validzenind]), len(self.heights)))
        for i, ht in enumerate(self.heights):
            # minimum height the lidar sees is sensor height
            if ht >= sensorheight:
                pgapzenviewlist = [ np.mean(self.getPgapZenView(ht, p, h)) \
                                        for p, h in zip(pgapzenrgviewlist, htmeshlist) ]
                pgapzenhtview[:, i] = np.array(pgapzenviewlist)

        return pgapzenhtview, self.midzeniths[validzenind]

    def getPgapZenView(self, htbin, pgapzenrgview, heights):
        """
        Get Pgap at a given height (htbin) at different zenith bins from a
        zenith-range 2D view of Pgap. Variable "heights" gives the height of
        each bin in the 2D view.
        """
        if len(pgapzenrgview) != len(heights):
            raise OutsideBoundsError("Numbers of rows in pgapzenrgview and heights do not agree. Outside-bound reference will occur")
        if len(pgapzenrgview) == 0:
            return np.array([])
        if (heights[:, -1] < htbin).any():
            raise OutsideBoundsError("Height, %.3f m, requested for Pgap profile is outside available heights in the scan" % htbin)
        
        pgapzenview = np.ones(pgapzenrgview.shape[0])
        for i in range(len(pgapzenview)):
            tmpind = np.where(heights[i, :]<=htbin)[0]
            if len(tmpind) > 0:
                pgapzenview[i] = pgapzenrgview[i, tmpind[-1]]

        return pgapzenview
    
    def genWaveformPgap2DView(self, fwhm, \
                                  leaf_rho, leaf_Ialim, \
                                  wood_rho, wood_Ialim, \
                                  plant_rho=None, plant_Ialim=None):
        """
        Synthesize waveforms of apparent reflectance from points of apparent
        reflectance. Then calculate Pgap using the method of Jupp et. al. (2009)
        for each waveform. However average Pgap in a zenith ring
        together. Create a view of average Pgap on the plane of Zenith and
        Range. Store the view in a 2D numpy array. In this way to save storage
        space rather than creating a giant 3D cube image in azimuth-zenith-range
        space!!! Assume each scattering event given by each point has a Gaussian
        pulse with a FWHM given by outgoing pulse model. Also assume each
        scattering event has the same pulse FWHM at present.

        Args:

            fwhm (float scalar): FWHM used to synthesize waveforms from
            points. Unit: meters.

            leaf_rho, wood_rho (float scalar): diffuse reflectance (DHRF
            precisely) of leaf and wood.

            leaf_Ialim, wood_Ialim (2-element sequence-like): [Ia_min, Ia_max]
            to scale Ia to Pgap for leaf or wood separately.

        Keywords:

            plant_rho (float scalar): "mean" diffuse reflectance (DHRF
            precisely) of all foliage elements including both leaves and
            woodies. Could be an average reflectance of leaf and wood weighted
            by their areas.

            plant_Ialim (2-element sequence-like): [Ia_min, Ia_max] to scale Ia
            to Pgap of all foliage elements.

        Returns:

            PgapZenAzView (2D numpy array): Pgap at furthest waveform range in
            an AT projection. X dimension: azimuth; Y dimension: zenith

            PgapZenRgView (2D numpy array): Pgap at different zenith angle over
            range, average over all azimuth angles. X dimension: range; Y
            dimension: zenith

            sensorheight (float scalar): sensor height, meters.

        Raise:
        """
        # create a spd file object with ybin size as 1, i.e. one row in SPD file
        # is a row we read out.
        spdobj = spdtlsfile.SPDFile(self.inspdfile, resfactor=1)

        # get sensor height
        if spdobj.f['HEADER']['DEFINED_HEIGHT'][0] == 0:
            self.sensorheight = spdobj.f['HEADER']['SENSOR_HEIGHT'][0]
        else:
            self.sensorheight = None

        self.PgapZenRgView = {'zenith':np.zeros(spdobj.f['HEADER']['NUMBER_BINS_Y'][0])-1, \
                                  'range':self.waveformsynrange}
        self.PgapZenAzView = {'zenith':np.zeros(spdobj.f['HEADER']['NUMBER_BINS_Y'][0])-1, \
                                  'azimuth':np.zeros(spdobj.f['HEADER']['NUMBER_BINS_X'][0])-1}

        labelclass = {'leaf_'+self.bandlabel:self.leaflabel, \
                          'wood_'+self.bandlabel:self.woodlabel}
        rhoclass = {'leaf_'+self.bandlabel:leaf_rho, \
                        'wood_'+self.bandlabel:wood_rho}
        Ialimclass = {'leaf_'+self.bandlabel:leaf_Ialim, \
                          'wood_'+self.bandlabel:wood_Ialim}
        if (plant_rho is not None) and (plant_Ialim is not None):
            labelclass['plant_'+self.bandlabel] = None
            rhoclass['plant_'+self.bandlabel] = plant_rho
            Ialimclass['plant_'+self.bandlabel] = plant_Ialim
        for name in rhoclass.keys():
            self.PgapZenRgView[name] = np.zeros((spdobj.nyblocks, self.nrgbins))-1
            self.PgapZenAzView[name] = np.zeros((spdobj.nyblocks, spdobj.f['HEADER']['NUMBER_BINS_X'][0]))-1
        self.PgapZenRgView['classname'] = list(rhoclass.keys())
        self.PgapZenAzView['classname'] = list(rhoclass.keys())

        pgap2d = np.ones((spdobj.f['HEADER']['NUMBER_BINS_X'][0], len(self.waveformsynrange)))*-1

        ngmodel = self.gaussianNormPulse(fwhm)
        validrow = np.zeros(spdobj.f['HEADER']['NUMBER_BINS_Y'][0], dtype=np.bool_)
        for row in range(spdobj.f['HEADER']['NUMBER_BINS_Y'][0]):

            pulsedata, pointslist = spdobj.readSPDRowsList(row)

            if pulsedata is not None:
                validrow[row] = True
                # an extra check to see if each pulse in a row of SPD file has
                # the same zenith angle.
                meanzen = np.mean(pulsedata['ZENITH'])
                if (pulsedata['ZENITH'] - meanzen > 5e-5).any():
                    print "Warning, row {0:d} has different zenith values, {1:6e}".format(row, np.max(pulsedata['ZENITH'] - meanzen))
                self.PgapZenAzView['zenith'][row] = meanzen
                self.PgapZenRgView['zenith'][row] = meanzen
                cnt = spdobj.f['INDEX']['PLS_PER_BIN'][row,:]
                validind = np.where(cnt > 0)[0]
                self.PgapZenAzView['azimuth'][validind] = pulsedata['AZIMUTH']
                if (cnt[validind]>1).any():
                    splitind = np.cumsum(cnt[validind])[:-1]
                else:
                    splitind = None
                npls = len(validind)
                if npls > 0:
                    for name in rhoclass.keys():
                        pgap2d[:] = -1.0
                        waveform2d = self.genWaveform2DFromPointsList(pointslist, ngmodel, splitind, classlabel=labelclass[name])
                        pgap2d[validind, :] = self.calcWaveformPgap(waveform2d, fwhm, \
                                                                        rhoclass[name], Ialimclass[name])
                        self.PgapZenAzView[name][row, :] = pgap2d[:, -1]
                        pgapavgaz = np.mean(pgap2d[validind, :], axis=0)
                        # pgapavgaz = self.calcWaveformPgapAvgAz(waveform2d, fwhm, rhoclass[name], Ialimclass[name])
                        self.PgapZenRgView[name][row, :] = pgapavgaz
                else:
                    for name in rhoclass.keys():
                        self.PgapZenAzView[name][row, :] = 1.0
                        self.PgapZenRgView[name][row, :] = 1.0

            if self.verbose:
                sys.stdout.write("Calculating Pgap 2D view at zenith angle NO. {0:d} / {1:d}      \r".format(row, spdobj.f['HEADER']['NUMBER_BINS_Y'][0]))
                sys.stdout.flush()

        for name in rhoclass.keys():
            self.PgapZenAzView[name] = self.PgapZenAzView[name][validrow, :]
            self.PgapZenRgView[name] = self.PgapZenRgView[name][validrow, :]

        self.PgapZenAzView['zenith'] = self.PgapZenAzView['zenith'][validrow]
        self.PgapZenRgView['zenith'] = self.PgapZenRgView['zenith'][validrow]

        sys.stdout.write("Calculating Pgap 2D view finished!\n")
        sys.stdout.flush()

        if self.savevar:
            np.savez((self.tempprefix + "_"+self.bandlabel.lower()+"_Pgap2DView.npz"), \
                         PgapZenAzView=self.PgapZenAzView, \
                         PgapZenRgView=self.PgapZenRgView, \
                         sensorheight=self.sensorheight)
        return self.PgapZenAzView, self.PgapZenRgView, self.sensorheight


    def genWaveform2DFromPointsList(self, pointslist, ngmodel, splitind=None, classlabel=None):
        """
        Create a 2D array of waveforms synthesized from points from multiple
        pulses in a row.
        """
        npls = len(pointslist)
        nband = len(self.waveformsynrange)
        Waveform2D = [self.genWaveformFromPoints(ptsdata, ngmodel, classlabel) for ptsdata in pointslist]
        Waveform2D = np.array(Waveform2D)
        if splitind is None:
            return Waveform2D
        else:
            Waveform2DList = np.split(Waveform2D, splitind, axis=0)
            Waveform2D = [np.mean(wf, axis=0) for wf in Waveform2DList]
            return np.array(Waveform2D)
        
    def gaussianNormPulse(self, fwhm):
        """
        Utility function for genWaveformFromPoints. It returns a normalized
        (peak=1) Gaussian model with number of bins determined by 3*sigma given
        FWHM.
        """
        tmpw = 5*fwhm/np.sqrt(2*np.pi)
        tmpx = np.arange(-1*tmpw-self.rgres, tmpw+self.rgres, self.rgres)
        tmpy = np.exp(-1*tmpx**2*np.pi/fwhm**2)
        tmpy[0] = 0
        tmpy[-1] = 0
        # make sure the integral of finite Gaussian pulse model is FWHM
        print "error in Gaussian pulse model = {0:.6f}".format(np.sum(tmpy)*self.rgres - fwhm)
        return {'numbins':len(tmpx), 'x':tmpx, 'y':tmpy, 'peakbin':np.argmax(tmpy)}

    def gaussianPulse(self, amp, rg, ngmodel):
        """
        Utility function for genWaveformFromPoints. It returns a waveform of
        Gaussian given its amplitude, peak location and FWHM. Also zeromask is
        to put waveform bins far away from Gaussian peak to zero rather than
        having a infinite Gaussian pulse coverage.
        """
        return amp*np.interp(self.waveformsynrange, ngmodel['x']+rg, ngmodel['y'])


    def genWaveformFromPoints(self, pointdata, ngmodel, classlabel=None):
        """
        Generate/synthesize a waveform using return points from ONE
        pulse. Gaussian function with given FWHM is used to generate
        waveform. Only use points of given class to generate the
        waveform. classlabel is defined by SPDCommon.h in spdlib. Defaut 0 is to
        use all points without considering point class.
        """
        if classlabel is not None:
            keep = pointdata['CLASSIFICATION'] == classlabel
            nu_pointdata = pointdata[keep]
        else:
            nu_pointdata = pointdata
        
        if (nu_pointdata is None) or (len(nu_pointdata) == 0):
            return np.zeros_like(self.waveformsynrange)

        wflist = [ self.gaussianPulse(pts['AMPLITUDE_RETURN'], pts['RANGE'], ngmodel) for pts in nu_pointdata]

        return np.sum(np.array(wflist), axis=0)


    def calcWaveformPgap(self, waveform, fwhm, rho_d, Ialim):
        """
        Calculate scaled Pgap from one or multiple waveforms. If multiple
        waveforms, they are stored in a nw-by-nband 2D numpy array, nw is number
        of waveforms, nband is number of bins in a waveform. Pgap has the same
        shape with waveform.
        
        If Ialim is None, use normalization to estimate Pgap rather than scaling.
        """
        Phitapp = np.cumsum(waveform, axis=1)*self.rgres/self.ptsampscale/(fwhm*rho_d)
        if Ialim is None:
            # some waveform has no return thus Phitapp=0. Do not normalize them
            tmpind = np.where(Phitapp[:,-1]>1e-10)[0]
            tmpmin = np.min(Phitapp[tmpind, :], axis=1)
            tmpmin = np.reshape(tmpmin, (tmpmin.size, 1))
            tmpmin = np.tile(tmpmin, waveform.shape[1])
            tmpmax = np.max(Phitapp[tmpind, :], axis=1)
            tmpmax = np.reshape(tmpmax, (tmpmax.size, 1))
            tmpmax = np.tile(tmpmax, waveform.shape[1])
            tmpscale = 1.0 / (tmpmax-tmpmin)
            Phitapp[tmpind, :] = Phitapp[tmpind, :] * tmpscale + tmpmin
            Pgap = 1.0 - Phitapp
        else:
            min_Ia = Ialim[0]
            max_Ia = Ialim[1]
            I_a = 1.0 - Phitapp
            Pgap = (I_a - min_Ia) / (max_Ia - min_Ia)
            Pgap[Pgap<0] = 0.0
            Pgap[Pgap>1] = 1.0
        return Pgap
    
    def calcWaveformPgapAvgAz(self, waveform, fwhm, rho_d, Ialim):
        """
        Calculate Pgap over range for each zenith angle from mean Ia averaged
        over azimuth angle. If multiple waveforms in variable "waveform", they
        are stored in a nw-by-nband 2D numpy array, nw is number of waveforms
        usually in azimuth dimension, nband is number of bins in a
        waveform. Pgap, a 1D numpy array of size number_of_waveform_bins

        This function plots Pgap from each waveform and the average Pgap over
        azimuth. It is for debugging and comparing Pgap estimate method.
        """
        min_Ia = Ialim[0]
        max_Ia = Ialim[1]
        
        Phitapp = np.cumsum(waveform, axis=1)*self.rgres/self.ptsampscale/(fwhm*rho_d)
        normPhitapp = Phitapp.copy()
        # scale Phit_app to 0 - 1
        # some waveform has no return thus Phitapp=0. Do not normalize them
        tmpind = np.where(normPhitapp[:,-1]>1e-10)[0]
        tmpmin = np.min(normPhitapp[tmpind, :], axis=1)
        tmpmin = np.reshape(tmpmin, (tmpmin.size, 1))
        tmpmin = np.tile(tmpmin, waveform.shape[1])
        tmpmax = np.max(normPhitapp[tmpind, :], axis=1)
        tmpmax = np.reshape(tmpmax, (tmpmax.size, 1))
        tmpmax = np.tile(tmpmax, waveform.shape[1])
        tmpscale = 1.0 / (tmpmax-tmpmin)
        normPhitapp[tmpind, :] = normPhitapp[tmpind, :] * tmpscale + tmpmin 
        # I_a = 1.0 - normPhitapp
        # average over azimuth dimension before scaling
        # I_a = np.mean(I_a, axis=0)
        meannormPhitapp = np.mean(normPhitapp, axis=0)
        # I_a = 1.0 - meannormPhitapp * 0.5 / (np.max(meannormPhitapp) - np.min(meannormPhitapp))
        normI_a = 1.0 - meannormPhitapp

        I_a = 1.0 - np.mean(Phitapp, axis=0)
        # scale
        Pgap = (I_a - min_Ia) / (max_Ia - min_Ia)
        Pgap[Pgap<0] = 0.0
        Pgap[Pgap>1] = 1.0

        # import pdb; pdb.set_trace()
        # compare with old Pgap by scaling before average over azimuth
        old_I_a = 1.0 - np.cumsum(waveform, axis=1)*self.rgres/self.ptsampscale/(fwhm*rho_d)        
        old_Pgap = (old_I_a - min_Ia) / (max_Ia - min_Ia)
        old_Pgap[old_Pgap<0] = 0.0
        old_Pgap[old_Pgap>1] = 1.0

        plt.figure()
        plt.plot(self.waveformsynrange, old_I_a.T)
        plt.title("$I_a$ from individual waveform")
        plt.plot(self.waveformsynrange, np.ones_like(self.waveformsynrange)*min_Ia, '--k')
        plt.xlabel('range')
        plt.ylabel('$P_{gap}$')
        plt.figure()
        plt.plot(self.waveformsynrange, old_Pgap.T)
        plt.title("$P_{gap}$ by scaling from individual waveform")
        plt.xlabel('range')
        plt.ylabel('$P_{gap}$')
        
        old_Pgap = np.mean(old_Pgap, axis=0)
        plt.figure()
        plt.plot(self.waveformsynrange, I_a, label=r"$\overline{I_a}$")
        plt.plot(self.waveformsynrange, Pgap, label=r"$scale(\overline{I_a})$")
        plt.plot(self.waveformsynrange, old_Pgap, label=r"$\overline{scale(I_a)}$")
        plt.plot(self.waveformsynrange, normI_a, label="$\overline{norm(I_a)}$")
        plt.title("Average of waveforms in a zenith ring")
        plt.xlabel('range')
        plt.ylabel('$P_{gap}$')
        plt.legend()

        plt.show()
        plt.close('all')

        return Pgap

    def plotPgapProfile(self, pgapprofile, zeniths, heights, pgapname, outfile=None):
        numcolor = 7
        if zeniths.size > numcolor:
            plt.figure(figsize=(8, 10))

            plt.subplot2grid((2, 5), (0, 0), colspan=4)
            linelist = plt.plot(heights, np.transpose(pgapprofile[0:numcolor]))
            labellist = [ "{0:d} - {1:d} deg".format(np.round(zen-self.zenithbinsize*0.5).astype(int), np.round(zen+self.zenithbinsize*0.5).astype(int)) for zen in zeniths[0:numcolor] ]
            plt.legend(linelist, labellist, bbox_to_anchor=(1.02, 1), loc=2)
            plt.title(pgapname.replace('_', '\_'))
            plt.xlabel('height (m)')
            plt.ylabel('Pgap')
            plt.ylim((0.0, 1.0))

            plt.subplot2grid((2, 5), (1, 0), colspan=4)
            linelist = plt.plot(heights, np.transpose(pgapprofile[numcolor:]))
            labellist = [ "{0:d} - {1:d} deg".format(np.round(zen-self.zenithbinsize*0.5).astype(int), np.round(zen+self.zenithbinsize*0.5).astype(int)) for zen in zeniths[numcolor:] ]
            plt.legend(linelist, labellist, bbox_to_anchor=(1.02, 1), loc=2)
            plt.xlabel('height (m)')
            plt.ylabel('Pgap')
            plt.ylim((0.0, 1.0))
        else:
            plt.figure(figsize=(8, 5))
            plt.subplot2grid((1, 5), (0, 0), colspan=4)
            linelist = plt.plot(heights, np.transpose(pgapprofile))
            labellist = [ "{0:d} - {1:d} deg".format(np.round(zen-self.zenithbinsize*0.5).astype(int), np.round(zen+self.zenithbinsize*0.5).astype(int)) for zen in zeniths ]
            plt.legend(linelist, labellist, bbox_to_anchor=(1.02, 1), loc=2)
            plt.title(pgapname.replace('_', '\_'))
            plt.xlabel('height (m)')
            plt.ylabel('Pgap')
            plt.ylim((0.0, 1.0))

        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()

        plt.close()
        

    def plotPgapZenAzView(self, pgapzenazview, zeniths, azimuths, pgapname, outfile=None):
        fig, ax = plt.subplots(figsize=(8, 5))
        zenmaskind = np.where(zeniths<0.0)[0]
        azmaskind = np.where(azimuths<0.0)[0]
        pgap = pgapzenazview
        pgapmask = pgap<0.0
        pgapmask[np.ix_(zenmaskind, azmaskind)] = True
        masked_pgap = np.ma.array(pgap, mask=pgapmask)

        cmap = plt.get_cmap('gray')
        cmap.set_bad('b', 1.0)

        # cbar = plt.colorbar(implot, orientation='horizontal')
        # cbar.ax.set_ylabel('Pgap')
        if outfile is not None:
            dpi = 72
            mpl.image.imsave(outfile, masked_pgap, dpi=dpi, \
                                 vmin=np.percentile(masked_pgap[~np.isnan(masked_pgap)], 2), \
                                 vmax=np.percentile(masked_pgap[~np.isnan(masked_pgap)], 98), \
                                 cmap=cmap)
        else:
            implot = ax.imshow(masked_pgap, cmap=cmap, \
                                   extent=(np.min(azimuths), np.max(azimuths), np.max(zeniths), np.min(zeniths)))
            ax.set_aspect('equal')
            plt.xlabel('azimuth, deg')
            plt.ylabel('zenith, deg')
            ax.set_title(pgapname.replace('_', '\_'))
            plt.show()
            plt.close()

    def plotPgapZenRgView(self, pgapzenrgview, zeniths, ranges, pgapname, outfile=None, maxrg=100.0):
        # fig, ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(8, 5))
        # ax.set_theta_direction(-1)
        # ax.set_theta_offset(np.radians(90.0))
        # validzenind = np.where(zeniths>=0.0)[0]
        # validrgind = np.where(ranges<maxrg)[0]
        # zenmesh, rgmesh = np.meshgrid(np.radians(zeniths[validzenind]), ranges[validrgind], indexing='ij')
        # pgap = pgapzenrgview[np.ix_(validzenind,validrgind)]
        # masked_pgap = np.ma.array(pgap, mask=pgap<0.0)
        # cmap = plt.get_cmap('winter')
        # cmap.set_bad('r', 1.0)
        # pcm = ax.pcolormesh(zenmesh, rgmesh, masked_pgap, cmap=cmap)
        # ax.set_xlim(np.radians(0.0), np.radians(90.0))
        # cbar = plt.colorbar(pcm)
        # cbar.ax.set_ylabel('Pgap')
        fig, ax = plt.subplots(figsize=(8, 5))
        validzenind = np.where(zeniths>=0.0)[0]
        validrgind = np.where(ranges<maxrg)[0]
        pgap = pgapzenrgview[np.ix_(validzenind,validrgind)]
        masked_pgap = np.ma.array(pgap, mask=pgap<0.0)
        cmap = plt.get_cmap('winter')
        cmap.set_bad('r', 1.0)
        implot = ax.imshow(masked_pgap, cmap=cmap, extent=[np.min(ranges[validrgind]), np.max(ranges[validrgind]), np.max(zeniths[validzenind]), np.min(zeniths[validzenind])])
        plt.xlabel('range, meter')
        plt.ylabel('zenith, deg')
        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()
        plt.close()

    def plotPlantProfileClass(self, plantprofileclass, outfile=None):
        fig = plt.figure(figsize=(8, 5))
        ax1 = plt.subplot2grid((6, 2), (0, 0), rowspan=5)
        ax2 = plt.subplot2grid((6, 2), (0, 1), rowspan=5, sharey=ax1)
        ax3 = plt.subplot2grid((6, 2), (5, 0), colspan=2)
        ax1.hold(True)
        ax2.hold(True)
        lineplots = [None]*len(plantprofileclass['classname'])
        for i, name in enumerate(plantprofileclass['classname']):
            lineplots[i] = ax1.plot(plantprofileclass[name].PAI, plantprofileclass['height'], self.favdclass[name], label=name.replace('_', '\_'))[0]
            ax2.plot(plantprofileclass[name].PAVD, plantprofileclass['height'], self.favdclass[name], label=name.replace('_', '\_'))

        ax1.set_xlim((0.0, ax1.get_xlim()[1]))
        ax2.set_xlim((0.0, ax2.get_xlim()[1]))
        ax1.set_title("PAI")
        ax2.set_title("PAVD")
        ax1.set_xlabel("PAI")
        ax1.set_ylabel("height (m)")
        ax2.set_xlabel("PAVD")
        ax2.set_ylabel("height (m)")

        plt.sca(ax3)
        plt.axis('off')
        legendstr = [ name.replace('_', '\_') for name in plantprofileclass['classname'] ]
        ax3.legend(lineplots, legendstr, bbox_to_anchor=(0., 0., 1, 0.1), loc='lower left', \
                       ncol=5, mode="expand", borderaxespad=0.)
        fig.tight_layout()

        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()
        plt.close()


    def writePlantProfileClass(self, PlantProfileClass, outfile):
        nrows = len(PlantProfileClass['height'])
        ncols = len(PlantProfileClass['classname'])*3
        outmat = np.zeros((nrows, ncols))
        headerstr = "heights,"
        for i, name in enumerate(PlantProfileClass['classname']):
            outmat[:, i*3] = PlantProfileClass[name].PAI.squeeze()
            outmat[:, i*3+1] = PlantProfileClass[name].PAVD.squeeze()
            outmat[:, i*3+2] = PlantProfileClass[name].MLA.squeeze()
            headerstr = headerstr + "{0:s}_PAI,{0:s}_PAVD,{0:s}_MLA,".format(name)
        outmat = np.hstack((PlantProfileClass['height'].reshape(nrows, 1), outmat))
        headerstr = headerstr.rstrip(',')
        np.savetxt(outfile, outmat, fmt='%.3f', delimiter=',', header=headerstr, comments='')
        
        
    @staticmethod
    def deriv(x,y):
        """
        IDL's numerical differentiation using 3-point, Lagrangian interpolation
        df/dx = y0*(2x-x1-x2)/(x01*x02)+y1*(2x-x0-x2)/(x10*x12)+y2*(2x-x0-x1)/(x20*x21)
        where: x01 = x0-x1, x02 = x0-x2, x12 = x1-x2, etc.
        """
        
        x12 = x - np.roll(x,-1) #x1 - x2
        x01 = np.roll(x,1) - x #x0 - x1
        x02 = np.roll(x,1) - np.roll(x,-1) #x0 - x2

        d = np.roll(y,1) * (x12 / (x01*x02)) + y * (1.0/x12 - 1.0/x01) - np.roll(y,-1) * (x01 / (x02 * x12)) # Middle points
        d[0] = y[0] * (x01[1]+x02[1])/(x01[1]*x02[1]) - y[1] * x02[1]/(x01[1]*x12[1]) + y[2] * x01[1]/(x02[1]*x12[1]) # First point
        d[y.size-1] = -y[y.size-3] * x12[y.size-2]/(x01[y.size-2]*x02[y.size-2]) + \
        y[y.size-2] * x02[y.size-2]/(x01[y.size-2]*x12[y.size-2]) - y[y.size-1] * \
        (x02[y.size-2]+x12[y.size-2]) / (x02[y.size-2]*x12[y.size-2]) # Last point

        return d
