''' Create the Sounding (Profile) Object '''
from __future__ import division
import numpy as np
import numpy.ma as ma
import getpass
from datetime import datetime
from sharppy.sharptab import utils, winds, params, interp, thermo, watch_type, fire
import sharppy.io.qc_tools as qc_tools
from sharppy.databases.sars import hail, supercell
from sharppy.databases.pwv import pwv_climo
from sharppy.sharptab.constants import MISSING
import logging
import warnings

def create_profile(**kwargs):
    '''
    This is a wrapper function for constructing Profile objects
    and objects that inherit from the Profile class. This will
    construct and return the appropriate Profile object
    based on the supplied keyword argument. If no profile keyword
    is supplied, it defaults to a basic Profile. This also requires
    that you pass through all the relevant keyword arguments for
    the constructors to the Profile objects and the objects that
    inherit from Profile.

    Parameters
    ----------
    Mandatory Keywords

    pres : array_like
        The pressure values (Hectopascals)
    hght : array_like
        The corresponding height values (Meters)
    tmpc : array_like
        The corresponding temperature values (Celsius)
    dwpc : array_like
        The corresponding dewpoint temperature values (Celsius)

    Optional Keyword Pairs (must use one or the other)

    wdir : array_like
        The direction from which the wind is blowing in meteorological degrees
    wspd : array_like
        The speed of the wind (kts)

    OR

    u : array_like
        The U-component of the direction from which the wind is blowing. (kts)

    v : array_like
        The V-component of the direction from which the wind is blowing. (kts)

    Optional Keywords

    missing : number, optional (default: sharppy.sharptab.constants.MISSING)
        The value of the missing flag used in the Profile objects

    profile : string, optional (default: 'default')
        The text identifier for the Profile to be generated. Valid options
        include ('default' | 'basic' | 'convective'). Default will construct a basic
        Profile, and convective will construct a ConvectiveProfile used for
        the SPC style GUI. 

    omeg: array_like
        The corresponding vertical velocity values (Pa/s)

    Returns
    -------

    Profile : a basic Profile object
        This is the most basic and default object.

    OR

    ConvectiveProfile : a child of Profile
        This is the class used for the SPC GUI.


    '''
    ## Get the user's input for which Profile to construct.
    ## Make the default the 'default' profile.
    profile = kwargs.get('profile', 'default')

    ## if the profile is default, pass the rest of the keyword
    ## arguments to the BasicProfile object and return it
    if profile == 'default':
        return BasicProfile(**kwargs)
    ## if the profile is raw, return a base profile object
    elif profile == 'raw':
        return Profile(**kwargs)
    ## if the profile is convective, pass the rest of the keyword
    ## arguments to the ConvectiveProfile object and return it
    elif profile == 'convective':
        return ConvectiveProfile(**kwargs)

class Profile(object):
    def __init__(self, **kwargs):
        ## set the missing variable
        self.missing = kwargs.get('missing', MISSING)
        self.profile = kwargs.get('profile')
        self.latitude = kwargs.get('latitude', ma.masked)
        self.strictQC = kwargs.get('strictQC', False)

        ## get the data and turn them into arrays
        self.pres = ma.asanyarray(kwargs.get('pres'), dtype=float)
        self.hght = ma.asanyarray(kwargs.get('hght'), dtype=float)
        self.tmpc = ma.asanyarray(kwargs.get('tmpc'), dtype=float)
        self.dwpc = ma.asanyarray(kwargs.get('dwpc'), dtype=float)

        assert len(self.pres) > 1 and len(self.hght) > 1 and len(self.tmpc) > 1 and len(self.dwpc) > 1,\
               "The length of the data arrays passed to Profile object constructor must all have a length greater than 1."

        assert len(self.pres) == len(self.hght) == len(self.tmpc) == len(self.dwpc),\
                "The pres, hght, tmpc, or dwpc arrays passed to the Profile object constructor must all have the same length."

        if np.ma.max(self.pres) <= 100:
            warnings.warn("The pressure values passed to the profile object are below 100 mb.  This may cause some the SHARPpy routines not to behave as expected.") 

        if 'wdir' in kwargs and 'wspd' in kwargs:
            self.wdir = ma.asanyarray(kwargs.get('wdir'), dtype=float)
            self.wspd = ma.asanyarray(kwargs.get('wspd'), dtype=float)
            assert len(self.wdir) == len(self.wspd) == len(self.pres), "The wdir and wspd arrays passed to the Profile constructor must have the same length as the pres array."
            #self.u, self.v = utils.vec2comp(self.wdir, self.wspd)
            self.u = None
            self.v = None

        ## did the user provide the wind in u,v form?
        elif 'u' in kwargs and 'v' in kwargs:
            self.u = ma.asanyarray(kwargs.get('u'), dtype=float)
            self.v = ma.asanyarray(kwargs.get('v'), dtype=float)
            assert len(self.u) == len(self.v) == len(self.pres), "The u and v arrays passed to the Profile constructor must have the same length as the pres array."

            #self.wdir, self.wspd = utils.comp2vec(self.u, self.v)
            self.wdir = None
            self.wspd = None
        else:
            warnings.warn("No wind data (wdir/wspd or u/v) passed to the Profile object constructor.  This may cause some of the SHARPpy routines to not behave as expected.")

        ## check if any standard deviation data was supplied
        if 'tmp_stdev' in kwargs:
            self.dew_stdev = ma.asanyarray(kwargs.get('dew_stdev'), dtype=float)
            self.tmp_stdev = ma.asanyarray(kwargs.get('tmp_stdev'), dtype=float)
        else:
            self.dew_stdev = None
            self.tmp_stdev = None

        if kwargs.get('omeg', None) is not None:
            ## get the omega data and turn into arrays
            self.omeg = ma.asanyarray(kwargs.get('omeg'))
            assert len(self.omeg) == len(self.pres), "Length of omeg array passed to constructor is not the same length as the pres array."
        else:
            self.omeg = None

        ## optional keyword argument for location
        self.location = kwargs.get('location', None)
        self.date = kwargs.get('date', None)

        if self.strictQC is True:
            self.checkDataIntegrity()

    @classmethod
    def copy(cls, prof, strictQC=False, **kwargs):
        '''
            Copies a profile object.
        ''' 
        new_kwargs = dict( (k, prof.__dict__[k]) for k in [ 'pres', 'hght', 'tmpc', 'dwpc', 'omeg', 'location', 'date', 'latitude', 'strictQC', 'missing' ])

        if prof.u is not None and prof.v is not None:
            new_kwargs.update({'u':prof.u, 'v':prof.v})
        else:
            new_kwargs.update({'wspd':prof.wspd, 'wdir':prof.wdir})
        
        new_kwargs.update({'strictQC':strictQC})

        # Create a new profile object using the old profile object data cls is the Class type (e.g., ConvectiveProfile)
        new_kwargs.update(kwargs)
        new_prof = cls(**new_kwargs)

        if hasattr(prof, 'srwind'):
            rmu, rmv, lmu, lmv = prof.srwind
            new_prof.set_srright(rmu, rmv)
            new_prof.set_srleft(lmu, lmv)

        return new_prof

    def toFile(self, file_name):
        snd_file = open(file_name, 'w')
        def qc(val):
            return -9999. if not utils.QC(val) else val

        snd_loc = (" " * (4 - len(self.location))) + self.location

        now = datetime.utcnow()
        #print(now, self.date)
        user = getpass.getuser()
        snd_file.write("%TITLE%\n")
        #snd_file.write("%s   %s\n Saved by user: %s on %s UTC\n" % (snd_loc, self.date.strftime("%y%m%d/%H%M"), user, now.strftime('%Y%m%d/%H%M')))
        snd_file.write("   LEVEL       HGHT       TEMP       DWPT       WDIR       WSPD\n")
        snd_file.write("-------------------------------------------------------------------\n")
        snd_file.write("%RAW%\n")
        for idx in range(self.pres.shape[0]):
            str = ""
            for col in ['pres', 'hght', 'tmpc', 'dwpc', 'wdir', 'wspd']:
                str += "%8.2f,  " % qc(self.__dict__[col][idx])

            snd_file.write(str[:-3] + "\n")
        snd_file.write("%END%\n")
        snd_file.close()

    def checkDataIntegrity(self):
        if not qc_tools.isHGHTValid(self.hght):
            qc_tools.raiseError("Invalid height data.  Data has repeat height values or height does not increase as pressure decreases.", qc_tools.DataQualityException)
        if not qc_tools.isTMPCValid(self.tmpc):
            qc_tools.raiseError("Invalid temperature data. Profile contains a temperature value < -273.15 Celsius.", qc_tools.DataQualityException)
        if not qc_tools.isDWPCValid(self.dwpc):
            qc_tools.raiseError("Invalid dewpoint data. Profile contains a dewpoint value < -273.15 Celsius.", qc_tools.DataQualityException)
        if not qc_tools.isWSPDValid(self.wspd):
            qc_tools.raiseError("Invalid wind speed data. Profile contains a wind speed value < 0 knots.", qc_tools.DataQualityException)
        if not qc_tools.isWDIRValid(self.wdir):
            qc_tools.raiseError("Invalid wind direction data. Profile contains a wind direction < 0 degrees or >= 360 degrees.", qc_tools.DataQualityException)


class BasicProfile(Profile):
    '''
    The default data class for SHARPpy. 
    All other data classes inherit from this class.
    This class holds the vertical data for pressure,
    height, temperature, dewpoint, and winds. This class
    has no indices computed.
        
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
            The speed of the wind (kts)
            
        OR
            
        u : array_like
            The U-component of the direction from which the wind
            is blowing (kts)
            
        v : array_like
            The V-component of the direction from which the wind
            is blowing. (kts)
            
        Optional Keywords
        missing : number (default: sharppy.sharptab.constants.MISSING)
            The value of the missing flag

        location : string (default: None)
            The 3 character station identifier or 4 character
            WMO station ID for radiosonde locations. Used for
            the PWV database.
        
        strictQC : boolean
            A flag that indicates whether or not the strict quality control
            routines should be run on the profile upon construction.

        Returns
        -------
        prof: Profile object
            
        '''
        super(BasicProfile, self).__init__(**kwargs)

        self.strictQC = kwargs.get('strictQC', True)

        ## did the user provide the wind in vector form?
        if self.wdir is not None:
            self.wdir[self.wdir == self.missing] = ma.masked
            self.wspd[self.wspd == self.missing] = ma.masked
            self.wdir[self.wspd.mask] = ma.masked
            self.wspd[self.wdir.mask] = ma.masked
            self.u, self.v = utils.vec2comp(self.wdir, self.wspd)

        ## did the user provide the wind in u,v form?
        elif self.u is not None:
            self.u[self.u == self.missing] = ma.masked
            self.v[self.v == self.missing] = ma.masked
            self.u[self.v.mask] = ma.masked
            self.v[self.u.mask] = ma.masked
            self.wdir, self.wspd = utils.comp2vec(self.u, self.v)

        ## check if any standard deviation data was supplied
        if self.tmp_stdev is not None:
            self.dew_stdev[self.dew_stdev == self.missing] = ma.masked
            self.tmp_stdev[self.tmp_stdev == self.missing] = ma.masked
            self.dew_stdev.set_fill_value(self.missing)
            self.tmp_stdev.set_fill_value(self.missing)

        if self.omeg is not None:
            ## get the omega data and turn into arrays
            self.omeg[self.omeg == self.missing] = ma.masked
        else:
            self.omeg = ma.masked_all(len(self.hght))

        # QC Checks on the arrays passed to the constructor.
        qc_tools.areProfileArrayLengthEqual(self)
       
        ## mask the missing values
        self.pres[self.pres == self.missing] = ma.masked
        self.hght[self.hght == self.missing] = ma.masked
        self.tmpc[self.tmpc == self.missing] = ma.masked
        self.dwpc[self.dwpc == self.missing] = ma.masked

        self.logp = np.log10(self.pres.copy())
        self.vtmp = thermo.virtemp( self.pres, self.tmpc, self.dwpc )
        idx = np.ma.where(self.pres > 0)[0]
        self.vtmp[self.dwpc.mask[idx]] = self.tmpc[self.dwpc.mask[idx]] # Masking any virtual temperature 

        ## get the index of the top and bottom of the profile
        self.sfc = self.get_sfc()
        self.top = self.get_top()

        if self.strictQC is True:
            self.checkDataIntegrity()

        ## generate the wetbulb profile
        self.wetbulb = self.get_wetbulb_profile()
        ## generate theta-e profile
        self.thetae = self.get_thetae_profile()
        ## generate theta profile
        self.theta = self.get_theta_profile()
        ## generate water vapor mixing ratio profile
        self.wvmr = self.get_wvmr_profile()
        ## generate rh profile
        self.relh = self.get_rh_profile()

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
     
    def get_wvmr_profile(self):
        '''
            Function to calculate the water vapor mixing ratio profile.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            Array of water vapor mixing ratio profile
            '''
        
        #wvmr = ma.empty(self.pres.shape[0])
        #for i in range(len(self.v)):
        wvmr = thermo.mixratio( self.pres, self.dwpc )
        wvmr[wvmr == self.missing] = ma.masked
        wvmr.set_fill_value(self.missing)
        return wvmr
    
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

    def get_rh_profile(self):
        '''
        Function to calculate the relative humidity profile
        
        Parameters
        ----------
        None
    
        Returns
        -------
        Array of the relative humidity profile
        '''

        rh = thermo.relh(self.pres, self.tmpc, self.dwpc)
        rh[rh == self.missing] = ma.masked
        rh.set_fill_value(self.missing)
        return rh


class ConvectiveProfile(BasicProfile):
    '''
    The Convective data class for SHARPPy. This is the class used
    to generate the indices that are default for the SPC NSHARP display.
    
    This class inherits from the Profile object.

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
            The speed of the wind (kts)
        
        OR
            
        u : array_like
            The U-component of the direction from which the wind
            is blowing
            
        v : array_like
            The V-component of the direction from which the wind
            is blowing.
            
        missing : number, optional (default: sharppy.sharptab.constants.MISSING)
            The value of the missing flag

        location : string, optional (default: None)
            The 3 character station identifier or 4 character
            WMO station ID for radiosonde locations. Used for
            the PWV database.

        omeg : array_like, optional
            List of the vertical velocity in pressure coordinates with height (Pascals/second)
            
        Returns
        -------
        A profile object
        '''
        ## call the constructor for Profile
        super(ConvectiveProfile, self).__init__(**kwargs)
        assert np.ma.max(self.pres) > 100, "ConvectiveProfile objects require that the minimum pressure passed in the data array is greater than 100 mb." 

        self.user_srwind = None

        # Generate the fire weather paramters
        logging.debug("Calling get_fire().")
        dt = datetime.now()
        self.get_fire()
        logging.debug("get_fire() took: " + str((datetime.now() - dt)))

        # Generate the winter inset/precipitation types
        logging.debug("Calling get_precip().")
        dt = datetime.now()
        self.get_precip()
        logging.debug("get_precip() took: " + str((datetime.now() - dt)))

        ## generate various parcels
        logging.debug("Calling get_parcels().")
        dt = datetime.now()
        self.get_parcels()
        logging.debug("get_parcels() took: " + str((datetime.now() - dt)))

        ## calculate thermodynamic window indices
        logging.debug("Calling get_thermo().")
        dt = datetime.now()
        self.get_thermo()
        logging.debug("get_thermo() took: " + str((datetime.now() - dt)))

        ## generate wind indices
        logging.debug("Calling get_kinematics().")
        dt = datetime.now()
        self.get_kinematics()
        logging.debug("get_kinematics() took: " + str((datetime.now() - dt)))

        ## get SCP, STP(cin), STP(fixed), SHIP
        logging.debug("Calling get_severe().")
        dt = datetime.now()
        self.get_severe()
        logging.debug("get_severe() took: " + str((datetime.now() - dt)))

        ## calculate the SARS database matches
        logging.debug("Calling get_sars().")
        dt = datetime.now()
        self.get_sars()
        logging.debug("get_sars() took: " + str((datetime.now() - dt)))

        ## get the precipitable water climatology
        logging.debug("Calling get_PWV_loc().")
        dt = datetime.now()
        self.get_PWV_loc()
        logging.debug("get_PWV_loc() took: " + str((datetime.now() - dt)))

        ## get the parcel trajectory
        logging.debug("Calling get_traj().")
        dt = datetime.now()
        self.get_traj()
        logging.debug("get_traj() took: " + str((datetime.now() - dt)))

        ## miscellaneous indices I didn't know where to put
        logging.debug("Calling get_indices().")
        dt = datetime.now()
        self.get_indices()
        logging.debug("get_indices() took: " + str((datetime.now() - dt)))

        ## get the possible watch type
        logging.debug("Calling get_watch().")
        dt = datetime.now()
        self.get_watch()
        logging.debug("get_watch() took: " + str((datetime.now() - dt)))

    def get_fire(self):
        '''
        Function to generate different indices and information
        regarding any fire weather in the sounding.  This helps fill
        the data shown in the FIRE inset.
    
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.fosberg = fire.fosberg(self)
        self.haines_hght = fire.haines_height(self)
        self.haines_low = fire.haines_low(self)
        self.haines_mid = fire.haines_mid(self)
        self.haines_high = fire.haines_high(self)
        self.ppbl_top = params.pbl_top(self)
        self.sfc_rh = thermo.relh(self.pres[self.sfc], self.tmpc[self.sfc], self.dwpc[self.sfc])
        pres_sfc = self.pres[self.sfc]
        pres_1km = interp.pres(self, interp.to_msl(self, 1000.))
        self.pbl_h = interp.to_agl(self, interp.hght(self, self.ppbl_top))
        self.rh01km = params.mean_relh(self, pbot=pres_sfc, ptop=pres_1km)
        self.pblrh = params.mean_relh(self, pbot=pres_sfc, ptop=self.ppbl_top)
        self.meanwind01km = winds.mean_wind(self, pbot=pres_sfc, ptop=pres_1km)
        self.meanwindpbl = winds.mean_wind(self, pbot=pres_sfc, ptop=self.ppbl_top)
        self.pblmaxwind = winds.max_wind(self, lower=0, upper=self.pbl_h)
        #self.pblmaxwind = [np.ma.masked, np.ma.masked]
        mulplvals = params.DefineParcel(self, flag=3, pres=500)
        mupcl = params.cape(self, lplvals=mulplvals)
        self.bplus_fire = mupcl.bplus

    def get_precip(self):
        '''
        Function to generate different indices and information
        regarding any precipitation in the sounding.  This helps fill
        the data shown in the WINTER inset.

        Returns nothing, but sets the following
        variables:

        self.dgz_pbot, self.dgz_ptop : the dendretic growth zone (DGZ) top and bottom (mb)
        self.dgz_meanrh : DGZ mean relative humidity (%)
        self.dgz_pw : the preciptable water vapor in the DGZ (inches)
        self.dgz_meanq : the mean water vapor mixing ratio in the DGZ (g/kg)
        self.dgz_meanomeg : the mean omega in the DGZ (microbars/second)
        self.oprh : the OPRH variable (units don't mean anything)
        self.plevel, self.phase, self.tmp, self.st : the initial phase, level, temperature, and state of any precip in the sounding
        self.tpos, self.tneg, self.ttop, self.tbot : positive and negative temperature layers in the sounding
        self.wpos, self.wneg, self.wtop, self.wbot : positive and negative wetbulb layers in the soundings
        self.precip_type : the best guess precipitation type
    
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.dgz_pbot, self.dgz_ptop = params.dgz(self)
        self.dgz_meanrh = params.mean_relh(self, pbot=self.dgz_pbot, ptop=self.dgz_ptop)
        self.dgz_pw = params.precip_water(self, pbot=self.dgz_pbot, ptop=self.dgz_ptop)
        self.dgz_meanq = params.mean_mixratio(self, pbot=self.dgz_pbot, ptop=self.dgz_ptop)
        self.dgz_meanomeg = params.mean_omega(self, pbot=self.dgz_pbot, ptop=self.dgz_ptop) * 10 # to microbars/sec
        self.oprh = self.dgz_meanomeg * self.dgz_pw * (self.dgz_meanrh/100.)

        self.plevel, self.phase, self.tmp, self.st = watch_type.init_phase(self)
        self.tpos, self.tneg, self.ttop, self.tbot = watch_type.posneg_temperature(self, start=self.plevel)
        self.wpos, self.wneg, self.wtop, self.wbot = watch_type.posneg_wetbulb(self, start=self.plevel)
        self.precip_type = watch_type.best_guess_precip(self, self.phase, self.plevel, self.tmp, self.tpos, self.tneg)


    def get_parcels(self):
        '''
        Function to generate various parcels and parcel
        traces.
        Returns nothing, but sets the following
        variables:

        self.mupcl : Most Unstable Parcel
        self.sfcpcl : Surface Based Parcel
        self.mlpcl : Mixed Layer Parcel
        self.fcstpcl : Forecast Surface Parcel
        self.ebottom : The bottom pressure level of the effective inflow layer
        self.etop : the top pressure level of the effective inflow layer
        self.ebotm : The bottom, meters (agl), of the effective inflow layer
        self.etopm : The top, meters (agl), of the effective inflow layer
    
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        self.mupcl = params.parcelx( self, flag=3 )
        if self.mupcl.lplvals.pres == self.pres[self.sfc]:
            self.sfcpcl = self.mupcl
        else:
            self.sfcpcl = params.parcelx( self, flag=1 )
        self.fcstpcl = params.parcelx( self, flag=2 )
        self.mlpcl = params.parcelx( self, flag=4 )
        self.usrpcl = params.Parcel()

        ## get the effective inflow layer data
        self.ebottom, self.etop = params.effective_inflow_layer( self, mupcl=self.mupcl )

        ## if there was no effective inflow layer, set the values to masked
        if self.etop is ma.masked or self.ebottom is ma.masked:
            self.ebotm = ma.masked; self.etopm = ma.masked
            self.effpcl = self.sfcpcl # Default to surface parcel, as in params.DefineProfile().

        ## otherwise, interpolate the heights given to above ground level
        else:
            self.ebotm = interp.to_agl(self, interp.hght(self, self.ebottom))
            self.etopm = interp.to_agl(self, interp.hght(self, self.etop))
            # The below code was adapted from params.DefineProfile()
            # Lifting one additional parcel probably won't slow the program too much.
            # It's just one more lift compared to all the lifts in the params.effective_inflow_layer() call.
            mtha = params.mean_theta(self, self.ebottom, self.etop)
            mmr = params.mean_mixratio(self, self.ebottom, self.etop)
            effpres = (self.ebottom+self.etop)/2.
            efftmpc = thermo.theta(1000., mtha, effpres)
            effdwpc = thermo.temp_at_mixrat(mmr, effpres)
            self.effpcl = params.parcelx(self, flag=5, pres=effpres, tmpc=efftmpc, dwpc=effdwpc) #This is the effective parcel.

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
        self.wind1km = interp.vec(self, p1km)
        self.wind6km = interp.vec(self, p6km)
        ## calcluate wind shear
        self.sfc_1km_shear = winds.wind_shear(self, pbot=sfc, ptop=p1km)
        self.sfc_3km_shear = winds.wind_shear(self, pbot=sfc, ptop=p3km)
        self.sfc_6km_shear = winds.wind_shear(self, pbot=sfc, ptop=p6km)
        self.sfc_8km_shear = winds.wind_shear(self, pbot=sfc, ptop=p8km)
        self.sfc_9km_shear = winds.wind_shear(self, pbot=sfc, ptop=p9km)
        self.lcl_el_shear = winds.wind_shear(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres)
        ## calculate mean wind
        self.mean_1km = utils.comp2vec(*winds.mean_wind(self, pbot=sfc, ptop=p1km))
        self.mean_3km = utils.comp2vec(*winds.mean_wind(self, pbot=sfc, ptop=p3km))
        self.mean_6km = utils.comp2vec(*winds.mean_wind(self, pbot=sfc, ptop=p6km))
        self.mean_8km = utils.comp2vec(*winds.mean_wind(self, pbot=sfc, ptop=p8km))
        self.mean_lcl_el = utils.comp2vec(*winds.mean_wind(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres))
        ## parameters that depend on the presence of an effective inflow layer
        if self.etop is ma.masked or self.ebottom is ma.masked:
            self.etopm = ma.masked; self.ebotm = ma.masked
            self.bunkers = winds.non_parcel_bunkers_motion( self )
            if self.user_srwind is None:
                self.user_srwind = self.bunkers
            self.srwind = self.user_srwind
            self.eff_shear = [MISSING, MISSING]
            self.ebwd = [MISSING, MISSING, MISSING]
            self.ebwspd = MISSING
            self.mean_eff = [MISSING, MISSING, MISSING]
            self.mean_ebw = [MISSING, MISSING, MISSING]

            self.right_srw_eff = [MISSING, MISSING, MISSING]
            self.right_srw_ebw = [MISSING, MISSING, MISSING]
            self.right_esrh = [ma.masked, ma.masked, ma.masked]
            self.right_critical_angle = ma.masked

            self.left_srw_eff = [MISSING, MISSING, MISSING]
            self.left_srw_ebw = [MISSING, MISSING, MISSING]
            self.left_esrh = [ma.masked, ma.masked, ma.masked]
            self.left_critical_angle = ma.masked
        else:
            self.bunkers = params.bunkers_storm_motion(self, mupcl=self.mupcl, pbot=self.ebottom)
            if self.user_srwind is None:
                self.user_srwind = self.bunkers
            self.srwind = self.user_srwind
            depth = ( self.mupcl.elhght - self.ebotm ) / 2
            elh = interp.pres(self, interp.to_msl(self, self.ebotm + depth))
            ## calculate mean wind
            self.mean_eff = winds.mean_wind(self, self.ebottom, self.etop )
            self.mean_ebw = winds.mean_wind(self, pbot=self.ebottom, ptop=elh )
            ## calculate wind shear of the effective layer
            self.eff_shear = winds.wind_shear(self, pbot=self.ebottom, ptop=self.etop)
            self.ebwd = winds.wind_shear(self, pbot=self.ebottom, ptop=elh)
            self.ebwspd = utils.mag( self.ebwd[0], self.ebwd[1] )
            ## calculate quantities relative to the right-mover vector
            self.right_srw_eff = winds.sr_wind(self, pbot=self.ebottom, ptop=self.etop, stu=self.srwind[0], stv=self.srwind[1] )
            self.right_srw_ebw = winds.sr_wind(self, pbot=self.ebottom, ptop=elh, stu=self.srwind[0], stv=self.srwind[1] )
            self.right_esrh = winds.helicity(self, self.ebotm, self.etopm, stu=self.srwind[0], stv=self.srwind[1])
            self.right_critical_angle = winds.critical_angle(self, stu=self.srwind[0], stv=self.srwind[1])
            ## calculate quantities relative to the left-mover vector
            self.left_srw_eff = winds.sr_wind(self, pbot=self.ebottom, ptop=self.etop, stu=self.srwind[2], stv=self.srwind[3] )
            self.left_srw_ebw = winds.sr_wind(self, pbot=self.ebottom, ptop=elh, stu=self.srwind[2], stv=self.srwind[3] )
            self.left_esrh = winds.helicity(self, self.ebotm, self.etopm, stu=self.srwind[2], stv=self.srwind[3])
            self.left_critical_angle = winds.critical_angle(self, stu=self.srwind[2], stv=self.srwind[3])

        ## calculate quantities relative to the right-mover vector
        self.right_srw_1km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p1km, stu=self.srwind[0], stv=self.srwind[1] ))
        self.right_srw_3km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p3km, stu=self.srwind[0], stv=self.srwind[1] ))
        self.right_srw_6km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p6km, stu=self.srwind[0], stv=self.srwind[1] ))
        self.right_srw_8km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p8km, stu=self.srwind[0], stv=self.srwind[1] ))
        self.right_srw_4_5km = utils.comp2vec(*winds.sr_wind(self, pbot=p4km, ptop=p5km, stu=self.srwind[0], stv=self.srwind[1] ))
        self.right_srw_lcl_el = utils.comp2vec(*winds.sr_wind(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres, stu=self.srwind[0], stv=self.srwind[1] ))
        # This is for the red, blue, and purple bars that appear on the SR Winds vs. Height plot
        self.right_srw_0_2km = winds.sr_wind(self, pbot=sfc, ptop=interp.pres(self, interp.to_msl(self, 2000.)), stu=self.srwind[0], stv=self.srwind[1])
        self.right_srw_4_6km = winds.sr_wind(self, pbot=interp.pres(self, interp.to_msl(self, 4000.)), ptop=p6km, stu=self.srwind[0], stv=self.srwind[1])
        self.right_srw_9_11km = winds.sr_wind(self, pbot=interp.pres(self, interp.to_msl(self, 9000.)), ptop=interp.pres(self, interp.to_msl(self, 11000.)), stu=self.srwind[0], stv=self.srwind[1])

        ## calculate quantities relative to the left-mover vector
        self.left_srw_1km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p1km, stu=self.srwind[2], stv=self.srwind[3] ))
        self.left_srw_3km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p3km, stu=self.srwind[2], stv=self.srwind[3] ))
        self.left_srw_6km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p6km, stu=self.srwind[2], stv=self.srwind[3] ))
        self.left_srw_8km = utils.comp2vec(*winds.sr_wind(self, pbot=sfc, ptop=p8km, stu=self.srwind[2], stv=self.srwind[3] ))
        self.left_srw_4_5km = utils.comp2vec(*winds.sr_wind(self, pbot=p4km, ptop=p5km, stu=self.srwind[2], stv=self.srwind[3] ))
        self.left_srw_lcl_el = utils.comp2vec(*winds.sr_wind(self, pbot=self.mupcl.lclpres, ptop=self.mupcl.elpres, stu=self.srwind[2], stv=self.srwind[3] ))
        # This is for the red, blue, and purple bars that appear on the SR Winds vs. Height plot
        self.left_srw_0_2km = winds.sr_wind(self, pbot=sfc, ptop=interp.pres(self, interp.to_msl(self, 2000.)), stu=self.srwind[2], stv=self.srwind[3])
        self.left_srw_4_6km = winds.sr_wind(self, pbot=interp.pres(self, interp.to_msl(self, 4000.)), ptop=p6km, stu=self.srwind[2], stv=self.srwind[3])
        self.left_srw_9_11km = winds.sr_wind(self, pbot=interp.pres(self, interp.to_msl(self, 9000.)), ptop=interp.pres(self, interp.to_msl(self, 11000.)), stu=self.srwind[2], stv=self.srwind[3])
        
        ## calculate upshear and downshear
        self.upshear_downshear = winds.mbe_vectors(self)
        self.right_srh1km = winds.helicity(self, 0, 1000., stu=self.srwind[0], stv=self.srwind[1])
        self.right_srh3km = winds.helicity(self, 0, 3000., stu=self.srwind[0], stv=self.srwind[1])
        self.left_srh1km = winds.helicity(self, 0, 1000., stu=self.srwind[2], stv=self.srwind[3])
        self.left_srh3km = winds.helicity(self, 0, 3000., stu=self.srwind[2], stv=self.srwind[3])

        self.srw_eff = self.right_srw_eff
        self.srw_ebw = self.right_srw_ebw
        self.esrh = self.right_esrh
        self.critical_angle = self.right_critical_angle
        self.srw_1km = self.right_srw_1km
        self.srw_3km = self.right_srw_3km
        self.srw_6km = self.right_srw_6km
        self.srw_8km = self.right_srw_8km
        self.srw_4_5km = self.right_srw_4_5km
        self.srw_lcl_el = self.right_srw_lcl_el
        self.srw_0_2km = self.right_srw_0_2km
        self.srw_4_6km = self.right_srw_4_6km
        self.srw_9_11km = self.right_srw_9_11km
        self.srh1km = self.right_srh1km
        self.srh3km = self.right_srh3km

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
        ## 2-6 km max lapse rate
        self.max_lapse_rate_2_6 = params.max_lapse_rate( self )
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
        self.inf_temp_adv = params.inferred_temp_adv(self, lat=self.latitude)

    def get_severe(self):
        '''
        Function to calculate special severe weather indices.
        Requires calling get_parcels() and get_kinematics().

        Returns nothing, but sets the following variables:

        self.right_stp_fixed - fixed layer significant tornado parameter (computed with SRH relative to the right-mover vector)
        self.left_stp_fixed - fixed layer significant tornado parameter (computed with SRH relative to the left-mover vector)
        self.right_stp_cin - effective layer significant tornado parameter (computed with SRH relative to the right-mover vector)
        self.left_stp_cin - effective layer significant tornado parameter (computed with SRH relative to the left-mover vector)
        self.right_scp - right moving supercell composite parameter
        self.left_scp - left moving supercell composite parameter

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        wspd = utils.mag(self.sfc_6km_shear[0], self.sfc_6km_shear[1])
        self.right_stp_fixed = params.stp_fixed(self.sfcpcl.bplus, self.sfcpcl.lclhght, self.right_srh1km[0], utils.KTS2MS(wspd))
        self.left_stp_fixed = params.stp_fixed(self.sfcpcl.bplus, self.sfcpcl.lclhght, self.left_srh1km[0], utils.KTS2MS(wspd))
        self.sherbe = params.sherb(self, effective=True)
        
        if self.etop is np.ma.masked or self.ebottom is np.ma.masked:
            self.right_scp = 0.0; self.left_scp = 0.0
            self.right_stp_cin = 0.0; self.left_stp_cin = 0.0
        else:
            self.right_scp = params.scp( self.mupcl.bplus, self.right_esrh[0], utils.KTS2MS(self.ebwspd))
            self.left_scp = params.scp( self.mupcl.bplus, self.left_esrh[0], utils.KTS2MS(self.ebwspd))

            right_esrh = self.right_esrh[0]
            left_esrh = self.left_esrh[0]

            if self.latitude < 0:
                right_esrh = -right_esrh
                left_esrh = -left_esrh

            self.right_stp_cin = params.stp_cin(self.mlpcl.bplus, right_esrh, utils.KTS2MS(self.ebwspd),
                self.mlpcl.lclhght, self.mlpcl.bminus)
            self.left_stp_cin = params.stp_cin(self.mlpcl.bplus, left_esrh, utils.KTS2MS(self.ebwspd),
                self.mlpcl.lclhght, self.mlpcl.bminus)

            if self.latitude < 0:
                self.right_stp_cin = -self.right_stp_cin
                self.left_stp_cin = -self.left_stp_cin

        if self.latitude < 0:
            self.stp_fixed = self.left_stp_fixed
            self.stp_cin = self.left_stp_cin
            self.scp = self.left_scp
        else:
            self.stp_fixed = self.right_stp_fixed
            self.stp_cin = self.right_stp_cin
            self.scp = self.right_scp

    def get_sars(self):
        '''
        Function to get the SARS analogues from the hail and
        supercell databases. Requires calling get_kinematics()
        and get_parcels() first. Also calculates the significant
        hail parameter.
        
        Function returns nothing, but sets the following variables:

        self.matches - the matches from SARS HAIL
        self.ship - significant hail parameter
        self.supercell_matches - the matches from SARS SUPERCELL
        
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
        right_srh3km = self.right_srh3km[0]
        right_srh1km = self.right_srh1km[0]
        left_srh3km = self.left_srh3km[0]
        left_srh1km = self.left_srh1km[0]
        mucape = self.mupcl.bplus
        mlcape = self.mlpcl.bplus
        mllcl = self.mlpcl.lclhght
        mumr = thermo.mixratio(self.mupcl.pres, self.mupcl.dwpc)
        self.ship = params.ship(self)

        self.hail_database = 'sars_hail.txt'
        self.supercell_database = 'sars_supercell.txt'
        try:
            self.right_matches = hail(self.hail_database, mumr, mucape, h500t, lapse_rate, sfc_6km_shear,
                sfc_9km_shear, sfc_3km_shear, right_srh3km)
        except:
            self.right_matches = ([], [], 0, 0, 0)

        try:
            self.left_matches = hail(self.hail_database, mumr, mucape, h500t, lapse_rate, sfc_6km_shear,
                sfc_9km_shear, sfc_3km_shear, -left_srh3km)
        except:
            self.left_matches = ([], [], 0, 0, 0)

        try:
            self.right_supercell_matches = supercell(self.supercell_database, mlcape, mllcl, h500t, lapse_rate, 
                utils.MS2KTS(sfc_6km_shear), right_srh1km, utils.MS2KTS(sfc_3km_shear), utils.MS2KTS(sfc_9km_shear), 
                right_srh3km)
        except:
            self.right_supercell_matches = ([], [], 0, 0, 0)

        try:
            self.left_supercell_matches = supercell(self.supercell_database, mlcape, mllcl, h500t, lapse_rate, 
                utils.MS2KTS(sfc_6km_shear), -left_srh1km, utils.MS2KTS(sfc_3km_shear), utils.MS2KTS(sfc_9km_shear), 
                -left_srh3km)
        except Exception as e:
            self.left_supercell_matches = ([], [], 0, 0, 0)

        if self.latitude < 0:
            self.supercell_matches = self.left_supercell_matches
            self.matches = self.left_matches
        else:
            self.supercell_matches = self.right_supercell_matches
            self.matches = self.right_matches

    def get_watch(self):
        '''
        Function to get the possible watch type.
        Function returns nothing, but sets the following
        variables:
        
        self.watch_type - possible watch type
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        watch_types = watch_type.possible_watch(self, use_left=False)
        self.right_watch_type = watch_types[0]

        watch_types = watch_type.possible_watch(self, use_left=True)
        self.left_watch_type = watch_types[0]

        if self.latitude < 0:
            self.watch_type = self.left_watch_type
        else:
            self.watch_type = self.right_watch_type

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
            self.slinky_traj = ma.masked
            self.updraft_tilt = ma.masked
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
        self.pwv_flag = pwv_climo(self, self.location, month=int(self.date.strftime('%m')))

    def get_indices(self):
        '''
        Function to set any additional indices that are included in the 
        thermo window.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        self.tei = params.tei(self)
        self.esp = params.esp(self)
        self.mmp = params.mmp(self)
        self.wndg = params.wndg(self)
        self.sig_severe = params.sig_severe(self)
        self.dcape, self.dpcl_ttrace, self.dpcl_ptrace = params.dcape(self)
        self.drush = thermo.ctof(self.dpcl_ttrace[-1])
        self.mburst = params.mburst(self)

    def set_srleft(self, lm_u, lm_v):
        '''
        Sets the u and v values of the left mover supercell storm motion vector.       
 
        Parameters
        ----------
        lm_u : number
            Left mover u-component of the storm motion vector
        lm_v : number
            Left mover v-component of the storm motion vector

        Returns
        -------
        None
        '''
        self.user_srwind = self.user_srwind[:2] + (lm_u, lm_v)
        self.get_kinematics()
        self.get_severe()

    def set_srright(self, rm_u, rm_v):
        '''
        Sets the u and v values of the right mover supercell storm motion vector.       
 
        Parameters
        ----------
        rm_u : number
            Right mover u-component of the storm motion vector
        rm_v : number
            Right mover v-component of the storm motion vector

        Returns
        -------
        None
        '''      
        self.user_srwind = (rm_u, rm_v) + self.user_srwind[2:] 
        self.get_kinematics()
        self.get_severe()

    def reset_srm(self):
        '''
        Resets the storm motion vector to those found by the Bunkers algorithm
 
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.user_srwind = self.bunkers
        self.get_kinematics()
        self.get_severe()
