import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from decoder import Decoder

from bufrpy.bufrdec import decode_file
from bufrpy.table import get_table
from bufrpy.value import BufrValue
from datetime import datetime, timedelta
from calendar import timegm
from io import BytesIO

__fmtname__ = "ibufr"
__classname__ = "IMETBufrDecoder"

TIME_ADJUST = False

meta_fields = {'SHIP OR MOBILE LAND STATION IDENTIFIER'                     : ['id',     lambda x: ''.join([i if ord(i) < 128 else '' for i in x.replace('\x00','').strip()])], \
               'YEAR'                                                       : ['year',   lambda x: int(x)], \
               'MONTH'                                                      : ['month',  lambda x: int(x)], \
               'DAY'                                                        : ['day',    lambda x: int(x)], \
               'HOUR'                                                       : ['hour',   lambda x: int(x)], \
               'MINUTE'                                                     : ['minute', lambda x: int(x)], \
               'SECOND'                                                     : ['second', lambda x: int(x)], \
               'LATITUDE (HIGH ACCURACY)'                                   : ['lat',    lambda x: float(x)], \
               'LONGITUDE (HIGH ACCURACY)'                                  : ['lon',    lambda x: float(x)], \
               'HEIGHT OF STATION GROUND ABOVE MEAN SEA LEVEL (SEE NOTE 3)' : ['elev',   lambda x: float(x)]}
data_fields = {'PRESSURE'                                                   : ['pres',   lambda x: float(x)/100.0], \
               'GEOPOTENTIAL HEIGHT'                                        : ['hght',   lambda x: float(x)], \
               'TEMPERATURE/DRY-BULB TEMPERATURE'                           : ['temp',   lambda x: float(x) - 273.15], \
               'DEW-POINT TEMPERATURE'                                      : ['dwpt',   lambda x: float(x) - 273.15], \
               'WIND DIRECTION'                                             : ['wdir',   lambda x: float(x) % 360.0], \
               'WIND SPEED'                                                 : ['wspd',   lambda x: float(x) * 1.94384]}
missing_data = -9999.0

class IMETBufrDecoder(Decoder):
    def __init__(self, file_name):
        super(IMETBufrDecoder, self).__init__(file_name)
    def __adjust_time__(self, sounding_time):
        time_offset = -1 * (timegm(sounding_time.utctimetuple())%(TIME_ADJUST * 3600))
        if abs(time_offset) >= (TIME_ADJUST * 1800):
            time_offset += (TIME_ADJUST * 3600)
        return sounding_time + timedelta(seconds=time_offset)
        
    def _parse(self):
        binary_bufr = self._downloadFile()
        bufr_start = 0
        bufr_length = len(binary_bufr)
        while binary_bufr[bufr_start:bufr_start+4] != 'BUFR':
            bufr_start += 1
            if bufr_start > bufr_length - 4:
                raise IOError('Not a BUFR file')
        with BytesIO(binary_bufr[bufr_start:]) as bufr_file:
            contents = decode_file(bufr_file, get_table())
        profiles = []
        dates = []
        location = None
        for subset_num in range(len(contents.section4.subsets)):
            meta_data = {}
            data = {}
            for x in data_fields:
                data[data_fields[x][0]] = []
            subset = contents.section4.subsets[subset_num]
            for value_num in range(len(subset.values)):
                value = subset.values[value_num]
                if type(value) == BufrValue:
                    value_name = value.descriptor.significance
                    if value_name in meta_fields:
                        meta_data[meta_fields[value_name][0]] = meta_fields[value_name][1](value.value)
                elif type(value) == list:
                    for x in range(len(value)):
                        level_data = {}
                        for field in data_fields:
                            level_data[data_fields[field][0]] = missing_data
                        for y in range(len(value[x])):
                            value_name = value[x][y].descriptor.significance
                            if value_name in data_fields:
                                if value[x][y].value is not None:
                                    level_data[data_fields[value_name][0]] = data_fields[value_name][1](value[x][y].value)
                        if level_data['pres'] != missing_data and level_data['hght'] != missing_data:
                            for field in level_data:
                                data[field].append(level_data[field])
            meta_data['date'] = datetime(meta_data['year'], meta_data['month'], meta_data['day'], meta_data['hour'], meta_data['minute'],meta_data['second'])
            if TIME_ADJUST:
                meta_data['date'] = self.__adjust_time__(meta_data['date'])
            if location is None:
                location = '{0:s}(lat={1:.2f}{2:s},lon={3:.2f}{4:s},elev={5:.2f}m)'.format(meta_data['id'] if meta_data['id']!='' else 'Incident', abs(meta_data['lat']), 'N' if meta_data['lat'] > 0 else 'S', abs(meta_data['lon']), 'W' if meta_data['lon'] < 0 else 'E', meta_data['elev'])
            # Force latitude to be 35 N. Figure out a way to fix this later.
            
            # Force pressure to be always increasing
            mask = []
            for x in range(1, len(data['hght'])):
                if data['hght'][x] - data['hght'][x-1] < 1:
                    mask.append(x-1)
            for x in mask:
                for field in data:
                    data[field].pop(x)
            
            profiles.append(profile.create_profile(profile='raw', pres=data['pres'], hght=data['hght'], tmpc=data['temp'], dwpc=data['dwpt'],
                wdir=data['wdir'], wspd=data['wspd'], location=location, date=meta_data['date'], latitude=35.))
            dates.append(meta_data['date'])

        prof_coll = prof_collection.ProfCollection(
            {'':profiles}, 
            dates,
        )
        prof_coll.setMeta('loc', location)
        prof_coll.setMeta('model', 'Observed')
        return prof_coll