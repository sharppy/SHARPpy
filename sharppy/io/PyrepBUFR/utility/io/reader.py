from datetime import datetime

from ...external import float64, ones, nan

class UpperAirSounding(object):
    __slots__ = ('__accent_only__', 'station_id', 'station_latitude', 'station_longitude', 'station_elevation', 'sounding_datetime', 
                 'pressure', 'height', 'dry_buld_temperature', 'dewpoint_temperature', 'wind_direction', 'wind_speed')
    def __init__(self, bufr_file, accent_only=False):
        self.__accent_only__ = accent_only
        self.station_id = None
        self.station_latitude = None
        self.station_longitude = None
        self.station_elevation = None
        self.sounding_datetime = None
        
        self.pressure = None
        self.height = None
        self.dry_buld_temperature = None
        self.dewpoint_temperature = None
        self.wind_direction = None
        self.wind_speed = None

        content = sorted([x for x in bufr_file.data.to_dict(filter_keys=['SMID', 'YEAR', 'MNTH', 'DAYS', 'HOUR', 'MINU', 'SECO', 'CLATH', 'CLONH', 'HSMSL', 'LTDS', 'PRLC', 'GPH10', 'LATDH', 'LONDH', 'TMDB', 'TMDP', 'WDIR', 'WSPD']) if x['LTDS'] is not None], key=lambda a: a['LTDS'])

        if content[0]['SMID'] != '':
            self.station_id = content[0]['SMID']
        
        self.station_latitude = content[0]['CLATH']
        self.station_longitude = content[0]['CLONH']
        self.station_elevation = content[0]['HSMSL']
        self.sounding_datetime = datetime(content[0]['YEAR'], content[0]['MNTH'], content[0]['DAYS'], content[0]['HOUR'], content[0]['MINU'], content[0]['SECO'])

        for i in range(len(content)):
            if 'PRLC' in content[i]:
                if self.pressure is None:
                    self.pressure = ones(len(content), dtype=float64) * nan
            if 'GPH10' in content[i]:
                if self.height is None:
                    self.height = ones(len(content), dtype=float64) * nan
            if 'TMDB' in content[i]:
                if self.dry_buld_temperature is None:
                    self.dry_buld_temperature = ones(len(content), dtype=float64) * nan
            if 'TMDP' in content[i]:
                if self.dewpoint_temperature is None:
                    self.dewpoint_temperature = ones(len(content), dtype=float64) * nan
            if 'WDIR' in content[i]:
                if self.wind_direction is None:
                    self.wind_direction = ones(len(content), dtype=float64) * nan
            if 'WSPD' in content[i]:
                if self.wind_speed is None:
                    self.wind_speed = ones(len(content), dtype=float64) * nan

        for i in range(len(content)):
            if 'PRLC' in content[i]:
                if content[i]['PRLC'] is not None:
                    self.pressure[i] = content[i]['PRLC']
            if 'GPH10' in content[i]:
                if content[i]['GPH10'] is not None:
                    self.height[i] = content[i]['GPH10']
            if 'TMDB' in content[i]:
                if content[i]['TMDB'] is not None:
                    self.dry_buld_temperature[i] = content[i]['TMDB']
            if 'TMDP' in content[i]:
                if content[i]['TMDP'] is not None:
                    self.dewpoint_temperature[i] = content[i]['TMDP']
            if 'WDIR' in content[i]:
                if content[i]['WDIR'] is not None:
                    self.wind_direction[i] = content[i]['WDIR']
            if 'WSPD' in content[i]:
                if content[i]['WSPD'] is not None:
                    self.wind_speed[i] = content[i]['WSPD']

