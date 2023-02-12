import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from .decoder import Decoder

from .PyrepBUFR import BUFRFile
from .PyrepBUFR.utility import fill_nan
from .PyrepBUFR.utility.io.reader import read_bufr_sounding, UpperAirSounding, ModelSounding
from datetime import datetime, timedelta
from calendar import timegm
from io import BytesIO
from numpy import array, floor, diff, isfinite

__fmtname__ = "bufr"
__classname__ = "BufrDecoder"

TIME_ADJUST = False
MAX_UNTHINNED_LEVELS = 100

missing_data = -9999.0

class BufrDecoder(Decoder):
    def __init__(self, file_name):
        super(BufrDecoder, self).__init__(file_name)
    def __adjust_time__(self, sounding_time):
        time_offset = -1 * (timegm(sounding_time.utctimetuple())%(TIME_ADJUST * 3600))
        if abs(time_offset) >= (TIME_ADJUST * 1800):
            time_offset += (TIME_ADJUST * 3600)
        return sounding_time + timedelta(seconds=time_offset)
        
    def _parse(self):
        with BytesIO(self._downloadFile()) as bufr_data:
            bufr_file = BUFRFile(bufr_data)
            bufr_soundings = read_bufr_sounding(bufr_file, ascent_only=True)
            bufr_file.close()
        
        profiles = []
        dates = []
        for contents in bufr_soundings:
            if type(contents) == UpperAirSounding:
                location = '{0:s}(lat={1:.2f}{2:s},lon={3:.2f}{4:s},elev={5:.2f}m)'.format(contents.station_id if contents.station_id is not None else 'Incident', abs(contents.station_latitude), 'N' if contents.station_latitude > 0 else 'S', abs(contents.station_longitude), 'W' if contents.station_longitude < 0 else 'E', contents.station_elevation)
                if TIME_ADJUST:
                    contents.sounding_datetime = self.__adjust_time__(contents.sounding_datetime)
            else:
                location = contents.station_id
            mask = isfinite(contents.pressure) * isfinite(contents.height) * (contents.pressure <= 108500.0)
            mask *= ( ( (contents.pressure >  65000) * (contents.height   <= 5570) ) + \
                    ( (contents.pressure <= 65000) * (contents.pressure >= 35000) * (contents.height >= 1940) * (contents.height <= 11760)) + \
                    ( (contents.pressure <  35000) * (contents.height   >= 5570) ) )

            for field in ['pressure', 'height', 'dry_buld_temperature', 'dewpoint_temperature', 'wind_direction', 'wind_speed', 'omega']:
                if getattr(contents, field) is not None:
                    setattr(contents, field, getattr(contents, field)[mask])
            
            # # Force height to be increasing and pressure to be decreasing
            # mask = array([True]+list((diff(contents.height, 1)>0)*(diff(contents.pressure, 1)<0)))
            # while sum(mask) != len(mask):
            #     for field in ['pressure', 'height', 'dry_buld_temperature', 'dewpoint_temperature', 'wind_direction', 'wind_speed']:
            #         setattr(contents, field, getattr(contents, field)[mask])
            #     mask = array([True]+list((diff(contents.height, 1)>0)*(diff(contents.pressure, 1)<0)))

            if len(contents.height) > MAX_UNTHINNED_LEVELS:
                thinning = int(floor(len(contents.height) / float(MAX_UNTHINNED_LEVELS)))
            else:
                thinning = 1
            if contents.omega is None:
                profiles.append(profile.create_profile(profile='raw', pres=(contents.pressure / 100.0)[::thinning], hght=contents.height[::thinning], tmpc=fill_nan(contents.dry_buld_temperature - 273.15, missing_data)[::thinning], dwpc=fill_nan(contents.dewpoint_temperature - 273.15, missing_data)[::thinning],
                                                       wdir=fill_nan(contents.wind_direction % 360, missing_data)[::thinning], wspd=fill_nan(contents.wind_speed * 1.94384, missing_data)[::thinning], location=location, date=contents.sounding_datetime, latitude=35.))
            else:
                profiles.append(profile.create_profile(profile='raw', pres=(contents.pressure / 100.0)[::thinning], hght=contents.height[::thinning], tmpc=fill_nan(contents.dry_buld_temperature - 273.15, missing_data)[::thinning], dwpc=fill_nan(contents.dewpoint_temperature - 273.15, missing_data)[::thinning],
                                                       wdir=fill_nan(contents.wind_direction % 360, missing_data)[::thinning], wspd=fill_nan(contents.wind_speed * 1.94384, missing_data)[::thinning], omeg=fill_nan(contents.omega, missing_data)[::thinning], location=location, date=contents.sounding_datetime, latitude=35.))
            dates.append(contents.sounding_datetime)

        prof_coll = prof_collection.ProfCollection(
            {'':profiles}, 
            dates,
        )
        prof_coll.setMeta('loc', location)
        if type(bufr_soundings[0]) == UpperAirSounding:
            prof_coll.setMeta('model', 'Observed')
            prof_coll.setMeta('observed', True)
        else:
            prof_coll.setMeta('model', 'Bufr')
            prof_coll.setMeta('observed', False)
        prof_coll.setMeta('base_time', dates[0])
        return prof_coll