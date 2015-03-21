
import xml.etree.ElementTree as ET
import glob
from datetime import datetime, timedelta

def loadDataSources(ds_dir='../datasources'):
    files = glob.glob(ds_dir + '/*.xml')
    ds = {}
    for ds_file in files:
        root = ET.parse(ds_file).getroot()
        for src in root:
            name = src.get('name')
            ds[name] = DataSource(src)
    return ds

class Outlet(object):
    def __init__(self, config):
        self._name = config.get('name')
        self._url = config.get('url')
        self._format = config.get('format')
        self._time = config.find('time')
        point_csv = config.find('points')
        self._points = self._loadCSV("../datasources/" + point_csv.get("csv"))

        for idx in xrange(len(self._points)):
            self._points[idx]['lat'] = float(self._points[idx]['lat'])
            self._points[idx]['lon'] = float(self._points[idx]['lon'])
            self._points[idx]['elev'] = int(self._points[idx]['elev'])

    def getForecastHours(self):
        times = []
        t = self._time
        f_range = int(t.get('range'))
        f_delta = int(t.get('delta'))
        if f_delta > 0:
            times.extend(range(0, f_range + f_delta, f_delta))
        else:
            times.append(0)
        return times

    def getCycles(self):
        times = []

        t = self._time
        c_length = int(t.get('cycle'))
        c_offset = int(t.get('offset'))
        return [ t + c_offset for t in range(0, 24, c_length) ]

    def getDelay(self):
        return int(self._time.get('delay'))

    def getArchiveLen(self):
        return int(self._time.get('archive'))

    def getURL(self):
        return self._url

    def hasCycle(self, point, cycle):
        return

    def getPoints(self):
        return [ ( p['lat'], p['lon'], p['icao'], p['name'], p['state'], p['country'] ) for p in self._points ]

    def _loadCSV(self, csv_file_name):
        csv = []
        csv_file = open(csv_file_name, 'r')
        fields = [ f.lower() for f in csv_file.readline().strip().split(',') ]

        for line in csv_file:
            line_dict = dict( (f, v) for f, v in zip(fields, line.split(',')))
            csv.append(line_dict)

        csv_file.close()
        return csv

class DataSource(object):
    def __init__(self, config):
        self._name = config.get('name')
        self._ensemble = config.get('ensemble')
        self._outlets = dict( (c.get('name'), Outlet(c)) for c in config )

    def _get(self, name, outlet, flatten=True):
        prop = None
        if outlet is None:
            prop = []
            for o in self._outlets.itervalues():
                func = getattr(o, name)
                prop.append(func())

            if flatten:
                prop = [ p for plist in prop for p in plist ]
                prop = list(set(prop))
                prop = sorted(prop)
        else:
            func = getattr(self._outlets[outlet], name)
            prop = func()
        return prop

    def getForecastHours(self, outlet=None, flatten=True):
        times = self._get('getForecastHours', outlet, flatten=flatten)
        return times

    def getDailyCycles(self, outlet=None, flatten=True):
        cycles = self._get('getCycles', outlet, flatten=flatten)
        return cycles

    def getDelays(self, outlet=None):
        delays = self._get('getDelay', outlet, flatten=False)
        return delays

    def getArchiveLens(self, outlet=None):
        lens = self._get('getArchiveLen', outlet, flatten=False)
        return lens

    def getMostRecentCycle(self, outlet=None):
        daily = self.getDailyCycles(outlet=outlet, flatten=False)
        delay = self.getDelays(outlet=outlet)
        now = datetime.utcnow()
        cycles = []
        for out_cyc, out_delay in zip(daily, delay):
            avail = [ now.replace(hour=hr, minute=0, second=0, microsecond=0) + timedelta(hours=out_delay) for hr in out_cyc ]
            avail = [ run - timedelta(days=1) if run > now else run for run in avail ]
            cycles.append(max(avail) - timedelta(hours=out_delay))
        return max(cycles)

    def getArchivedCycles(self, outlet=None, max_cycles=100):
        start = self.getMostRecentCycle(outlet=outlet)
        daily_cycles = self.getDailyCycles(outlet=outlet)
        time_counter = daily_cycles.index(start.hour)
        archive_len = max(self.getArchiveLens(outlet=outlet))

        cycles = []
        cur_time = start
        while cur_time >= start - timedelta(hours=archive_len):
            cycles.append(cur_time)

            if len(cycles) >= max_cycles:
                break

            time_counter = (time_counter - 1) % len(daily_cycles)
            cycle = daily_cycles[time_counter]
            cur_time.replace(hour=cycle)
            if cycle == daily_cycles[-1]:
                cur_time -= timedelta(days=1)
        return cycles

    def getURL(self, outlet=None):
        return

    def getPoints(self, outlet=None):
        points = self._get('getPoints', outlet, flatten=True)
        return points

if __name__ == "__main__":
    ds = loadDataSources()

    for n, d in ds.iteritems():
        print n, d.getArchivedCycles()
