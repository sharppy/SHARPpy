from copy import deepcopy
from datetime import datetime, timedelta

from ...external import arange, arctan2, array, compare, diff, exp, fill_array, float64, hypot, isfinite, isnan, log, logical_and, nan, numpy_found, pi

sat_pressure_0c = 611.2
molecular_weight_ratio = 0.6219569100577033
zero_degc = 273.15
g = 9.80665
Rd = 287.04749097718457

t0 = 288.0
p0 = 101325.0
gamma = 6.5e-3

def mixing_ratio_from_specific_humidity(specific_humidity):
    return specific_humidity / (1 - specific_humidity)

def saturation_mixing_ratio(total_press, temperature):
    return mixing_ratio(saturation_vapor_pressure(temperature), total_press)

def saturation_vapor_pressure(temperature):
    return sat_pressure_0c * exp(
        17.67 * (temperature - 273.15) / (temperature - 29.65)
    )

def mixing_ratio(partial_press, total_press):
    return molecular_weight_ratio * partial_press / (total_press - partial_press)

def relative_humidity_from_specific_humidity(pressure, temperature, specific_humidity):
    return (mixing_ratio_from_specific_humidity(specific_humidity)
            / saturation_mixing_ratio(pressure, temperature))

def dewpoint_from_specific_humidity(pressure, temperature, specific_humidity, minimum_relative_humidity=0.0000001):
    relative_humidity = relative_humidity_from_specific_humidity(
                                               pressure, temperature, specific_humidity)
    if isnan(relative_humidity):
        relative_humidity = minimum_relative_humidity
    relative_humidity = max(relative_humidity, minimum_relative_humidity)
    return dewpoint_from_relative_humidity(temperature, relative_humidity)

def dewpoint_from_relative_humidity(temperature, relative_humidity):
    return dewpoint(relative_humidity * saturation_vapor_pressure(temperature))

def dewpoint(vapor_pressure):
    val = log(vapor_pressure / sat_pressure_0c)
    return zero_degc + 243.5 * val / (17.67 - val)

def wind_speed(u, v):
    return hypot(u, v)

def wind_direction(u, v):
    return (90 - arctan2(-v, -u) * 180 / pi) % 360

def vertical_velocity_pressure_specific_humidity(w, pressure, temperature, specific_humidity):
    rho = density(pressure, temperature, mixing_ratio_from_specific_humidity(specific_humidity))
    return (-g * rho * w)

def density(pressure, temperature, mixing_ratio):
    virttemp = virtual_temperature(temperature, mixing_ratio)
    return (pressure / (Rd * virttemp))

def virtual_temperature(temperature, mixing_ratio):
    return temperature * ((mixing_ratio + molecular_weight_ratio)
                          / (molecular_weight_ratio * (1 + mixing_ratio)))

def pressure_to_height_std(pressure):
    return (t0 / gamma) * (1 - (pressure / p0)**(Rd * gamma / g))

def read_bufr_sounding(bufr_file, ascent_only=False):
    bufr_data = bufr_file.data.to_dict()
    soundings = []
    if 'LTDS' in bufr_data[0]:
        soundings.append(UpperAirSounding(bufr_data, ascent_only=ascent_only))
    elif 'FTIM' in bufr_data[0]:
        for profile_index in sorted(set([x['FTIM'] for x in bufr_data if 'FTIM' in x])):
            soundings.append(ModelSounding([x for x in bufr_data if 'FTIM' in x and x['FTIM'] == profile_index], ascent_only=ascent_only))

    return soundings

def clear_empty_array(test_array):
    return None if set([None if isnan(x) else x for x in test_array]) == {None} else test_array

class BUFRSounding(object):
    __slots__ = ('__ascent_only__', '__mask__', 'station_id', 'station_latitude', 'station_longitude', 'station_elevation', 
                 'sounding_datetime', 'pressure', 'height', 'dry_buld_temperature', 'dewpoint_temperature', 'wind_direction', 
                 'wind_speed', 'omega')
    def __init__(self, ascent_only=False):
        self.__ascent_only__ = ascent_only
        self.__mask__ = None

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
        self.omega = None

    def __apply_mask__(self):
        if self.__ascent_only__ and self.pressure is not None:
            self.pressure = self.__apply_field_mask__(self.pressure)
        if self.__ascent_only__ and self.height is not None:
            self.height = self.__apply_field_mask__(self.height)
        if self.__ascent_only__ and self.dry_buld_temperature is not None:
            self.dry_buld_temperature = self.__apply_field_mask__(self.dry_buld_temperature)
        if self.__ascent_only__ and self.dewpoint_temperature is not None:
            self.dewpoint_temperature = self.__apply_field_mask__(self.dewpoint_temperature)
        if self.__ascent_only__ and self.wind_direction is not None:
            self.wind_direction = self.__apply_field_mask__(self.wind_direction)
        if self.__ascent_only__ and self.wind_speed is not None:
            self.wind_speed = self.__apply_field_mask__(self.wind_speed)
        if self.__ascent_only__ and self.omega is not None:
            self.omega = self.__apply_field_mask__(self.omega)

    def __apply_field_mask__(self, values):
        if self.__mask__ is None:
            self.__mask__ = self.__get_ascent_only_mask__()
        if numpy_found:
            new_values = values[self.__mask__]
        else:
            new_values = [values[i] for i in self.__mask__]
        return new_values

    def __get_ascent_only_mask__(self):
        index = arange(len(self.pressure))
        height = deepcopy(self.height)
        pressure = deepcopy(self.pressure)
        mask = logical_and(compare(diff(height, n=1, prepend=height[0]-1), '>', 0),
                            compare(diff(pressure, n=1, prepend=pressure[0]+1), '<', 0))
        while sum(mask) != len(mask):
            index = array([index[i] for i, x in enumerate(mask) if x])
            height = array([height[i] for i, x in enumerate(mask) if x])
            pressure = array([pressure[i] for i, x in enumerate(mask) if x])
            mask = logical_and(compare(diff(height, n=1, prepend=height[0]-1), '>', 0),
                                compare(diff(pressure, n=1, prepend=pressure[0]+1), '<', 0))
        return index

class ModelSounding(BUFRSounding):
    def __init__(self, bufr_data, ascent_only=False):
        super().__init__(ascent_only=ascent_only)

        content = sorted([x for x in bufr_data if 'PRES' in x and x['PRES'] is not None and isfinite(x['PRES']) and x['PRES'] > 50], key=lambda a: a['PRES'], reverse=True)

        if content[0]['RPID'] is not None and content[0]['RPID'] != '':
            self.station_id = content[0]['RPID']
        elif content[0]['STNM'] is not None:
            self.station_id = str(content[0]['STNM'])

        self.station_latitude = content[0]['CLAT']
        self.station_longitude = content[0]['CLON']
        self.station_elevation = content[0]['GELV']
        self.sounding_datetime = datetime(content[0]['nominal_year'], content[0]['nominal_month'], content[0]['nominal_day'], content[0]['nominal_hour'], content[0]['nominal_minute'], content[0]['nominal_second']) + timedelta(seconds=int(content[0]['FTIM']))

        self.pressure = clear_empty_array(array([x['PRES'] if 'PRES' in x else None for x in content], dtype='float64'))
        self.height = clear_empty_array(array([ x['GELV'] - pressure_to_height_std(x['PRSS']) + pressure_to_height_std(x['PRES']) if 'GELV' in x and 'PRSS' in x and 'PRES' in x else None for x in content], dtype='float64'))
        self.dry_buld_temperature = clear_empty_array(array([x['TMDB'] if 'TMDB' in x else None for x in content], dtype='float64'))
        self.dewpoint_temperature = clear_empty_array(array([dewpoint_from_specific_humidity(x['PRES'], x['TMDB'], x['SPFH']) if 'PRES' in x and 'TMDB' in x and 'SPFH' in x else None for x in content], dtype='float64'))
        self.wind_direction = clear_empty_array(array([wind_direction(x['UWND'], x['VWND']) if 'UWND' in x and 'VWND' in x else None for x in content], dtype='float64'))
        self.wind_speed = clear_empty_array(array([wind_speed(x['UWND'], x['VWND']) if 'UWND' in x and 'VWND' in x else None for x in content], dtype='float64'))
        self.omega = clear_empty_array(array([x['OMEG'] if 'OMEG' in x else None for x in content], dtype='float64'))
        if self.omega is None:
            self.omega = clear_empty_array(array([vertical_velocity_pressure_specific_humidity(x['VVEL'] / 100.0, x['PRES'], x['TMDB'], x['SPFH']) if 'VVEL' in x and 'PRES' in x and 'TMDB' in x and 'SPFH' in x else None for x in content], dtype='float64'))

        self.__apply_mask__()

class UpperAirSounding(BUFRSounding):
    def __init__(self, bufr_data, ascent_only=False):
        super().__init__(ascent_only=ascent_only)

        content = sorted(bufr_data, key=lambda a: a['LTDS'] if a['LTDS'] is not None else 9999999999999)

        if content[0]['SMID'] != '':
            self.station_id = content[0]['SMID']

        self.station_latitude = content[0]['CLATH']
        self.station_longitude = content[0]['CLONH']
        self.station_elevation = content[0]['HSMSL']
        self.sounding_datetime = datetime(content[0]['YEAR'], content[0]['MNTH'], content[0]['DAYS'], content[0]['HOUR'], content[0]['MINU'], content[0]['SECO'])       

        self.pressure = clear_empty_array(array([x['PRLC'] if 'PRLC' in x else None for x in content], dtype='float64'))
        self.height = clear_empty_array(array([x['GPH10'] if 'GPH10' in x else None for x in content], dtype='float64'))
        self.dry_buld_temperature = clear_empty_array(array([x['TMDB'] if 'TMDB' in x else None for x in content], dtype='float64'))
        self.dewpoint_temperature = clear_empty_array(array([x['TMDP'] if 'TMDP' in x else None for x in content], dtype='float64'))
        self.wind_direction = clear_empty_array(array([x['WDIR'] if 'WDIR' in x else None for x in content], dtype='float64'))
        self.wind_speed = clear_empty_array(array([x['WSPD'] if 'WSPD' in x else None for x in content], dtype='float64'))

        self.__apply_mask__()