
import urllib2
import re
from datetime import datetime, timedelta

spc_base_url = "http://www.spc.noaa.gov/exper/soundings/"

def _available_spc():
    text = urllib2.urlopen(spc_base_url).read()
    matches = sorted(list(set(re.findall("([\d]{8})_OBS", text))))
    return [ datetime.strptime(m, '%y%m%d%H') for m in matches ]

def _availableat_spc(dt):
    recent_url = "%s%s/" % (spc_base_url, dt.strftime('%y%m%d%H_OBS'))
    text = urllib2.urlopen(recent_url).read()
    matches = re.findall("alt=\"([\w]{3}|[\d]{5})\"", text)
    return matches

psu_base_url = "ftp://ftp.meteo.psu.edu/pub/bufkit/"
psu_text = ""
psu_time = None

def _download_psu():
    global psu_time, psu_text
    now = datetime.utcnow()
    if psu_time is None or psu_time < now - timedelta(minutes=5):
        psu_time = now

        url_obj = urllib2.urlopen(psu_base_url)
        psu_text = url_obj.read()
    return psu_text 

def _availableat_psu(model, dt):
    _repl = {'gfs':'gfs3', 'nam':'namm?', 'rap':'rap', 'nam4km':'nam4km', 'hrrr':'hrrr', 'sref':'sref'}

    cycle = dt.hour
    url = "%s%s/%02d/" % (psu_base_url, model.upper(), cycle)
    url_obj = urllib2.urlopen(url)
    text = url_obj.read()
    stns = re.findall("%s_(.+)\.buf" % _repl[model], text)
    return stns

def _available_psu(model, nam=False, off=False):
    psu_text = _download_psu()
    latest = re.search("%s\.([\d]{12})\.done" % model, psu_text).groups(0)[0]
    dt = datetime.strptime(latest, "%Y%m%d%H%M")

    if nam and off and dt.hour in [ 0, 12 ]:
        dt -= timedelta(hours=6)
    if nam and not off and dt.hour in [ 6, 18 ]:
        dt -= timedelta(hours=6)
    return [ dt ]

available = {
    'psu':{}, 
    'psu_off':{
        'nam':lambda: _available_psu('nam', nam=True, off=True),
        'nam4km':lambda: _available_psu('nam4km', nam=True, off=True)
    },
    'spc':{'observed':_available_spc},
}

availableat = {
    'psu':{},
    'psu_off':{
        'nam':lambda dt: _availableat_psu('nam', dt),
        'nam4km':lambda dt: _availableat_psu('nam4km', dt)
    },
    'spc':{'observed':_availableat_spc},
}

for model in [ 'gfs', 'nam', 'rap', 'hrrr', 'nam4km', 'sref' ]:
    available['psu'][model] = (lambda m: lambda: _available_psu(m, nam=(m == 'nam'), off=False))(model)
    availableat['psu'][model] = (lambda m: lambda dt: _availableat_psu(m, dt))(model)

if __name__ == "__main__":
#   dt = available['psu']['gfs']()
#   stns = availableat['psu']['gfs'](dt)
    dt = available['spc']['observed']()
    stns = availableat['spc']['observed'](dt[-1])
