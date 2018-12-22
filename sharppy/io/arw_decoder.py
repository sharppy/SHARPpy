import sys
import numpy as np
import datetime as dattim
import sharppy.sharptab.utils as utils
from sharppy.sharptab.constants import *
import sharppy.sharptab.thermo as thermo
import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from datetime import datetime
from sharppy.io.decoder import Decoder

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__fmtname__ = "wrf-arw"
__classname__ = "ARWDecoder"


class ARWDecoder(Decoder):
    def __init__(self, file_name):
        super(ARWDecoder, self).__init__(file_name)

    def _downloadFile(self):
        """
        Overwrite the parent class version of _downloadFile.
        Open the netCDF file and return an exception if no
        file is found. The netCDF4 library will automatically
        distinguish between a URL and local file.
        """
        ## check to make sure that the netCDF4 library is installed
        try:
            from netCDF4 import Dataset
            data = Dataset(self._file_name[0])
            return data
        except (ImportError):
            print("No netCDF install found. Cannot read netCDF file.")
            pass
        except (RuntimeError): 
            print("No such file found")

    def _find_nearest_point(self, ncfile, lon, lat):
        """
        Locate the nearest model grid point to the location
        passed through to the decoder using the formula for
        calculating the distance between points on a sphere.

        Code modified from existing code given by Nick Szapiro
        at the University of Oklahoma.
        """
        ## convert the map lat/lon into radians
        lon = np.radians(lon)
        lat = np.radians(lat)

        ## open the netCDF file from the WRF-ARW and convert
        ## its grid points into radians
        gridlons = np.radians(ncfile.variables["XLONG"][0])
        gridlats = np.radians(ncfile.variables["XLAT"][0])
 
        ## difference between points
        dlat = gridlats - lat
        dlon = gridlons - lon

        ## latitude term of the distance equation
        latTerm = np.sin(0.5*dlat)
        latTerm = np.power(latTerm, 2)
        
        ## longitude term of the distance equation
        lonTerm = np.sin(0.5*dlon)
        lonTerm = np.power(lonTerm, 2) * np.cos(lat) * np.cos(gridlats)
 
        ## we assume a radius of 1 on the unit circle
        dAngle = np.sqrt(latTerm+lonTerm)
        dist = 2.*1.0*np.arcsin(dAngle)

        ## find the smalled distance and return the index
        idx = np.where( dist == dist.min() )
        return idx

    def _parse(self):
        """
        Parse the netCDF file according to the variable naming and
        dimmensional conventions of the WRF-ARW.
        """
        ## open the file and also store the lat/lon of the selected point
        file_data = self._downloadFile()
        gridx = self._file_name[1]
        gridy = self._file_name[2]
        
        ## calculate the nearest grid point to the map point 
        idx = self._find_nearest_point(file_data, gridx, gridy)

        ## check to see if this is a 4D netCDF4 that includes all available times.
        ## If it does, open and compute the variables as 4D variables
        if len(file_data.variables["T"][:].shape) == 4:        
            ## read in the data from the WRF file and conduct necessary processing
            theta = file_data.variables["T"][:, :, idx[0], idx[1]] + 300.0
            qvapr = file_data.variables["QVAPOR"][:, :, idx[0], idx[1]] * 10**3 #g/kg
            mpres = (file_data.variables["P"][:, :, idx[0], idx[1]] + file_data.variables["PB"][:, :, idx[0], idx[1]]) * .01
            mhght = file_data.variables["PH"][:, :, idx[0], idx[1]] + file_data.variables["PHB"][:, :, idx[0], idx[1]] / G
            ## unstagger the height grid
            mhght = ( mhght[:, :-1, :, :] + mhght[:, 1:, :, :] ) / 2.

            muwin = file_data.variables["U"][:, :, idx[0], idx[1]]
            mvwin = file_data.variables["V"][:, :, idx[0], idx[1]]

            ## convert the potential temperature to air temperature
            mtmpc = thermo.theta(1000.0, theta - 273.15, p2=mpres) 
            ## convert the mixing ratio to dewpoint
            mdwpc = thermo.temp_at_mixrat(qvapr, mpres)
            ## convert the grid relative wind to earth relative
            U = muwin*file_data.variables['COSALPHA'][0, idx[0], idx[1]] - mvwin*file_data.variables['SINALPHA'][0, idx[0], idx[1]]
            V = mvwin*file_data.variables['COSALPHA'][0, idx[0], idx[1]] + muwin*file_data.variables['SINALPHA'][0, idx[0], idx[1]]
            ## convert from m/s to kts
            muwin = utils.MS2KTS(U)
            mvwin = utils.MS2KTS(V)

        ## if the data is not 4D, then it must be assumed that this is a file containing only a single time
        else:
            ## read in the data from the WRF file and conduct necessary processing
            theta = file_data.variables["T"][:, idx[0], idx[1]] + 300.0
            qvapr = file_data.variables["QVAPOR"][:, idx[0], idx[1]] * 10**3 #g/kg
            mpres = (file_data.variables["P"][:, idx[0], idx[1]] + file_data.variables["PB"][:, idx[0], idx[1]]) * .01
            mhght = file_data.variables["PH"][:, idx[0], idx[1]] + file_data.variables["PHB"][:, idx[0], idx[1]] / G
            ## unstagger the height grid
            mhght = ( mhght[:-1, :, :] + mhght[1:, :, :] ) / 2.

            muwin = file_data.variables["U"][:, idx[0], idx[1]]
            mvwin = file_data.variables["V"][:, idx[0], idx[1]]

            ## convert the potential temperature to air temperature
            mtmpc = thermo.theta(1000.0, theta - 273.15, p2=mpres) 
            ## convert the mixing ratio to dewpoint
            mdwpc = thermo.temp_at_mixrat(qvapr, mpres)
            ## convert the grid relative wind to earth relative
            U = muwin*file_data.variables['COSALPHA'][0, idx[0], idx[1]] - mvwin*file_data.variables['SINALPHA'][0, idx[0], idx[1]]
            V = mvwin*file_data.variables['COSALPHA'][0, idx[0], idx[1]] + muwin*file_data.variables['SINALPHA'][0, idx[0], idx[1]]
            ## convert from m/s to kts
            muwin = utils.MS2KTS(U)
            mvwin = utils.MS2KTS(V)

        ## get the model start time of the file
        inittime = dattim.datetime.strptime( str( file_data.START_DATE ), '%Y-%m-%d_%H:%M:%S')

        profiles = []
        dates = []
        ## loop over the available times
        
        for i in range(file_data.variables["T"][:].shape[0]):
            ## make sure the arrays are 1D
            prof_pres = mpres[i].flatten()
            prof_hght = mhght[i].flatten()
            prof_tmpc = mtmpc[i].flatten()
            prof_dwpc = mdwpc[i].flatten()
            prof_uwin = muwin[i].flatten()
            prof_vwin = mvwin[i].flatten()
            ## compute the time of the profile
            try:
                delta = dattim.timedelta( minutes=int(file_data.variables["XTIME"][i]) )
                curtime = inittime + delta
            except KeyError:
                var = ''.join(np.asarray(file_data.variables['Times'][i], dtype=str))
                curtime = dattim.datetime.strptime(var, '%Y-%m-%d_%H:%M:%S') 
            date_obj = curtime

            ## construct the profile object
            prof = profile.create_profile(profile="raw", pres=prof_pres, 
                hght=prof_hght, tmpc=prof_tmpc, dwpc=prof_dwpc, u=prof_uwin, v=prof_vwin,
                location=str(gridx) + "," + str(gridy), date=date_obj, missing=-999.0,
                latitude=gridy, strictQC=False)

            ## append the dates and profiles
            profiles.append(prof)
            dates.append(date_obj)

        ## create a profile collection - dictionary has no key since this 
        ## is not an ensemble model
        prof_coll = prof_collection.ProfCollection({'':profiles}, dates)

        return prof_coll

if __name__ == '__main__':
	file = ARWDecoder(("/Users/blumberg/Downloads/wrfout_v2_Lambert.nc", -97, 35))
