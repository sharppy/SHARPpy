
import urllib2
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
        url_obj = urllib2.urlopen(goes_base_url)
        goes_text = url_obj.read()
        goes_time = now

    return goes_text

def _available_goes():
    '''
        _available_sharp()

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
    recent_url = "%s%s/" % (goes_base_url, dt.strftime('%Y%m%d%H/'))
    text = urllib2.urlopen(recent_url).read()
    matches = re.findall("a href=\"(.+).txt\"", text)
    return matches


sharp_base_url = "http://sharp.weather.ou.edu/soundings/obs/"
sharp_text = ""
sharp_time = None

# SHARP OBSERVED AVAILBILITY
def _download_sharp():
    global sharp_time, sharp_text
    now = datetime.utcnow()
    if sharp_time is None or sharp_time < now - cache_len:
        url_obj = urllib2.urlopen(sharp_base_url)
        sharp_text = url_obj.read()
        sharp_time = now

    return sharp_text

def _available_sharp():
    '''
        _available_sharp()

        Gets all of the available sounding times from the SHARP observed site.

        Returns
        -------
        matches : array
            Array of datetime objects that represents all the available times
            of sounding data on the SHARP site.
    '''
    text = _download_sharp()

    matches = sorted(list(set(re.findall("([\d]{10})/", text))))
    return [ datetime.strptime(m, '%Y%m%d%H') for m in matches ]

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
    recent_url = "%s%s/" % (sharp_base_url, dt.strftime('%Y%m%d%H/'))
    text = urllib2.urlopen(recent_url).read()
    matches = re.findall("a href=\"(.+).txt\"", text)
    return matches

# SPC DATA AVAILABLILY
spc_base_url = "http://www.spc.noaa.gov/exper/soundings/"
spc_text = ""
spc_time = None

def _download_spc():
    global spc_time, spc_text
    now = datetime.utcnow()
    if spc_time is None or spc_time < now - cache_len:
        url_obj = urllib2.urlopen(spc_base_url)
        spc_text = url_obj.read()

        spc_time = now

    return spc_text

def _available_spc():
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
    recent_url = "%s%s/" % (spc_base_url, dt.strftime('%y%m%d%H'))
    text = urllib2.urlopen(recent_url).read()
    matches = re.findall("show_soundings\(\"([\w]{3}|[\d]{5})\"\)", text)
    return matches

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
        url_obj = urllib2.urlopen(psu_base_url)
        psu_text = url_obj.read()

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
    url_obj = urllib2.urlopen(url)
    text = url_obj.read()

    stns = re.findall("%s_(.+)\.buf" % _repl[model], text)
    print stns
    return stns

def _available_psu(model, nam=False, off=False):
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
    if model == '4km nam': model = 'nam4km'

    psu_text = _download_psu()
    latest = re.search("%s\.([\d]{12})\.done" % model, psu_text).groups(0)[0]
    dt = datetime.strptime(latest, "%Y%m%d%H%M")

    return [ dt ]

## PECAN MAPS ENSEMBLE CODE
pecan_base_url = 'http://weather.ou.edu/~map/real_time_data/PECAN/'
#http://weather.ou.edu/~map/real_time_data/PECAN/2015061112/soundings/TOP_2015061113.txt

def _available_oupecan():
    text = urllib2.urlopen(pecan_base_url).read()
    matches = sorted(list(set(re.findall("([\d]{10})", text))))
    return [ datetime.strptime(m, "%Y%m%d%H") for m in matches ]

def _availableat_oupecan(dt):
    dt_string = datetime.strftime(dt, '%Y%m%d%H')
    url = "%s%s/soundings/" % (pecan_base_url, dt_string)
    url_obj = urllib2.urlopen(url)
    text = url_obj.read()
    dt_string = datetime.strftime(dt, '%Y%m%d%H')
    stns = re.findall("([\w]{3})_%s.txt" % dt_string, text)
    return np.unique(stns)

## NCAR ENSEMBLE CODE
ncarens_base_url = 'http://sharp.weather.ou.edu/soundings/ncarens/'

def _available_ncarens():
    text = urllib2.urlopen(ncarens_base_url).read()

    matches = sorted(list(set(re.findall("([\d]{8}_[\d]{2})", text))))
    return [ datetime.strptime(m, '%Y%m%d_%H') for m in matches ]

def _availableat_ncarens(dt):
    dt_string = datetime.strftime(dt, '%Y%m%d_%H')
    url = "%s%s/" % (ncarens_base_url, dt_string)
    url_obj = urllib2.urlopen(url)
    text = url_obj.read()

    stns = re.findall("(N[\w]{2}.[\w]{2}W.[\w]{2,3}.[\w]{2}).txt", text)
    stns2 = re.findall("([\w]{3}).txt", text)
    return stns + stns2 

def _available_nssl(ens=False):
    path_to_nssl_wrf = ''
    path_to_nssl_wrf_ens = ''

# A dictionary of the available times for profiles from observations, forecast models, etc.
available = {
    'psu':{}, 
    'spc':{'observed':_available_spc},
    'ou_pecan': {'pecan ensemble': _available_oupecan },
    'ncar_ens': {'ncar ensemble': _available_ncarens },
    'sharp': {'ncar ensemble': _available_ncarens, 'observed':_available_sharp, 'goes':_available_goes },
    'local': {'local wrf-arw': lambda filename:  _available_local(filename)},
}

# A dictionary containing paths to the stations for different observations, forecast models, etc.
# given a specific datetime object.
availableat = {
    'psu':{},
    'spc':{'observed':_availableat_spc},
    'ou_pecan': {'pecan ensemble': lambda dt: _availableat_oupecan(dt) },
    'sharp': {'ncar ensemble': lambda dt: _availableat_ncarens(dt) , 'observed':_availableat_sharp, 'goes':_availableat_goes,},
}

# Set the available and available-at-time functions for the PSU data.
for model in [ 'gfs', 'nam', 'rap', 'hrrr', '4km nam', 'sref' ]:
    available['psu'][model] = (lambda m: lambda: _available_psu(m, nam=(m in [ 'nam', '4km nam' ]), off=False))(model)
    availableat['psu'][model] = (lambda m: lambda dt: _availableat_psu(m, dt))(model)

if __name__ == "__main__":
    dt = available['sharp']['observed']()
    print dt
    print availableat['sharp']['observed'](dt[-1])
    stop
    dt = available['psu']['gfs']()
    stns = availableat['psu']['gfs'](dt[0])
    #dt = available['spc']['observed']()
    #stns = availableat['spc']['observed'](dt[-1])
    dt = available['ou_pecan']['pecan ensemble']()
    print dt
    stns = availableat['ou_pecan']['pecan ensemble'](dt[-2])
    print stns
