''' Create the Sounding (Profile) Object '''
from __future__ import division
import os
import numpy as np
import numpy.ma as ma
from sharppy.sharptab import utils, winds, params, interp, thermo
from sharppy.sharptab.sars import sars_hail
from sharppy.sharptab.constants import MISSING


class Profile(object):
    '''
    The default data class for SHARPpy

    '''
    def __init__(self, **kwargs):
        '''
        Create the sounding data object

        Parameters
        ----------
        Mandatory Keywords
            pres : array_like
                The pressure values (Hectopaschals)
            hght : array_like
                The corresponding height values (Meters)
            tmpc : array_like
                The corresponding temperature values (Celsius)
            dwpc : array_like
                The corresponding dewpoint temperature values (Celsius)

        Optional Keyword Pairs (must use one or the other)
            wdir : array_like
                The direction from which the wind is blowing in
                meteorological degrees
            wspd : array_like
                The speed of the wind

            OR

            u : array_like
                The U-component of the direction from which the wind
                is blowing
            v : array_like
                The V-component of the direction from which the wind
                is blowing.

        Optional Keywords
            missing : number (default: sharppy.sharptab.constants.MISSING)
                The value of the missing flag

        Returns
        -------
        A profile object

        '''
        self.missing = kwargs.get('missing', MISSING)
        self.masked = ma.masked
        self.pres = ma.asanyarray(kwargs.get('pres'))
        self.hght = ma.asanyarray(kwargs.get('hght'))
        self.tmpc = ma.asanyarray(kwargs.get('tmpc'))
        self.dwpc = ma.asanyarray(kwargs.get('dwpc'))
        self.pres[self.pres == self.missing] = ma.masked
        self.hght[self.hght == self.missing] = ma.masked
        self.tmpc[self.tmpc == self.missing] = ma.masked
        self.dwpc[self.dwpc == self.missing] = ma.masked
        self.logp = np.log10(self.pres.copy())
        if 'wdir' in kwargs:
            self.wdir = ma.asanyarray(kwargs.get('wdir'))
            self.wspd = ma.asanyarray(kwargs.get('wspd'))
            self.wdir[self.wdir == self.missing] = ma.masked
            self.wspd[self.wspd == self.missing] = ma.masked
            self.wdir[self.wspd.mask] = ma.masked
            self.wspd[self.wdir.mask] = ma.masked
            self.u, self.v = utils.vec2comp(self.wdir, self.wspd)
        elif 'u' in kwargs:
            self.u = ma.asanyarray(kwargs.get('u'))
            self.v = ma.asanyarray(kwargs.get('v'))
            self.u[self.u == self.missing] = ma.masked
            self.v[self.v == self.missing] = ma.masked
            self.u[self.v.mask] = ma.masked
            self.v[self.u.mask] = ma.masked
            self.wdir, self.wspd = utils.comp2vec(self.u, self.v)
        self.pres.set_fill_value(self.missing)
        self.hght.set_fill_value(self.missing)
        self.tmpc.set_fill_value(self.missing)
        self.dwpc.set_fill_value(self.missing)
        self.wdir.set_fill_value(self.missing)
        self.wspd.set_fill_value(self.missing)
        self.u.set_fill_value(self.missing)
        self.v.set_fill_value(self.missing)
        self.sfc = self.get_sfc()
        self.top = self.get_top()
        ## generate the wetbulb profile
        self.wetbulb = self.get_wetbulb_profile()
        ## generate the theta profile
        self.theta = self.get_theta_profile()
        ## generate theta-e profile
        self.thetae = self.get_thetae_profile()
        ## generate various parcels
        self.sfcpcl = params.parcelx( self, flag=1 )
        self.fcstpcl = params.parcelx( self, flag=2 )
        self.mupcl = params.parcelx( self, flag=3 )
        self.mlpcl = params.parcelx( self, flag=4 )
        self.brnu = self.mupcl.brnu
        self.brnv = self.mupcl.brnv
        ## generate wind indices
        ## get the pressure at various levels
        sfc = self.pres[self.sfc]
        p1km = interp.pres(self, interp.to_msl(self, 1000.))
        p3km = interp.pres(self, interp.to_msl(self, 3000.))
        p4km = interp.pres(self, interp.to_msl(self, 4000.))
        p5km = interp.pres(self, interp.to_msl(self, 5000.))
        p6km = interp.pres(self, interp.to_msl(self, 6000.))
        p8km = interp.pres(self, interp.to_msl(self, 8000.))
        p9km = interp.pres(self, interp.to_msl(self, 9000.))
        ## 1km and 6km winds
        self.wind1km = interp.components(self, p1km)
        self.wind6km = interp.components(self, p6km)
        ## calcluate wind shear
        self.sfc_1km_shear = winds.wind_shear(self, pbot=sfc, ptop=p1km)
        self.sfc_3km_shear = winds.wind_shear(self, pbot=sfc, ptop=p3km)
        self.sfc_6km_shear = winds.wind_shear(self, pbot=sfc, ptop=p6km)
        self.sfc_8km_shear = winds.wind_shear(self, pbot=sfc, ptop=p8km)
        self.sfc_9km_shear = winds.wind_shear(self, pbot=sfc, ptop=p9km)
        self.lcl_el_shear = winds.wind_shear(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres)
        ## calculate mean wind
        self.mean_1km = winds.mean_wind(self, pbot=sfc, ptop=p1km)
        self.mean_3km = winds.mean_wind(self, pbot=sfc, ptop=p3km)
        self.mean_6km = winds.mean_wind(self, pbot=sfc, ptop=p6km)
        self.mean_8km = winds.mean_wind(self, pbot=sfc, ptop=p8km)
        self.mean_lcl_el = winds.mean_wind(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres)
        ## generate other indices
        self.ebottom, self.etop = params.effective_inflow_layer( self, mupcl=self.mupcl )
       
        if self.etop is np.ma.masked or self.ebottom is np.ma.masked:
            self.etopm = ma.masked; self.ebotm = ma.masked
            self.srwind = winds.non_parcel_bunkers_motion( self )
            self.right_esrh = [ma.masked, ma.masked, ma.masked]
            self.left_esrh = [ma.masked, ma.masked, ma.masked]
            self.eff_shear = [self.missing, self.missing]
            self.ebwd = [self.missing, self.missing, self.missing]
            self.mean_eff = [self.missing, self.missing, self.missing]
            self.mean_ebw = [self.missing, self.missing, self.missing]
            self.srw_eff = [self.missing, self.missing, self.missing]
            self.srw_ebw = [self.missing, self.missing, self.missing]
            self.right_scp = 0.0; self.left_scp = 0.0
            self.stp_cin = 0.0
        else:
            self.ebotm = interp.to_agl(self, interp.hght(self, self.ebottom))
            self.etopm = interp.to_agl(self, interp.hght(self, self.etop))
            self.srwind = params.bunkers_storm_motion(self, mupcl=self.mupcl, pbot=self.ebottom)
            depth = ( self.mupcl.elhght - self.ebotm ) / 2
            elh = interp.pres(self, interp.to_msl(self, self.ebotm + depth))
            ## calculate helicity
            self.right_esrh = winds.helicity(self, self.ebotm, self.etopm, stu=self.srwind[0], stv=self.srwind[1])
            self.left_esrh = winds.helicity(self, self.ebotm, self.etopm, stu=self.srwind[2], stv=self.srwind[3])
            ## calculate mean wind
            self.mean_eff = winds.mean_wind(self, self.ebottom, self.etop )
            self.mean_ebw = winds.mean_wind(self, pbot=self.ebottom, ptop=elh )
            ## calculate wind shear of the effective layer
            self.eff_shear = winds.wind_shear(self, pbot=self.ebottom, ptop=self.etop)
            self.ebwd = winds.wind_shear(self, pbot=self.ebottom, ptop=elh)
            self.ebwspd = utils.mag( self.ebwd[0], self.ebwd[1] )
            ## calculate the mean sr wind
            self.srw_eff = winds.sr_wind(self, pbot=self.ebottom, ptop=self.etop, stu=self.srwind[0], stv=self.srwind[1] )
            self.srw_ebw = winds.sr_wind(self, pbot=self.ebottom, ptop=elh, stu=self.srwind[0], stv=self.srwind[1] )
            #self.stp_fixed = params.stp( self.sfcpcl, )
            #self.stp_cin = params.stp( self.mlpcl, )
            self.right_scp = params.scp( self.mupcl.bplus, self.right_esrh[0], self.ebwspd)
            self.left_scp = params.scp( self.mupcl.bplus, self.left_esrh[0], self.ebwspd)
            self.stp_cin = params.stp_cin(self.mlpcl.bplus, self.right_esrh[0], self.ebwspd,
                    self.mlpcl.lclhght, self.mlpcl.bminus)
            #self.ship = params.ship()
        ## calculate helicity
        self.srh1km = winds.helicity(self, 0, 1000., stu=self.srwind[0], stv=self.srwind[1])
        self.srh3km = winds.helicity(self, 0, 3000., stu=self.srwind[0], stv=self.srwind[1])
        ## calculate mean srw
        self.srw_1km = winds.sr_wind(self, pbot=sfc, ptop=p1km, stu=self.srwind[0], stv=self.srwind[1] )
        self.srw_3km = winds.sr_wind(self, pbot=sfc, ptop=p3km, stu=self.srwind[0], stv=self.srwind[1] )
        self.srw_6km = winds.sr_wind(self, pbot=sfc, ptop=p6km, stu=self.srwind[0], stv=self.srwind[1] )
        self.srw_8km = winds.sr_wind(self, pbot=sfc, ptop=p8km, stu=self.srwind[0], stv=self.srwind[1] )
        self.srw_4_5km = winds.sr_wind(self, pbot=p4km, ptop=p5km, stu=self.srwind[0], stv=self.srwind[1] )
        self.srw_lcl_el = winds.sr_wind(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres, stu=self.srwind[0], stv=self.srwind[1] )
        # This is for the red, blue, and purple bars that appear on the SR Winds vs. Height plot
        self.srw_0_2km = winds.sr_wind(self, pbot=sfc, ptop=interp.pres(self, interp.to_msl(self, 2000.)), stu=self.srwind[0], stv=self.srwind[1])
        self.srw_4_6km = winds.sr_wind(self, pbot=interp.pres(self, interp.to_msl(self, 4000.)), ptop=p6km, stu=self.srwind[0], stv=self.srwind[1])
        self.srw_9_11km = winds.sr_wind(self, pbot=interp.pres(self, interp.to_msl(self, 9000.)), ptop=interp.pres(self, interp.to_msl(self, 11000.)), stu=self.srwind[0], stv=self.srwind[1])

        ## calculate upshear and downshear
        self.upshear_downshear = winds.mbe_vectors(self)
        ## calculate the SARS database matches
        sfc_6km_shear = utils.KTS2MS( utils.mag( self.sfc_6km_shear[0], self.sfc_6km_shear[1]) )
        sfc_3km_shear = utils.KTS2MS( utils.mag( self.sfc_3km_shear[0], self.sfc_3km_shear[1]) )
        sfc_9km_shear = utils.KTS2MS( utils.mag( self.sfc_9km_shear[0], self.sfc_9km_shear[1]) )
        h500t = interp.temp(self, 500.)
        lapse_rate = params.lapse_rate( self, 700., 500., pres=True )
        srh3km = self.srh3km[0]
        mucape = self.mupcl.bplus
        mumr = thermo.mixratio(self.mupcl.pres, self.mupcl.dwpc)
        self.database = os.path.join( os.path.dirname( __file__ ), 'nlist.txt' )
        try:
            self.matches = sars_hail(self.database, mumr, mucape, h500t, lapse_rate, sfc_6km_shear,
                sfc_9km_shear, sfc_3km_shear, srh3km)
        except:
            self.matches = ma.masked
        self.stp_fixed = params.stp_fixed(self.sfcpcl.bplus, self.sfcpcl.lclhght, self.srh1km[0], sfc_6km_shear)
        self.ship = params.ship(mucape, mumr, lapse_rate, h500t, sfc_6km_shear )

    def get_sfc(self):
        '''
        Convenience function to get the index of the surface. It is
        determined by finding the lowest level in which a temperature is
        reported.

        Parameters
        ----------
        None

        Returns
        -------
        Index of the surface

        '''
        return np.where(~self.tmpc.mask)[0].min()
    
    def get_top(self):
        '''
        Convenience function to get the index of the surface. It is
        determined by finding the lowest level in which a temperature is
        reported.
            
        Parameters
        ----------
        None
            
        Returns
        -------
        Index of the surface
            
        '''
        return np.where(~self.tmpc.mask)[0].max()

    def get_wetbulb_profile(self):
        '''
        Function to calculate the wetbulb profile.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        Array of wet bulb profile
        '''
        wetbulb = ma.empty(self.pres.shape[0])
        for i in range(len(self.v)):
            wetbulb[i] = thermo.wetbulb( self.pres[i], self.tmpc[i], self.dwpc[i] )
        wetbulb[wetbulb == self.missing] = ma.masked
        wetbulb.set_fill_value(self.missing)
        return wetbulb

    def get_theta_profile(self):
        '''
        Function to calculate the theta profile.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        Array of theta profile
        '''
        theta = ma.empty(self.pres.shape[0])
        for i in range(len(self.v)):
            theta[i] = thermo.ctok( thermo.theta(self.pres[i], self.tmpc[i]) )
        theta[theta == self.missing] = ma.masked
        theta.set_fill_value(self.missing)
        return theta

    def get_thetae_profile(self):
        '''
        Function to calculate the theta-e profile.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        Array of theta-e profile
        '''
        thetae = ma.empty(self.pres.shape[0])
        for i in range(len(self.v)):
            thetae[i] = thermo.ctok( thermo.thetae(self.pres[i], self.tmpc[i], self.dwpc[i]) )
        thetae[thetae == self.missing] = ma.masked
        thetae.set_fill_value(self.missing)
        return thetae

