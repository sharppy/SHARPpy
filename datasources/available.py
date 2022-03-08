
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

import certifi
import re
import numpy as np
from datetime import datetime, timedelta

cache_len = timedelta(minutes=5)


goes_base_url = "http://sharp.weather.ou.edu/soundings/goes/"
goes_text = ""
goes_time = None

# SHARP OBSERVED AVAILBILITY
def _download_goes():
    global goes_time, goes_text
    now = datetime.utcnow()
    if goes_time is None or goes_time < now - cache_len:
        url_obj = urlopen(goes_base_url, cafile=certifi.where())
        goes_text = url_obj.read().decode('utf-8')
        goes_time = now

    return goes_text

def _available_goes(dt=None):
    '''
        _available_goes()

        Gets all of the available sounding times from the SHARP observed site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SHARP site.
    '''
    text = _download_goes()

    matches = sorted(list(set(re.findall("([\d]{10})/", text))))
    return [ datetime.strptime(m, '%Y%m%d%H') for m in matches ]

def _availableat_goes(dt):
    '''
        _availableat_goes(dt)

        Get all the station locations where data was available for a certain dt object.

        Parameters
        ----------
        dt : datetime object

        Returns
        -------
        matches : array of strings
            An array that contains all of the three letter station identfiers.
    '''
    recent_url = "%s%s/available.txt" % (goes_base_url, dt.strftime('%Y%m%d%H'))
    text = urlopen(recent_url, cafile=certifi.where()).read().decode('utf-8')
    matches = re.findall("(.+).txt", text)
    return matches


sharp_base_url = "http://sharp.weather.ou.edu/soundings/obs/"
sharp_text = ""
sharp_time = None
sharp_archive_text = ""
sharp_archive_time = None

# SHARP OBSERVED AVAILBILITY
def _download_sharp():
    global sharp_time, sharp_text
    now = datetime.utcnow()
    if sharp_time is None or sharp_time < now - cache_len:
        url_obj = urlopen(sharp_base_url, cafile=certifi.where())
        sharp_text = url_obj.read().decode('utf-8')
        sharp_time = now
    return sharp_text

def _download_sharp_archive(dt):
    global sharp_time, sharp_text
    now = datetime.utcnow()
    base_url = 'http://sharp.weather.ou.edu/soundings/archive/%Y/%m/%d/'
    try:
        dt = datetime(dt.year(), dt.month(), dt.day(), 0,0,0)
    except:
        dt = dt
    if sharp_archive_time is None or sharp_archive_time < now - cache_len:
        url_obj = urlopen(dt.strftime(base_url), cafile=certifi.where())
        sharp_archive_text = url_obj.read().decode('utf-8')
        sharp_time = now
    return sharp_archive_text, dt

def _available_sharp(dt=None):
    '''
        _available_sharp()

        Gets all of the available sounding times from the SHARP observed site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SHARP site.
    '''
    if dt is None:
        text = _download_sharp()
        matches = sorted(list(set(re.findall("([\d]{10})/", text))))
        return [ datetime.strptime(m, '%Y%m%d%H') for m in matches ]
    else:
        text, dt = _download_sharp_archive(dt)
        matches = sorted(list(set(re.findall(">([\d]{2})/<", text))))
        return [ datetime.strptime(dt.strftime('%Y%m%d') + m, '%Y%m%d%H')  for m in matches ]

def _availableat_sharp(dt):
    '''
        _availableat_sharp(dt)

        Get all the station locations where data was available for a certain dt object.

        Parameters
        ----------
        dt : datetime object

        Returns
        -------
        matches : array of strings
            An array that contains all of the three letter station identfiers.
    '''
    #recent_url = "%s%s/" % (sharp_base_url, dt.strftime('%Y%m%d%H/'))
    #text = urlopen(recent_url).read().decode('utf-8')
    #matches = re.findall("a href=\"(.+).txt\"", text)
    recent_url = 'http://sharp.weather.ou.edu/soundings/archive/%Y/%m/%d/%H/'
    text = urlopen(dt.strftime(recent_url), cafile=certifi.where()).read().decode('utf-8')
    matches = re.findall("a href=\"(.+).txt\"", text)
    return matches

##################################
##################################

# NUCAPS DATA AVAILABILITY - JTS
nucaps_conus_j01_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/j01/txt/"
nucaps_conus_aq0_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/aq0/txt/"
nucaps_conus_m01_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m01/txt/"
nucaps_conus_m02_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m02/txt/"
nucaps_conus_m03_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m03/txt/"
nucaps_caribbean_j01_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/j01/txt/"
nucaps_alaska_j01_url = "https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/j01/txt/"
nucaps_text = ""

##################################
# Retrieve the obs times for CONUS NOAA-20.
def _download_nucaps_conus_j01():
    global nucaps_text
    nucaps_text = urlopen(nucaps_conus_j01_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_conus_j01(dt=None):
    '''
        _available_nucaps_conus_j01()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_conus_j01()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


##################################
# Retrieve the obs times for CONUS Aqua.
def _download_nucaps_conus_aq0():
    global nucaps_text
    nucaps_text = urlopen(nucaps_conus_aq0_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_conus_aq0(dt=None):
    '''
        _available_nucaps_conus_aq0()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_conus_aq0()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


#################################
# Retrieve the obs times for CONUS MetOp-B.
def _download_nucaps_conus_m01():
    global nucaps_text
    nucaps_text = urlopen(nucaps_conus_m01_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_conus_m01(dt=None):
    '''
        _available_nucaps_conus_m01()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_conus_m01()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


#################################
# Retrieve the obs times for CONUS MetOp-A.
def _download_nucaps_conus_m02():
    global nucaps_text
    nucaps_text = urlopen(nucaps_conus_m02_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_conus_m02(dt=None):
    '''
        _available_nucaps_conus_m02()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_conus_m02()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


#################################
# Retrieve the obs times for CONUS MetOp-C.
def _download_nucaps_conus_m03():
    global nucaps_text
    nucaps_text = urlopen(nucaps_conus_m03_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_conus_m03(dt=None):
    '''
        _available_nucaps_conus_m03()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_conus_m03()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


#################################
# Retrieve the obs times for Caribbean NOAA-20.
def _download_nucaps_caribbean_j01():
    global nucaps_text
    nucaps_text = urlopen(nucaps_caribbean_j01_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_caribbean_j01(dt=None):
    '''
        _available_nucaps_caribbean_j01()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_caribbean_j01()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


#################################
# Retrieve the obs times for Alaska NOAA-20.
def _download_nucaps_alaska_j01():
    global nucaps_text
    nucaps_text = urlopen(nucaps_alaska_j01_url, cafile=certifi.where()).read().decode('utf-8')
    return nucaps_text

def _available_nucaps_alaska_j01(dt=None):
    '''
        _available_nucaps_alaska_j01()

        Gets all of the available sounding times from the SPoRT FTP site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPoRT FTP site.
    '''
    text = _download_nucaps_alaska_j01()
    matches = sorted(list(set(re.findall(">([\d]{12})</a", text))))
    return [ datetime.strptime(m, '%Y%m%d%H%M') for m in matches ]


##################################
##################################

# SPC DATA AVAILABLILY
spc_base_url = "http://www.spc.noaa.gov/exper/soundings/"
spc_text = ""
spc_time = None

def _download_spc():
    global spc_time, spc_text
    now = datetime.utcnow()
    if spc_time is None or spc_time < now - cache_len:
        url_obj = urlopen(spc_base_url, cafile=certifi.where())
        spc_text = url_obj.read().decode('utf-8')

        spc_time = now

    return spc_text

def _available_spc(dt=None):
    '''
        _available_spc()

        Gets all of the available sounding times from the SPC site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SPC site.
    '''
    text = _download_spc()
    matches = sorted(list(set(re.findall("([\d]{8})_OBS", text))))
    return [ datetime.strptime(m, '%y%m%d%H') for m in matches ]

def _availableat_spc(dt):
    '''
        _availableat_spc(dt)

        Get all the station locations where data was available for a certain dt object.

        Parameters
        ----------
        dt : datetime object

        Returns
        -------
        matches : array of strings
            An array that contains all of the three letter station identfiers.
    '''
    recent_url = "%s%s/" % (spc_base_url, dt.strftime('%y%m%d%H_OBS'))
    text = urlopen(recent_url, cafile=certifi.where()).read().decode('utf-8')
    matches = re.findall("show_soundings\(\"([\w]{3}|[\d]{5})\"\)", text)
    return matches

### IEM BUFKIT ARCHIVE CODE
iem_base_url = "http://mtarchive.geol.iastate.edu/%Y/%m/%d/bufkit/%H/"
iem_text = ""
iem_time = None

### PSU CODE
psu_base_url = "ftp://ftp.meteo.psu.edu/pub/bufkit/"
psu_text = ""
psu_time = None

def _download_psu():
    '''
        _download_psu()

        Downloads the PSU directory webpage that lists all the
        files available.

        Returns
        -------
        psu_text : string
            Lists the files within the PSU FTP site.
    '''
    global psu_time, psu_text
    now = datetime.utcnow()
    if psu_time is None or psu_time < now - cache_len:
        url_obj = urlopen(psu_base_url, cafile=certifi.where())
        psu_text = url_obj.read().decode('utf-8')

        psu_time = now

    return psu_text

def _availableat_psu(model, dt):
    '''
        _availableat_psu

        Downloads a list of all the BUFKIT profile stations for a given
        model and runtime.

        Parameters
        ----------
        model : string
            A string representing the forecast model requested
        dt : datetime object
            A datetime object that represents the model initalization time.
    '''
    if model == '4km nam': model = 'nam4km'
    _repl = {'gfs':'gfs3', 'nam':'namm?', 'rap':'rap', 'nam4km':'nam4kmm?', 'hrrr':'hrrr', 'sref':'sref'}

    cycle = dt.hour
    url = "%s%s/%02d/" % (psu_base_url, model.upper(), cycle)
    url_obj = urlopen(url, cafile=certifi.where())
    text = url_obj.read().decode('utf-8')

    stns = re.findall("%s_(.+)\.buf" % _repl[model], text)
    return stns

def _available_psu(model, dt=None):
    '''
        _available_psu

        Downloads a list of datetime objects that represents
        the available model times from the PSU server.

        Parameters
        ----------
        model : string
            the name of the forecast model
        nam : boolean (default: false)
            Specifies whether or not this is the NAM or 4km NAM
        off : boolean (default: false)
            Specifies whether or not this is an off-hour run
    '''

    if dt is not None and dt < datetime.utcnow() - timedelta(3600*29): # We know PSU is only a 24 hr service
        return []

    if model == '4km nam': model = 'nam4km'

    psu_text = _download_psu()
    latest = re.search("%s\.([\d]{12})\.done" % model, psu_text).groups(0)[0]
    dt = datetime.strptime(latest, "%Y%m%d%H%M")
    return [ dt ]

### IEM CODE
iem_base_url = "http://mtarchive.geol.iastate.edu/%Y/%m/%d/bufkit/%H/MODEL/"
iem_text = ""
iem_time = None

def _download_iem():
    '''
        _download_iem()

        Downloads the IEM directory webpage that lists all the
        files available.

        Returns
        -------
        iem_text : string
            Lists the files within the IEM site.
    '''
    global iem_time, iem_text
    now = datetime.utcnow()
    if iem_time is None or iem_time < now - cache_len:
        iem_obj = urlopen(iem_base_url, cafile=certifi.where())
        psu_text = url_obj.read().decode('utf-8')
        iem_time = now

    return iem_text

def _availableat_iem(model, dt):
    '''
        _availableat_iem

        Downloads a list of all the BUFKIT profile stations for a given
        model and runtime.

        Parameters
        ----------
        model : string
            A string representing the forecast model requested
        dt : datetime object
            A datetime object that represents the model initalization time.
    '''
    if model == '4km nam' or model == 'nam nest': model = 'nam4km'
    _repl = {'gfs':'gfs3', 'nam':'namm?', 'rap':'rap', 'nam4km':'nam4kmm?', 'hrrr':'hrrr', 'sref':'sref', 'ruc':'ruc'}

    cycle = dt.hour
    url = dt.strftime(iem_base_url).replace("MODEL", model.lower())
    url_obj = urlopen(url, cafile=certifi.where())
    text = url_obj.read().decode('utf-8')

    stns = re.findall("%s_(.+)\.buf\">" % _repl[model], text)

    return stns

def _available_iem(model, dt=None):
    '''
        _available_iem

        Downloads a list of datetime objects that represents
        the available model times from the PSU server.

        Parameters
        ----------
        model : string
            the name of the forecast model
        nam : boolean (default: false)
            Specifies whether or not this is the NAM or 4km NAM
        off : boolean (default: false)
            Specifies whether or not this is an off-hour run
    '''
    #nam=(m in [ 'nam', '4km nam' ])
    if dt is None:
        dt = datetime.utcnow()
    else:
        try:
            a = int(dt.year)
        except:
            dt = datetime(dt.year(), dt.month(), dt.day())

    if model == '4km nam' or model == 'nam nest': model = 'nam4km'

    # Filtering out datetimes where we know there is no data on the IEM server.
    # Either due to no data, depreciated modeling systems, etc.
    if dt < datetime(2010,12,30): # No Bufkit files before this date
        return []
    if dt > datetime.utcnow() - timedelta(seconds=3600*24):
        return []
    if model == 'ruc' and dt > datetime(2012,5,1,11,0,0): # RIP RUC
        return []
    if model == 'nam4km' and dt < datetime(2013,3,25,0,0,0): # No NAM 4 km data before this time
        return []
    if model == 'rap' and dt < datetime(2012,5,1): # No RAP data prior to this date
        return []
    if model == 'hrrr' and dt < datetime(2019,8,24):
        return []

    if model == 'ruc' or model == 'rap':
        if dt.year == 2012 and dt.month == 5 and dt.day == 1: # Need to truncate the times since there was a switchover from RUC to RAP on this day.
            if model == 'ruc':
                start = 0; end = 12;
            elif model == 'rap':
                start = 12; end = 24;
        else:
            start = 0; end = 24;
        inc = 1

    if model == 'gfs' or model == 'nam' or model == 'nam4km':
        start = 0; end = 24; inc = 6

    if model == 'hrrr':
        if dt.year == 2019 and dt.month == 8 and dt.day == 24:
            start = 1
        else:
            start = 0
        end = 24
        inc = 1

    return [datetime(dt.year, dt.month, dt.day, h, 0, 0) for h in np.arange(start,end,inc)]


## PECAN MAPS ENSEMBLE CODE
pecan_base_url = 'http://weather.ou.edu/~map/real_time_data/PECAN/'
#http://weather.ou.edu/~map/real_time_data/PECAN/2015061112/soundings/TOP_2015061113.txt

def _available_oupecan(**kwargs):
    text = urlopen(pecan_base_url, cafile=certifi.where()).read().decode('utf-8')
    matches = sorted(list(set(re.findall("([\d]{10})", text))))
    return [ datetime.strptime(m, "%Y%m%d%H") for m in matches ]

def _availableat_oupecan(dt):
    dt_string = datetime.strftime(dt, '%Y%m%d%H')
    url = "%s%s/soundings/" % (pecan_base_url, dt_string)
    url_obj = urlopen(url, cafile=certifi.where())
    text = url_obj.read().decode('utf-8')
    dt_string = datetime.strftime(dt, '%Y%m%d%H')
    stns = re.findall("([\w]{3})_%s.txt" % dt_string, text)
    return np.unique(stns)

## NCAR ENSEMBLE CODE
ncarens_base_url = 'http://sharp.weather.ou.edu/soundings/ncarens/'

def _available_ncarens(dt=None):
    text = urlopen(ncarens_base_url, cafile=certifi.where()).read().decode('utf-8')

    matches = sorted(list(set(re.findall("([\d]{8}_[\d]{2})", text))))
    return [ datetime.strptime(m, '%Y%m%d_%H') for m in matches ]

def _availableat_ncarens(dt):
    dt_string = datetime.strftime(dt, '%Y%m%d_%H')
    url = "%s%s/" % (ncarens_base_url, dt_string)
    url_obj = urlopen(url, cafile=certifi.where())
    text = url_obj.read().decode('utf-8')

    stns = re.findall("(N[\w]{2}.[\w]{2}W.[\w]{2,3}.[\w]{2}).txt", text)
    stns2 = re.findall("([\w]{3}).txt", text)
    return stns + stns2

def _available_nssl(ens=False):
    path_to_nssl_wrf = ''
    path_to_nssl_wrf_ens = ''

# A dictionary of the available times for profiles from observations, forecast models, NUCAPS, etc.
# JTS - Added the available obs times for the various NUCAPS sources.
available = {
    'psu':{},
    'iem':{},
    'spc':{'observed': lambda dt=None: _available_spc(dt=dt)},
#    'ou_pecan': {'pecan ensemble': lambda dt=None: _available_oupecan(dt=dt) },
#    'ncar_ens': {'ncar ensemble': lambda dt=None: _available_ncarens(dt=dt) },
    'sharp': {'ncar ensemble': lambda dt=None: _available_ncarens(dt=dt), 'observed': lambda dt=None: _available_sharp(dt=dt), 'goes': lambda dt=None: _available_goes(dt=dt)},
    'local': {'local wrf-arw': lambda filename:  _available_local(filename)},
    'stc': {'nucaps conus noaa-20': lambda dt=None: _available_nucaps_conus_j01(dt=dt), \
            'nucaps conus aqua': lambda dt=None: _available_nucaps_conus_aq0(dt=dt), \
            'nucaps conus metop-b': lambda dt=None: _available_nucaps_conus_m01(dt=dt), \
            'nucaps conus metop-a': lambda dt=None: _available_nucaps_conus_m02(dt=dt), \
            'nucaps conus metop-c': lambda dt=None: _available_nucaps_conus_m03(dt=dt), \
            'nucaps caribbean noaa-20': lambda dt=None: _available_nucaps_caribbean_j01(dt=dt), \
            'nucaps alaska noaa-20': lambda dt=None: _available_nucaps_alaska_j01(dt=dt)},
}

# A dictionary containing paths to the stations for different observations, forecast models, etc.
# given a specific datetime object.
availableat = {
    'psu':{},
    'iem':{},
    'spc':{'observed':_availableat_spc},
    'ou_pecan': {'pecan ensemble': lambda dt: _availableat_oupecan(dt)},
    'sharp': {'ncar ensemble': lambda dt: _availableat_ncarens(dt) , 'observed':_availableat_sharp, 'goes':_availableat_goes},
}

# Set the available and available-at-time functions for the PSU data.
for model in [ 'gfs', 'nam', 'rap', 'hrrr', '4km nam', 'sref' ]:
    available['psu'][model] = (lambda m: lambda dt=None: _available_psu(m, dt=dt))(model)
    availableat['psu'][model] = (lambda m: lambda dt: _availableat_psu(m, dt))(model)

# Set the available and available-at-time functions for the IEM data.
for model in [ 'gfs', 'nam', 'rap', 'ruc', 'nam nest','hrrr' ]:
    available['iem'][model] = (lambda m: lambda dt=None: _available_iem(m, dt=dt))(model)
    availableat['iem'][model] = (lambda m: lambda dt: _availableat_iem(m, dt))(model)

if __name__ == "__main__":

    dt = datetime.utcnow()
    dt = available['spc']['observed'](dt)
    print(dt)
    print(availableat['spc']['observed'](dt[-1]))
    ##stop
    dt = datetime(2015,1,1,0,0,0)
    print(dt)
    dt = available['iem']['gfs'](dt)
    stns = availableat['iem']['gfs'](dt[0])
    print(dt, stns)
    #dt = available['spc']['observed']()
    #stns = availableat['spc']['observed'](dt[-1])
    dt = available['ou_pecan']['pecan ensemble']()
    #print(dt)
    #stns = availableat['ou_pecan']['pecan ensemble'](dt[-2])
    #print(stns)
