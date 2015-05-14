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
mpl.use('Agg')
import matplotlib.pyplot as plt

#from spdtlstools import spdtlsfile
import nu_spdtlsfile as spdtlsfile
from spddwelerrors import *
from spdtlstools.spdtlserrors import *

class dwelDualProfile:
    """
    Some methods to calculate separated Pgap and foliage profiles of leaves and
    woodies from classified DWEL data.
    """

    def __init__(self, nirfile, swirfile, zenithbinsize=5.0, \
                     minzenith=5.0, maxzenith=70.0, \
                     minazimuth=0.0, maxazimuth=360, \
                     maxht=34.0, htbinsize=0.5, \
                     rgres=0.075, savevar=False, tempprefix=None):
        self.nirfile = nirfile
        self.swirfile = swirfile
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

        self.pgapclassname = ['plant_nir', 'leaf_nir', 'wood_nir', 'leaf_swir', 'wood_swir']
        self.markerstr = ['-k', '--g', '-g', '--r', '-r']
        self.rwood = 0
        self.rleaf = 1
        self.cnir = 0
        self.cswir = 1
        self.__defaultPar__ = { \
            'phase_theta_g':np.array([[0.25, 0.25], [0.25, 0.25]]), \
                'rho_d':np.array([[0.541, 0.540], [0.413, 0.284]]), \
                'min_Ia':np.array([[0.6, 0.6], [0.6, 0.6]]), \
                'max_Ia':np.array([[0.95, 0.95], [0.95, 0.95]]), \
                'fwhm':np.array([0.54665703, 0.54665703]), \
                'sensorheight':0.0}


    def defaultPar(self, parname=None):
        if parname is None:
            return self.__defaultPar__
        else:
            return self.__defaultPar__[parname]

    def getLinearDualPlantProfile(self, DualPgapProfile, plot=False):
        self.DualPlantProfile = {'height':DualPgapProfile['height']}
        for name in self.pgapclassname:
            self.DualPlantProfile[name] = self.calcLinearPlantProfile(DualPgapProfile, name, plot)

        return self.DualPlantProfile

    def calcLinearPlantProfile(self, dualpgapprofile, pgapname, plot=False):
        """
        Calculate the linear model PAI/PAVD
        """
        
        kthetal = -np.log(dualpgapprofile[pgapname])
        xtheta = 2 * np.tan(np.radians(dualpgapprofile['zenith'])) / np.pi
        PAIv = np.zeros(dualpgapprofile['height'].size)
        PAIh = np.zeros(dualpgapprofile['height'].size)
        residual = np.zeros(dualpgapprofile['height'].size)
        for i,h in enumerate(dualpgapprofile['height']):
            A = np.vstack([xtheta, np.ones(xtheta.size)]).T
            y = kthetal[:,i]
            if y.any():
                solution = np.linalg.lstsq(A, y)
                Lv, Lh = solution[0]
                PAIv[i] = Lv
                PAIh[i] = Lh
                residual[i] = np.sqrt(solution[1][0])
        
        PAI = PAIv + PAIh
        PAVD = self.deriv(dualpgapprofile['height'],PAI)
        MLA = 90 - np.degrees(np.arctan2(PAIv,PAIh))
        profile = np.vstack((PAI, PAVD, MLA, residual)).T.copy()
        profileview = profile.view(dtype=[('PAI', profile.dtype), ('PAVD', profile.dtype), ('MLA', profile.dtype), ('residual', profile.dtype)]).view(np.recarray)

        if plot:
            miny = np.min(kthetal)
            maxy = np.max(kthetal)
            linex = np.array([xtheta[0], xtheta[-1]])
            liney = np.vstack((PAIv*xtheta[0]+PAIh, PAIv*xtheta[-1]+PAIh))
            print "Saving {0:d} plots of linear fitting at all heights. Be patient ...".format(len(dualpgapprofile['height']))
            for i, h in enumerate(dualpgapprofile['height']):
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

    
    def getDualPgapProfile(self, PgapZenRgView, sensorheight):
        """
        Get Pgap profile for leavies, woodies and total plant from both NIR and
        SWIR along canopy height at different zenith angle bins from a 2D view
        of Pgap on Zenith-Range plane.
        """

        self.heights = np.arange(0, self.maxht, self.htbinsize) + self.htbinsize
        self.midzeniths = np.arange(self.minzenith, self.maxzenith, self.zenithbinsize) + self.zenithbinsize*0.5

        self.DualPgapProfile = {'height':self.heights, 'zenith':self.midzeniths}
        for name in self.pgapclassname:
            self.DualPgapProfile[name] = np.ones((self.heights.size, self.midzeniths.size))
        
        zeniths = PgapZenRgView['zenith']
        validzenind = np.where(np.logical_and(zeniths>=self.minzenith, zeniths<=self.maxzenith))[0]
        zeniths = zeniths[validzenind]
        rgs = PgapZenRgView['range']
        for name in self.pgapclassname:
            pgapzenrgview = PgapZenRgView[name][validzenind, :]
            # further check invalid shots in a zenith row. I guess this could
            # happen. Just in case.
            validpgapind = np.where(np.all(pgapzenrgview>=0.0, axis=1))[0]
            self.DualPgapProfile[name] = self.getPgapZenHtView(pgapzenrgview[validpgapind,:], zeniths[validpgapind], rgs, sensorheight)

        if self.savevar:
            np.savez((self.tempprefix + "_DualPgapProfile.npz"), \
                         DualPgapProfile=self.DualPgapProfile)

        return self.DualPgapProfile
        
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

        pgapzenhtview = np.ones((len(self.midzeniths), len(self.heights)))
        for i, ht in enumerate(self.heights):
            # minimum height the lidar sees is sensor height
            if ht >= sensorheight:
                pgapzenviewlist = [ np.mean(self.getPgapZenView(ht, p, h)) \
                                        for p, h in zip(pgapzenrgviewlist, htmeshlist) ]
                pgapzenhtview[:, i] = np.array(pgapzenviewlist)

        return pgapzenhtview

    def getPgapZenView(self, htbin, pgapzenrgview, heights):
        """
        Get Pgap at a given height at different zenith bins
        """
        if len(pgapzenrgview) != len(heights):
            raise OutsideBoundsError("Numbers of rows in pgapzenrgview and heights do not agree. Outside-bound reference will occur")
        if (heights[:, -1] < htbin).any():
            raise OutsideBoundsError("Height, %.3f m, requested for Pgap profile is outside available heights in the scan" % htbin)
        
        pgapzenview = np.ones(pgapzenrgview.shape[0])
        for i in range(len(pgapzenview)):
            tmpind = np.where(heights[i, :]<=htbin)[0]
            if len(tmpind) > 0:
                pgapzenview[i] = pgapzenrgview[i, tmpind[-1]]

        return pgapzenview
    
    def genWaveformPgap2DView(self, fwhm=None, \
                                    rho_d=None, \
                                    min_Ia=None, \
                                    max_Ia=None, \
                                    phase_theta_g=None):
        """
        Synthesize waveforms of apparent reflectance from points of apparent
        reflectance. Then calculate Pgap using the method of Jupp et. al. (2009) for
        each waveform. However average Pgap in a zenith ring together. Create a view
        of average Pgap on the plane of Zenith and Range. Store the view in a 2D
        numpy array. In this way to save storage space rather than creating a giant
        3D cube image in azimuth-zenith-range space!!! Assume each scattering event
        given by each point has a Gaussian pulse with a FWHM given by outgoing pulse
        model. Also assume each scattering event has the same pulse FWHM at present.
        """
        # set default parameters if user has not given one
        if fwhm is None:
            fwhm = self.defaultPar('fwhm')
        if phase_theta_g is None:
            phase_theta_g = self.defaultPar('phase_theta_g')
        if rho_d is None:
            rho_d = self.defaultPar('rho_d')
        if min_Ia is None:
            min_Ia = self.defaultPar('min_Ia')
        if max_Ia is None:
            max_Ia = self.defaultPar('max_Ia')

        nirspdobj = spdtlsfile.SPDFile(self.nirfile, resfactor=1)
        swirspdobj = spdtlsfile.SPDFile(self.swirfile, resfactor=1)

        # get sensor height
        if nirspdobj.f['HEADER']['DEFINED_HEIGHT'][0] == 0:
            self.sensorheight = nirspdobj.f['HEADER']['SENSOR_HEIGHT'][0]
        else:
            self.sensorheight = None
        if swirspdobj.f['HEADER']['DEFINED_HEIGHT'][0] == 0:
            swirsensorheight = swirspdobj.f['HEADER']['SENSOR_HEIGHT'][0]
        else:
            swirsensorheight = None
        if self.sensorheight != swirsensorheight:
            raise BandDisagreeError("Sensor heights from NIR and SWIR do not agree.")

        # # define the start and finish of row according to zenith range.
        # zenbins = np.arange(nirspdobj.f['HEADER']['NUMBER_BINS_Y'][0])*nirspdobj.f['HEADER']['BIN_SIZE'][0]
        # startrow = np.where(zenbins>=max(nirspdobj.f['HEADER']['ZENITH_MIN'][0], self.minzenith))[0][0] # inclusive
        # finishrow = np.where(zenbins>min(nirspdobj.f['HEADER']['ZENITH_MAX'][0], self.maxzenith))[0][0] + 1 # exclusive
        # zenbins[0:startrow] = -1.0
        # zenbins[finishrow:] = -1.0

        self.PgapZenRgView = {'zenith':np.zeros(nirspdobj.f['HEADER']['NUMBER_BINS_Y'][0])-1, \
                                  'range':self.waveformsynrange}
        self.PgapZenAzView = {'zenith':np.zeros(nirspdobj.f['HEADER']['NUMBER_BINS_Y'][0])-1, \
                                  'azimuth':np.zeros(nirspdobj.f['HEADER']['NUMBER_BINS_X'][0])-1}
        for name in self.pgapclassname:
            self.PgapZenRgView[name] = np.zeros((nirspdobj.nyblocks, self.nrgbins))-1
            self.PgapZenAzView[name] = np.zeros((nirspdobj.nyblocks, nirspdobj.f['HEADER']['NUMBER_BINS_X'][0]))-1

        pgap2d = np.ones((nirspdobj.f['HEADER']['NUMBER_BINS_X'][0], len(self.waveformsynrange)))*-1

        nirngmodel = self.gaussianNormPulse(fwhm[self.cnir])
        swirngmodel = self.gaussianNormPulse(fwhm[self.cswir])
        for row in range(nirspdobj.f['HEADER']['NUMBER_BINS_Y'][0]):
            
            pulsedata, pointslist = nirspdobj.readSPDRowsList(row)

            if pulsedata is not None:
                # an extra check
                meanzen = np.mean(pulsedata['ZENITH'])
                if (pulsedata['ZENITH'] - meanzen > 5e-5).any():
                    print "Warning, row {0:d} has different zenith values, {1:6e}".format(row, np.max(pulsedata['ZENITH'] - meanzen))
                self.PgapZenAzView['zenith'][row] = meanzen
                self.PgapZenRgView['zenith'][row] = meanzen
                cnt = nirspdobj.f['INDEX']['PLS_PER_BIN'][row,:]
                validind = np.where(cnt > 0)[0]
                self.PgapZenAzView['azimuth'][validind] = pulsedata['AZIMUTH']
                if (cnt[validind]>1).any():
                    splitind = np.cumsum(cnt[validind])[:-1]
                else:
                    splitind = None
                npls = len(validind)
                if npls > 0:
                    # nir, plant (both leaves and woodies)
                    pgap2d[:] = -1.0
                    waveform2d = self.genWaveform2DFromPointsList(pointslist, nirngmodel, splitind)
                    pgap2d[validind, :] = self.calcWaveformPgap(waveform2d, fwhm[self.cnir], \
                                                                    rho_d=rho_d[self.rleaf, self.cnir], \
                                                                    min_Ia=min_Ia[self.rleaf, self.cnir], \
                                                                    max_Ia=max_Ia[self.rleaf, self.cnir])
                    self.PgapZenAzView['plant_nir'][row, :] = pgap2d[:, -1]
                    self.PgapZenRgView['plant_nir'][row, :] = np.mean(pgap2d[validind, :], axis=0)

                    # nir, leaves
                    pgap2d[:] = -1.0
                    waveform2d = self.genWaveform2DFromPointsList(pointslist, nirngmodel, splitind, classlabel=self.leaflabel)
                    pgap2d[validind, :] = self.calcWaveformPgap(waveform2d, fwhm[self.cnir], \
                                                                    rho_d=rho_d[self.rleaf, self.cnir], \
                                                                    min_Ia=min_Ia[self.rleaf, self.cnir], \
                                                                    max_Ia=max_Ia[self.rleaf, self.cnir])
                    self.PgapZenAzView['leaf_nir'][row, :] = pgap2d[:, -1]
                    self.PgapZenRgView['leaf_nir'][row, :] = np.mean(pgap2d[validind, :], axis=0)

                    # nir, woodies
                    pgap2d[:] = -1.0
                    waveform2d = self.genWaveform2DFromPointsList(pointslist, nirngmodel, splitind, classlabel=self.woodlabel)
                    pgap2d[validind, :] = self.calcWaveformPgap(waveform2d, fwhm[self.cnir], \
                                                                    rho_d=rho_d[self.rwood, self.cnir], \
                                                                    min_Ia=min_Ia[self.rwood, self.cnir], \
                                                                    max_Ia=max_Ia[self.rwood, self.cnir])
                    self.PgapZenAzView['wood_nir'][row, :] = pgap2d[:, -1]
                    self.PgapZenRgView['wood_nir'][row, :] = np.mean(pgap2d[validind, :], axis=0)

            pulsedata, pointslist = swirspdobj.readSPDRowsList(row)
            if pulsedata is not None:
                cnt = swirspdobj.f['INDEX']['PLS_PER_BIN'][row,:]
                validind = np.where(cnt > 0)[0]
                if (cnt[validind]>1).any():
                    splitind = np.cumsum(cnt[validind])[:-1]
                else:
                    splitind = None
                npls = len(validind)
                if npls > 0:
                    # swir, leaves
                    pgap2d[:] = -1.0
                    waveform2d = self.genWaveform2DFromPointsList(pointslist, swirngmodel, splitind, classlabel=self.leaflabel)
                    pgap2d[validind, :] = self.calcWaveformPgap(waveform2d, fwhm[self.cswir], \
                                                                    rho_d=rho_d[self.rleaf, self.cswir], \
                                                                    min_Ia=min_Ia[self.rleaf, self.cswir], \
                                                                    max_Ia=max_Ia[self.rleaf, self.cswir])
                    self.PgapZenAzView['leaf_swir'][row, :] = pgap2d[:, -1]
                    self.PgapZenRgView['leaf_swir'][row, :] = np.mean(pgap2d[validind, :], axis=0)

                    # swir, woodies
                    pgap2d[:] = -1.0
                    waveform2d = self.genWaveform2DFromPointsList(pointslist, swirngmodel, splitind, classlabel=self.woodlabel)
                    pgap2d[validind, :] = self.calcWaveformPgap(waveform2d, fwhm[self.cswir], \
                                                                    rho_d=rho_d[self.rwood, self.cswir], \
                                                                    min_Ia=min_Ia[self.rwood, self.cswir], \
                                                                    max_Ia=max_Ia[self.rwood, self.cswir])
                    self.PgapZenAzView['wood_swir'][row, :] = pgap2d[:, -1]
                    self.PgapZenRgView['wood_swir'][row, :] = np.mean(pgap2d[validind, :], axis=0)

        if self.savevar:
            np.savez((self.tempprefix + "_Pgap2DView.npz"), \
                         PgapZenAzView=self.PgapZenAzView, \
                         PgapZenRgView=self.PgapZenRgView, \
                         sensorheight=self.sensorheight)
        return self.PgapZenAzView, self.PgapZenRgView, self.sensorheight


    def genWaveform2DFromPointsList(self, pointslist, ngmodel, splitind=None, classlabel=0):
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
        
    def gaussianNormPulse(self, fwhm=None):
        """
        Utility function for genWaveformFromPoints. It returns a normalized
        (peak=1) Gaussian model with number of bins determined by 3*sigma given
        FWHM.
        """
        if fwhm is None:
            # default is NIR FWHM
            fwhm = self.defaultPar('fwhm')[0]

        tmpw = 3*fwhm/np.sqrt(2*np.pi)
        tmpx = np.arange(-1*tmpw-self.rgres, tmpw+self.rgres, self.rgres)
        tmpy = np.exp(-1*tmpx**2*np.pi/fwhm**2)
        tmpy[0] = 0
        tmpy[-1] = 0
        return {'numbins':len(tmpx), 'x':tmpx, 'y':tmpy, 'peakbin':np.argmax(tmpy)}

    def gaussianPulse(self, amp, rg, ngmodel):
        """
        Utility function for genWaveformFromPoints. It returns a waveform of
        Gaussian given its amplitude, peak location and FWHM. Also zeromask is
        to put waveform bins far away from Gaussian peak to zero rather than
        having a infinite Gaussian pulse coverage.
        """
        return amp*np.interp(self.waveformsynrange, ngmodel['x']+rg, ngmodel['y'])


    def genWaveformFromPoints(self, pointdata, ngmodel, classlabel=0):
        """
        Generate/synthesize a waveform using return points from ONE
        pulse. Gaussian function with given FWHM is used to generate
        waveform. Only use points of given class to generate the
        waveform. classlabel is defined by SPDCommon.h in spdlib. Defaut 0 is to
        use all points without considering point class.
        """
        if classlabel > 0:
            keep = pointdata['CLASSIFICATION'] == classlabel
            nu_pointdata = pointdata[keep]
        else:
            nu_pointdata = pointdata
        
        if (nu_pointdata is None) or (len(nu_pointdata) == 0):
            return np.zeros_like(self.waveformsynrange)

        wflist = [ self.gaussianPulse(pts['AMPLITUDE_RETURN'], pts['RANGE'], ngmodel) for pts in nu_pointdata]

        return np.sum(np.array(wflist), axis=0)


    def calcWaveformPgap(self, waveform, fwhm, rho_d=None, min_Ia=None, max_Ia=None, phase_theta_g=None):
        """
        Calculate scaled Pgap from one or multiple waveforms. If multiple
        waveforms, they are stored in a nw-by-nband 2D numpy array, nw is number
        of waveforms, nband is number of bins in a waveform. Pgap has the same
        shape with waveform
        """
        # default is for woodies at NIR
        if phase_theta_g is None:
            phase_theta_g = self.defaultPar('phase_theta_g')[0, 0]
        if rho_d is None:
            rho_d = self.defaultPar('rho_d')[0, 0]
        if min_Ia is None:
            min_Ia = self.defaultPar('min_Ia')[0, 0]
        if max_Ia is None:
            max_Ia = self.defaultPar('max_Ia')[0, 0]
        I_a = 1.0 - np.cumsum(waveform, axis=1)/self.ptsampscale/(fwhm*rho_d)
        Pgap = (I_a - min_Ia) / (max_Ia - min_Ia)
        Pgap[Pgap<0] = 0.0
        Pgap[Pgap>1] = 1.0
        return Pgap

    def plotPgapProfile(self, pgapprofile, pgapname, outfile=None):
        numcolor = 7
        if pgapprofile['zenith'].size > numcolor:
            plt.figure(figsize=(8, 10))

            plt.subplot2grid((2, 5), (0, 0), colspan=4)
            linelist = plt.plot(pgapprofile['height'], np.transpose(pgapprofile[pgapname][0:numcolor]))
            labellist = [ "{0:d} - {1:d} deg".format(np.round(zen-self.zenithbinsize*0.5).astype(int), np.round(zen+self.zenithbinsize*0.5).astype(int)) for zen in pgapprofile['zenith'][0:numcolor] ]
            plt.legend(linelist, labellist, bbox_to_anchor=(1.02, 1), loc=2)
            plt.title(pgapname.replace('_', '\_'))
            plt.xlabel('height (m)')
            plt.ylabel('Pgap')
            plt.ylim((0.0, 1.0))

            plt.subplot2grid((2, 5), (1, 0), colspan=4)
            linelist = plt.plot(pgapprofile['height'], np.transpose(pgapprofile[pgapname][numcolor:]))
            labellist = [ "{0:d} - {1:d} deg".format(np.round(zen-self.zenithbinsize*0.5).astype(int), np.round(zen+self.zenithbinsize*0.5).astype(int)) for zen in pgapprofile['zenith'][numcolor:] ]
            plt.legend(linelist, labellist, bbox_to_anchor=(1.02, 1), loc=2)
            plt.xlabel('height (m)')
            plt.ylabel('Pgap')
            plt.ylim((0.0, 1.0))
        else:
            plt.figure(figsize=(8, 5))
            plt.subplot2grid((1, 5), (0, 0), colspan=4)
            linelist = plt.plot(pgapprofile['height'], np.transpose(pgapprofile[pgapname]))
            labellist = [ "{0:d} - {1:d} deg".format(np.round(zen-self.zenithbinsize*0.5).astype(int), np.round(zen+self.zenithbinsize*0.5).astype(int)) for zen in pgapprofile['zenith'] ]
            plt.legend(linelist, labellist, bbox_to_anchor=(1.02, 1), loc=2)
            plt.title(pgapname.replace('_', '\_'))
            plt.xlabel('height (m)')
            plt.ylabel('Pgap')
            plt.ylim((0.0, 1.0))

        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()
        

    def plotPgapZenAzView(self, pgapzenazview, pgapname, outfile=None):
        fig, ax = plt.subplots(figsize=(8, 5))
        zenmaskind = np.where(pgapzenazview['zenith']<0.0)[0]
        azmaskind = np.where(pgapzenazview['azimuth']<0.0)[0]
        pgap = pgapzenazview[pgapname]
        pgapmask = pgap<0.0
        pgapmask[np.ix_(zenmaskind, azmaskind)] = True
        masked_pgap = np.ma.array(pgap, mask=pgapmask)
        cmap = plt.get_cmap('gray')
        cmap.set_bad('b', 1.0)
        implot = ax.imshow(masked_pgap, cmap=cmap)
        ax.set_aspect('equal')
        plt.xlabel('azimuth, deg')
        plt.ylabel('zenith, deg')
        ax.set_title(pgapname.replace('_', '\_'))
        # cbar = plt.colorbar(implot, orientation='horizontal')
        # cbar.ax.set_ylabel('Pgap')
        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()


    def plotPgapZenRgView(self, pgapzenrgview, pgapname, outfile=None, maxrg=100.0):
        fig, ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(8, 5))
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.radians(90.0))
        validzenind = np.where(pgapzenrgview['zenith']>=0.0)[0]
        validrgind = np.where(pgapzenrgview['range']<maxrg)[0]
        zenmesh, rgmesh = np.meshgrid(np.radians(pgapzenrgview['zenith'][validzenind]), pgapzenrgview['range'][validrgind], indexing='ij')
        pgap = pgapzenrgview[pgapname][np.ix_(validzenind,validrgind)]
        masked_pgap = np.ma.array(pgap, mask=pgap<0.0)
        cmap = plt.get_cmap('winter')
        cmap.set_bad('r', 1.0)
        pcm = ax.pcolormesh(zenmesh, rgmesh, masked_pgap, cmap=cmap)
        ax.set_xlim(np.radians(0.0), np.radians(90.0))
        cbar = plt.colorbar(pcm)
        cbar.ax.set_ylabel('Pgap')
        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()

    def plotPlantProfile(self, dualplantprofile, outfile=None):
        fig = plt.figure(figsize=(8, 5))
        ax1 = plt.subplot2grid((6, 2), (0, 0), rowspan=5)
        ax2 = plt.subplot2grid((6, 2), (0, 1), rowspan=5, sharey=ax1)
        ax3 = plt.subplot2grid((6, 2), (5, 0), colspan=2)
        ax1.hold(True)
        ax2.hold(True)
        lineplots = [None]*len(self.pgapclassname)
        for i, name in enumerate(self.pgapclassname):
            lineplots[i] = ax1.plot(dualplantprofile[name].PAI, dualplantprofile['height'], self.markerstr[i], label=name.replace('_', '\_'))[0]
            ax2.plot(dualplantprofile[name].PAVD, dualplantprofile['height'], self.markerstr[i], label=name.replace('_', '\_'))[0]

        ax1.set_title("PAI")
        ax2.set_title("PAVD")
        ax1.set_xlabel("PAI")
        ax1.set_ylabel("height (m)")
        ax2.set_xlabel("PAVD")
        ax2.set_ylabel("height (m)")

        plt.sca(ax3)
        plt.axis('off')
        legendstr = [ name.replace('_', '\_') for name in self.pgapclassname]
        ax3.legend(lineplots, legendstr, bbox_to_anchor=(0., 0., 1, 0.1), loc='lower left', \
                       ncol=5, mode="expand", borderaxespad=0.)
        fig.tight_layout()

        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        else:
            plt.show()


    def writeDualPlantProfile(self, DualPlantProfile, outfile):
        nrows = len(DualPlantProfile['height'])
        ncols = len(self.pgapclassname)*3
        outmat = np.zeros((nrows, ncols))
        headerstr = "heights,"
        for i, name in enumerate(self.pgapclassname):
            outmat[:, i*3] = DualPlantProfile[name].PAI.squeeze()
            outmat[:, i*3+1] = DualPlantProfile[name].PAVD.squeeze()
            outmat[:, i*3+2] = DualPlantProfile[name].MLA.squeeze()
            headerstr = headerstr + "{0:s}_PAI,{0:s}_PAVD,{0:s}_MLA,".format(name)
        outmat = np.hstack((DualPlantProfile['height'].reshape(nrows, 1), outmat))
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
