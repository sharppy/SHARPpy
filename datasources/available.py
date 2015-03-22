
import urllib2
import re
from datetime import datetime, timedelta

def _available_spc_observed():
    available_url = "http://www.spc.noaa.gov/exper/soundings/"
    text = urllib2.urlopen(available_url).read()
    matches = sorted(list(set(re.findall("[\d]{8}_OBS", text))))
    recent_synop = [ m for m in matches if m[6:8] in ["00", "12"] ][-1]

    recent_url = "%s%s/" % (available_url, recent_synop)
    text = urllib2.urlopen(recent_url).read()
    matches = re.findall("alt=\"([\w]{3}|[\d]{5})\"", text)

    lats, lons, stns, names = [], [], [], []
    for line in open("ua_stations.csv"):
        data = line.split(",")
        if data[2][1:] in matches or data[2] in matches:
            if data[2][1:] in matches: 
                stns.append(data[2][1:])
            else:   
                stns.append(data[2])

            lats.append(float(data[3]))
            lons.append(float(data[4]))
            names.append(data[1].title() + ', ' + data[0].upper() + ' (' + data[2] + ')')
            names[-1] = names[-1].replace('Afb', 'AFB')
    return matches, stns

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

def _available_psu(model):
    psu_text = _download_psu()
    latest = re.search("%s\.([\d]{12})\.done" % model, psu_text).groups(0)[0]
    dt = datetime.strptime(latest, "%Y%m%d%H%M")
    return dt

available = {
    'psu':{}, 
    'spc':{},
}

availableat = {
    'psu':{},
    'spc':{},
}

for model in [ 'gfs', 'nam', 'rap', 'hrrr', 'nam4km', 'sref' ]:
    available['psu'][model] = lambda: _available_psu(model)
    availableat['psu'][model] = lambda dt: _availableat_psu(model, dt)

if __name__ == "__main__":
    dt = available['psu']['gfs']()
    stns = availableat['psu']['gfs'](dt)
