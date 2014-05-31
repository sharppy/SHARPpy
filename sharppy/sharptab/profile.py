''' Create the Sounding (Profile) Object '''
from __future__ import division
import os
import numpy as np
import numpy.ma as ma
from sharppy.sharptab import utils, winds, params, interp, thermo, watch_type
from sharppy.databases.sars import sars_hail
from sharppy.databases.pwv import pwv_climo
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
        self.location = kwargs.get('location')
        self.pres[self.pres == self.missing] = ma.masked
        self.hght[self.hght == self.missing] = ma.masked
        self.tmpc[self.tmpc == self.missing] = ma.masked
        self.dwpc[self.dwpc == self.missing] = ma.masked
        self.logp = np.log10(self.pres.copy())
        self.vtmp = thermo.virtemp( self.pres, self.tmpc, self.dwpc )
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
        if 'tmp_stdev' in kwargs:
            self.dew_stdev = ma.asanyarray(kwargs.get('dew_stdev'))
            self.tmp_stdev = ma.asanyarray(kwargs.get('tmp_stdev'))
            self.dew_stdev[self.dew_stdev == self.missing] = ma.masked
            self.tmp_stdev[self.tmp_stdev == self.missing] = ma.masked
            self.dew_stdev.set_fill_value(self.missing)
            self.tmp_stdev.set_fill_value(self.missing)
        elif not 'tmp_stdev' in kwargs:
            self.dew_stdev = None
            self.tmp_stdev = None
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
        ## generate theta-e profile
        self.thetae = self.get_thetae_profile()
        ## generate various parcels
        self.get_parcels()
        ## calculate thermodynamic window indices
        self.get_thermo()
        ## generate wind indices
        self.get_kinematics()
        ## get SCP, STP(cin), STP(fixed), SHIP
        self.get_severe()
        ## calculate the SARS database matches
        self.get_sars()
        ## get the possible watch type
        self.get_PWV_loc()
        self.get_watch()
        self.get_traj()

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
            theta[i] = thermo.theta(self.pres[i], self.tmpc[i])
        theta[theta == self.missing] = ma.masked
        theta.set_fill_value(self.missing)
        theta = thermo.ctok(theta)
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

    def get_parcels(self):
        '''
        Function to generate various parcels and parcel
        traces.
        
        Returns nothing, but sets the following
        variables:
        
        self.mupcl - Most Unstable Parcel
        self.sfcpcl - Surface Based Parcel
        self.mlpcl - Mixed Layer Parcel
        self.fcstpcl - Forecast Surface Parcel
        
        self.ebottom - The bottom pressure level of 
            the effective inflow layer
        self.etop - the top pressure level of
            the effective inflow layer
        self.ebotm - The bottom, meters (agl), of the
            effective inflow layer
        self.etopm - The top, meters (agl), of the
            effective inflow layer
        
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        self.sfcpcl = params.parcelx( self, flag=1 )
        self.fcstpcl = params.parcelx( self, flag=2 )
        self.mupcl = params.parcelx( self, flag=3 )
        self.mlpcl = params.parcelx( self, flag=4 )
        ## get the effective inflow layer
        self.ebottom, self.etop = params.effective_inflow_layer( self, mupcl=self.mupcl )
        self.ebotm = interp.to_agl(self, interp.hght(self, self.ebottom))
        self.etopm = interp.to_agl(self, interp.hght(self, self.etop))

    def get_kinematics(self):
        '''
        Function to generate the numerous kinematic quantities
        used for display and calculations. It requires that the
        parcel calculations have already been called for the lcl
        to el shear and mean wind vectors, as well as indices
        that require an effective inflow layer.
        
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        sfc = self.pres[self.sfc]
        heights = np.array([1000., 3000., 4000., 5000., 6000., 8000., 9000.])
        p1km, p3km, p4km, p5km, p6km, p8km, p9km = interp.pres(self, interp.to_msl(self, heights))
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
        ## parameters that depend on the presence of an effective inflow layer
        if self.etop is ma.masked or self.ebottom is ma.masked:
            self.etopm = ma.masked; self.ebotm = ma.masked
            self.srwind = winds.non_parcel_bunkers_motion( self )
            self.eff_shear = [self.missing, self.missing]
            self.ebwd = [self.missing, self.missing, self.missing]
            self.mean_eff = [self.missing, self.missing, self.missing]
            self.mean_ebw = [self.missing, self.missing, self.missing]
            self.srw_eff = [self.missing, self.missing, self.missing]
            self.srw_ebw = [self.missing, self.missing, self.missing]
            self.right_esrh = [ma.masked, ma.masked, ma.masked]
            self.left_esrh = [ma.masked, ma.masked, ma.masked]
        else:
            self.srwind = params.bunkers_storm_motion(self, mupcl=self.mupcl, pbot=self.ebottom)
            depth = ( self.mupcl.elhght - self.ebotm ) / 2
            elh = interp.pres(self, interp.to_msl(self, self.ebotm + depth))
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
            self.right_esrh = winds.helicity(self, self.ebotm, self.etopm, stu=self.srwind[0], stv=self.srwind[1])
            self.left_esrh = winds.helicity(self, self.ebotm, self.etopm, stu=self.srwind[2], stv=self.srwind[3])
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
        self.srh1km = winds.helicity(self, 0, 1000., stu=self.srwind[0], stv=self.srwind[1])
        self.srh3km = winds.helicity(self, 0, 3000., stu=self.srwind[0], stv=self.srwind[1])


    def get_thermo(self):
        '''
        Function to generate thermodynamic indices.
        
        Function returns nothing, but sets the following
        variables:
        
        self.k_idx - K Index, a severe weather index
        self.pwat - Precipitable Water Vapor (inches)
        self.lapserate_3km - 0 to 3km AGL lapse rate (C/km)
        self.lapserate_3_6km - 3 to 6km AGL lapse rate (C/km)
        self.lapserate_850_500 - 850 to 500mb lapse rate (C/km)
        self.lapserate_700_500 - 700 to 500mb lapse rate (C/km)
        self.convT - The Convective Temperature (F)
        self.maxT - The Maximum Forecast Surface Temp (F)
        self.mean_mixr - Mean Mixing Ratio
        self.low_rh - low level mean relative humidity
        self.mid_rh - mid level mean relative humidity
        self.totals_totals - Totals Totals index, a severe weather index
        
        Parameters
        ----------
        None
        
        
        Returns
        -------
        None
        '''
        ## either get or calculate the indices, round to the nearest int, and
        ## convert them to strings.
        ## K Index
        self.k_idx = params.k_index( self )
        ## precipitable water
        self.pwat = params.precip_water( self )
        ## 0-3km agl lapse rate
        self.lapserate_3km = params.lapse_rate( self, 0., 3000., pres=False )
        ## 3-6km agl lapse rate
        self.lapserate_3_6km = params.lapse_rate( self, 3000., 6000., pres=False )
        ## 850-500mb lapse rate
        self.lapserate_850_500 = params.lapse_rate( self, 850., 500., pres=True )
        ## 700-500mb lapse rate
        self.lapserate_700_500 = params.lapse_rate( self, 700., 500., pres=True )
        ## convective temperature
        self.convT = thermo.ctof( params.convective_temp( self ) )
        ## sounding forecast surface temperature
        self.maxT = thermo.ctof( params.max_temp( self ) )
        #fzl = str(int(self.sfcparcel.hght0c))
        ## 100mb mean mixing ratio
        self.mean_mixr = params.mean_mixratio( self )
        ## 150mb mean rh
        self.low_rh = params.mean_relh( self )
        self.mid_rh = params.mean_relh( self, pbot=(self.pres[self.sfc] - 150),
            ptop=(self.pres[self.sfc] - 350) )
        ## calculate the totals totals index
        self.totals_totals = params.t_totals( self )
        ## calculate the inferred temperature advection
        self.inf_temp_adv = params.inferred_temp_adv(self)

    def get_severe(self):
        '''
        Function to calculate special severe weather indices.
        Requires calling get_parcels() and get_kinematics().
        
        Returns nothing, but sets the following variables:
        
        self.stp_fixed - fixed layer significant tornado parameter
        self.stp_cin - effective layer significant tornado parameter
        self.right_scp - right moving supercell composite parameter
        self.left_scp - left moving supercell composite parameter
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        self.stp_fixed = params.stp_fixed(self.sfcpcl.bplus, self.sfcpcl.lclhght, self.srh1km[0], self.sfc_6km_shear)
        if self.etop is np.ma.masked or self.ebottom is np.ma.masked:
            self.right_scp = 0.0; self.left_scp = 0.0
            self.stp_cin = 0.0
        else:
            self.right_scp = params.scp( self.mupcl.bplus, self.right_esrh[0], self.ebwspd)
            self.left_scp = params.scp( self.mupcl.bplus, self.left_esrh[0], self.ebwspd)
            self.stp_cin = params.stp_cin(self.mlpcl.bplus, self.right_esrh[0], self.ebwspd,
                self.mlpcl.lclhght, self.mlpcl.bminus)

    def get_sars(self):
        '''
        Function to get the SARS analogues from the hail and
        supercell databases. Requires calling get_kinematics() 
        and get_parcels() first. Also calculates the significant
        hail parameter.
        
        Function returns nothing, but sets the following variables:
        
        self.matches - array of sounding analogues
        self.ship - significant hail parameter
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        sfc_6km_shear = utils.KTS2MS( utils.mag( self.sfc_6km_shear[0], self.sfc_6km_shear[1]) )
        sfc_3km_shear = utils.KTS2MS( utils.mag( self.sfc_3km_shear[0], self.sfc_3km_shear[1]) )
        sfc_9km_shear = utils.KTS2MS( utils.mag( self.sfc_9km_shear[0], self.sfc_9km_shear[1]) )
        h500t = interp.temp(self, 500.)
        lapse_rate = params.lapse_rate( self, 700., 500., pres=True )
        srh3km = self.srh3km[0]
        mucape = self.mupcl.bplus
        mumr = thermo.mixratio(self.mupcl.pres, self.mupcl.dwpc)
        self.ship = params.ship(mucape, mumr, lapse_rate, h500t, sfc_6km_shear )
        self.database = 'sars_hail.txt'
        try:
            self.matches = sars_hail(self.database, mumr, mucape, h500t, lapse_rate, sfc_6km_shear,
                sfc_9km_shear, sfc_3km_shear, srh3km)
        except:
            self.matches = ma.masked

    def get_watch(self):
        '''
        Function to get the possible watch type.
        Function returns nothing, but sets the following
        variables:
        
        self.watch_type - possible watch type
        self.watch_type_color - the color of type severity
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        watch_types = watch_type.possible_watch(self)
        self.watch_type = watch_types[0][0]
        self.watch_type_color = watch_types[1][0]

    def get_traj(self):
        '''
        Function to compute the storm slinky profile using
        the trajectory model.
        
        self.slinky_traj - the list containing the position vector for the updraft
        self.updraft_tilt - the updraft tilt (an angle) with respect to the horizon
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
    
        parcel = self.mupcl
        slinky = params.parcelTraj(self, parcel)
    
        if slinky == None:
            self.slinky_traj = None
            self.updraft_tilt = None
        else:
            self.slinky_traj = slinky[0]
            self.updraft_tilt = slinky[1]

    def get_PWV_loc(self):
        '''
        Function to compute the location of the current PWV with respect to
        it's sounding climatology from Bunkers.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        self.pwv_flag = pwv_climo(self, self.location, month=None)
