
import xml.etree.ElementTree as ET
import glob, os, sys, shutil
from datetime import datetime, timedelta
try:
    from urllib2 import urlopen, URLError
    from urllib import quote
    from urlparse import urlparse, urlunsplit
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError
    from urllib.parse import quote, urlparse, urlunsplit

import certifi
import platform, subprocess, re
import imp
import socket
import logging
import traceback

import sharppy.io.decoder as decoder
from sharppy.io.csv import loadCSV
from sharppy.io.csv import loadNUCAPS_CSV

import sutils.frozenutils as frozenutils

HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy", "datasources")
NUCAPS_times_file = os.path.join(HOME_DIR, "nucapsTimes.txt") # JTS

# Cleanup; Remove nucapsTimes.txt and cloudTopValues.txt when main GUI opens.
if os.path.isfile(NUCAPS_times_file):
    os.remove(NUCAPS_times_file)

if not os.path.exists(HOME_DIR):
    os.makedirs(HOME_DIR)

if frozenutils.isFrozen():
    from . import available
else:
    avail_loc = os.path.join(HOME_DIR, 'available.py')
    if not os.path.exists(avail_loc):
        pkg_avail_loc = os.path.join(os.path.dirname(__file__), 'available.py')
        shutil.copy(pkg_avail_loc, avail_loc)

    available = imp.load_source('available', avail_loc)

# TAS: Comment this file and available.py

class DataSourceError(Exception):
    pass

def loadDataSources(ds_dir=HOME_DIR):
    """
    Load the data source information from the XML files.
    Returns a dictionary associating data source names to DataSource objects.
    """

    files = glob.glob(os.path.join(ds_dir, '*.xml'))
    if len(files) == 0:
        if frozenutils.isFrozen():
            frozen_path = frozenutils.frozenPath()
            files = glob.glob(os.path.join(frozen_path, 'sharppy', 'datasources', '*.xml')) +  \
                    glob.glob(os.path.join(frozen_path, 'sharppy', 'datasources', '*.csv'))
        else:
            pkg_path = os.path.dirname(__file__)
            files = glob.glob(os.path.join(pkg_path, '*.xml')) + glob.glob(os.path.join(pkg_path, '*.csv'))

        for file_name in files:
            shutil.copy(file_name, ds_dir)

    files = glob.glob(os.path.join(ds_dir, '*.xml'))
    ds = {}
    for ds_file in files:
        root = ET.parse(ds_file).getroot()
        for src in root:
            name = src.get('name')
            try:
                ds[name] = DataSource(src)
            except Exception as e:
                traceback.print_exc()
                print("Exception: ", e)
                print('Unable to process %s file'%os.path.basename(ds_file))
                print("This data source may not be loaded then.")
    return ds

def _pingURL(hostname, timeout=1):
    try:
        urlopen(hostname, timeout=timeout, cafile=certifi.where())
    except URLError:
        return False
    except socket.timeout as e:
        return False

    return True

def pingURLs(ds_dict):
    """
    Try to ping all the URLs in any XML file.
    Takes a dictionary associating data source names to DataSource objects.
    Returns a dictionary associating URLs with a boolean specifying whether or not they were reachable.
    """
    urls = {}

    for ds in list(ds_dict.values()):
        ds_urls = ds.getURLList()
        for url in ds_urls:
            urlp = urlparse(url)
            base_url = urlunsplit((urlp.scheme, urlp.netloc, '', '', ''))
            urls[base_url] = None

    for url in urls.keys():
        urls[url] = _pingURL(url)

        if urls[url]:
            # A bit of a hack. Since we're only using this to check for an Internet connection, we don't need to check
            # any more if we find one.
            break
    return urls

class Outlet(object):
    """
    An Outlet object contains all the information for a data outlet (for example, the observed
    sounding feed from SPC, which is distinct from the observed sounding feed from, say, Europe).
    """
    def __init__(self, ds_name, config):
        self._ds_name = ds_name
        self._name = config.get('name')
        self._url = config.get('url')
        self._format = config.get('format')
        self._time = config.find('time')
        point_csv = config.find('points')
        #self.start, self.end = self.getTimeSpan()

        # JTS - Parse remote CSVs from FTP site for NUCAPS data sources.
        # Read the NUCAPS data source, region, satellite ID, year, month, day and time info
        # from the temporary file and assign to local variables.
        if os.path.isfile(NUCAPS_times_file):
            file = open(NUCAPS_times_file)
            line = file.readlines()

            # Remove the list surrounding the values.
            line = line[0]
            selected_ds = str(line.split(',')[0])

            # If data source in xml matches selected data source, then grab the associated remote csv file.
            if self._ds_name == selected_ds:
                region = str(line.split(',')[1])
                satID = str(line.split(',')[2])
                YEAR = str(line.split(',')[3])
                MONTH = str(line.split(',')[4])
                DAY = str(line.split(',')[5])
                TIME = str(line.split(',')[6])

                remote_csv = f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/{region}/sharppy/{satID}/csv/{YEAR}{MONTH}{DAY}{TIME}/{satID}_{region}.csv'
                self._csv_fields, self._points = loadNUCAPS_CSV(remote_csv)
            else:
                # Do nothing if data source name in xml does not match the selected data source.
                self._csv_fields, self._points = loadCSV(os.path.join(HOME_DIR, point_csv.get("csv")))
        else:
            # Parse local CSVs stored in ~/.sharppy/datasources for non-NUCAPS data sources.
            self._csv_fields, self._points = loadCSV(os.path.join(HOME_DIR, point_csv.get("csv")))

        for idx in range(len(self._points)):
            self._points[idx]['lat'] = float(self._points[idx]['lat'])
            self._points[idx]['lon'] = float(self._points[idx]['lon'])
            self._points[idx]['elev'] = int(self._points[idx]['elev'])

        self._custom_avail = self._name.lower() in available.available and self._ds_name.lower() in available.available[self._name.lower()]
        self._is_available = True

    def getTimeSpan(self):
        """
        Read in the XML data to determine the dates/times this outlet spans across
        """
        try:
            start = self._time.get('start')
        except:
            start = '-'
        try:
            end = self._time.get('end')
        except:
            end = '-'
        if start == "-" or start is None:
            s = None
        elif start == "now":
            s = datetime.utcnow()
        else:
            s = datetime.strptime(start, '%Y/%m/%d')

        if end == "-" or end is None:
            e = None
        elif end == 'now':
            e = datetime.utcnow()
        else:
            e = datetime.strptime(end, '%Y/%m/%d')
        return [s, e]

    def getForecastHours(self):
        """
        Return a list of forecast hours that this outlet serves. If the 'delta' attribute is set to 0,
        then the data source only has the 0-hour.
        """
        times = []
        t = self._time
        f_start = int(t.get('first'))
        f_range = int(t.get('range'))
        f_delta = int(t.get('delta'))
        if f_delta > 0:
            times.extend(list(range(f_start, f_range + f_delta, f_delta)))
        else:
            times.append(0)
        return times

    def getCycles(self):
        """
        Return a list of data cycles that this outlet serves.
        """
        times = []

        t = self._time
        c_length = int(t.get('cycle'))
        c_offset = int(t.get('offset'))
        return [ t + c_offset for t in range(0, 24, c_length) ]

    def getDelay(self):
        return int(self._time.get('delay'))

    def getMostRecentCycle(self, dt=None):
        custom_failed = False

        if self._custom_avail:
            try:
                try:
                    times = available.available[self._name.lower()][self._ds_name.lower()](dt)
                except TypeError:
                    times = available.available[self._name.lower()][self._ds_name.lower()]()
                recent = max(times)
                self._is_available = True
            except URLError:
                custom_failed = True
                self._is_available = False

        if not self._custom_avail or custom_failed:
            now = datetime.utcnow()
            cycles = self.getCycles()
            delay = self.getDelay()
            avail = [ now.replace(hour=hr, minute=0, second=0, microsecond=0) + timedelta(hours=delay) for hr in cycles ]
            avail = [ run - timedelta(days=1) if run > now else run for run in avail ]
            recent = max(avail) - timedelta(hours=delay)
        return recent

    def getArchivedCycles(self, **kwargs):
        max_cycles = kwargs.get('max_cycles', 100)

        start = kwargs.get('start', None)
        if start is None:
            start = self.getMostRecentCycle()

        daily_cycles = self.getCycles()
        time_counter = daily_cycles.index(start.hour)
        archive_len = self.getArchiveLen()
        # TODO: Potentially include the option to specify the beginning date of the archive, if the data source
        # is static?

        cycles = []
        cur_time = start
        while cur_time > start - timedelta(hours=archive_len):
            cycles.append(cur_time)

            if len(cycles) >= max_cycles:
                break

            time_counter = (time_counter - 1) % len(daily_cycles)
            cycle = daily_cycles[time_counter]
            cur_time = cur_time.replace(hour=cycle)
            if cycle == daily_cycles[-1]:
                cur_time -= timedelta(days=1)
        return cycles

    def getAvailableAtTime(self, **kwargs):
        dt = kwargs.get('dt', None)

        logging.debug("Calling getAvailableAtTime()" + str(dt) + " " + self._ds_name.lower() + " " + self._name.lower())
        if dt is None:
            dt = self.getMostRecentCycle(dt)
        elif dt == datetime(1700,1,1,0,0,0):
            return []
        stns_avail = self.getPoints()
        if self._name.lower() in available.availableat and self._ds_name.lower() in available.availableat[self._name.lower()]:
            #avail = available.availableat[self._name.lower()][self._ds_name.lower()](dt)
            try:
                avail = available.availableat[self._name.lower()][self._ds_name.lower()](dt)
                stns_avail = []
                points = self.getPoints()
                srcids = [ p['srcid'] for p in points ]
                for stn in avail:
                    try:
                        idx = srcids.index(stn)
                        stns_avail.append(points[idx])
                    except ValueError:
                        pass

                self._is_available = True

            except URLError as err:
                logging.exception(err)
                stns_avail = []
                self._is_available = False
        logging.debug("_is_available: "+ str(self._is_available))
        logging.debug('Number of stations found:' + str(len(stns_avail)))
        return stns_avail

    def getAvailableTimes(self, max_cycles=100, **kwargs):
        # THIS IS WHERE I COULD POTENTIALLY PASS AN ARGUMENT TO FILTER OUT WHAT RAOBS OR MODELS ARE AVAILABLE
        custom_failed = False
        dt = kwargs.get('dt', None) #Used to help search for times
        logging.debug("Called outlet.getAvailableTimes():" + " dt=" + str(dt) + " self._name=" + str(self._name) + " self._ds_name=" + str(self._ds_name))
        if self._custom_avail:
            try:
                if self._name.lower() == "local":
                    times = available.available[self._name.lower()][self._ds_name.lower()](kwargs.get("filename"))
                else:
                    try:
                        times = available.available[self._name.lower()][self._ds_name.lower()](dt)
                    except TypeError:
                        times = available.available[self._name.lower()][self._ds_name.lower()]()
                if len(times) == 1:
                    times = self.getArchivedCycles(start=times[0], max_cycles=max_cycles)
                self._is_available = True
            except URLError as err:
                logging.exception(err)
                custom_failed = True
                self._is_available = False

        if not self._custom_avail or custom_failed:
            times = self.getArchivedCycles(max_cycles=max_cycles)
        logging.debug("outlet.getAvailableTimes() times Found:" + str(times[~max_cycles:]))
        return times[-max_cycles:]

    def getArchiveLen(self):
        return int(self._time.get('archive'))

    def getURL(self):
        return self._url

    def getDecoder(self):
        return decoder.getDecoder(self._format)

    def hasProfile(self, point, cycle):
        logging.debug("Calling outlet.hasProfile() ")
        times = self.getAvailableTimes(dt=cycle)
        has_prof = cycle in times

        if has_prof:
            stns = self.getAvailableAtTime(dt=cycle)
            if point['icao'] != '':
                has_prof = point['icao'] in [ s['icao'] for s in stns ]
            elif point['iata'] != '':
                has_prof = point['iata'] in [ s['iata'] for s in stns ]
            else:
                has_prof = point['synop'] in [ s['synop'] for s in stns ]
        return has_prof

    def getPoints(self):
        points = self._points
        return points

    def getFields(self):
        return self._csv_fields

    def isAvailable(self):
        return self._is_available


class DataSource(object):
    def __init__(self, config):
        self._name = config.get('name')
        self._ensemble = config.get('ensemble').lower() == "true"
        self._observed = config.get('observed').lower() == "true"
        self._outlets = dict( (c.get('name'), Outlet(self._name, c)) for c in config )

    def _get(self, name, outlet_num=None, flatten=True, **kwargs):
        prop = None
        if outlet_num is None:
            prop = []
            for o in self._outlets.values():
                func = getattr(o, name)
                prop.append(func(**kwargs))

            if flatten:
                prop = [ p for plist in prop for p in plist ]
                prop = list(set(prop))
                prop = sorted(prop)
        else:
            func = getattr(list(self._outlets.values())[outlet_num], name)
            prop = func()
        return prop

    def _getOutletWithProfile(self, stn, cycle_dt, outlet_num=0):
        logging.debug("_getOutletWithProfile: " + str(stn) + ' ' + str(cycle_dt))
        use_outlets = [ out for out, cfg in self._outlets.items() if cfg.hasProfile(stn, cycle_dt) ]
        try:
            outlet = use_outlets[outlet_num]
        except IndexError:
            raise DataSourceError()
        return outlet

    def updateTimeSpan(self):
        outlets = [ self._outlets[key].getTimeSpan() for key in self._outlets.keys() ]
        return outlets

    def getForecastHours(self, outlet_num=None, flatten=True):
        times = self._get('getForecastHours', outlet_num=outlet_num, flatten=flatten)
        return times

    def getDailyCycles(self, outlet_num=None, flatten=True):
        cycles = self._get('getCycles', outlet_num=outlet_num, flatten=flatten)
        return cycles

    def getDelays(self, outlet_num=None):
        delays = self._get('getDelay', outlet, flatten=False)
        return delays

    def getArchiveLens(self, outlet_num=None):
        lens = self._get('getArchiveLen', outlet_num=outlet_num, flatten=False)
        return lens

    def getMostRecentCycle(self, outlet_num=None):
        cycles = self._get('getMostRecentCycle', outlet_num=outlet_num, flatten=False)
        return max(cycles)

    def getAvailableTimes(self, filename=None, outlet_num=None, max_cycles=100, dt=None):
        logging.debug("data_source.getAvailableTimes() filename="+str(filename)+' outlet_num=' +str(outlet_num) + ' dt=' + str(dt))
        cycles = self._get('getAvailableTimes', outlet_num=outlet_num, filename=filename, max_cycles=max_cycles, dt=dt)
        return cycles[-max_cycles:]

    def getAvailableAtTime(self, dt, outlet_num=None):
        points = self._get('getAvailableAtTime', outlet_num=outlet_num, flatten=False, dt=dt)

        flatten_pts = []
        flatten_coords = []
        for pt_list in points:
            for pt in pt_list:
                if (pt['lat'], pt['lon']) not in flatten_coords:
                    flatten_coords.append((pt['lat'], pt['lon']))
                    flatten_pts.append(pt)
        return flatten_pts

    def getDecoder(self, stn, cycle_dt, outlet_num=0):
        outlet = self._getOutletWithProfile(stn, cycle_dt, outlet_num=outlet_num)
        decoder = self._outlets[outlet].getDecoder()
        return decoder

    def getURL(self, stn, cycle_dt, outlet_num=0, outlet=None):
        if outlet is None:
            outlet = self._getOutletWithProfile(stn, cycle_dt, outlet_num=outlet_num)
        url_base = self._outlets[outlet].getURL()
        logging.debug("URL: " + url_base)

        # JTS - Format the URL differently for NUCAPS.
        if self._name == 'NUCAPS CONUS NOAA-20' \
            or self._name == 'NUCAPS CONUS Aqua' \
            or self._name == 'NUCAPS CONUS MetOp-A' \
            or self._name == 'NUCAPS CONUS MetOp-B' \
            or self._name == 'NUCAPS CONUS MetOp-C' \
            or self._name == 'NUCAPS Caribbean NOAA-20' \
            or self._name == 'NUCAPS Alaska NOAA-20':
            fmt = {
                'srcid':quote(stn['srcid']),
                'cycle':"%02d%02d" % (cycle_dt.hour, cycle_dt.minute),
                'date':cycle_dt.strftime("%y%m%d"),
                'year':cycle_dt.strftime("%Y"),
                'month':cycle_dt.strftime("%m"),
                'day':cycle_dt.strftime("%d")
            }
        else:
            fmt = {
                'srcid':quote(stn['srcid']),
                'cycle':"%02d" % cycle_dt.hour,
                'date':cycle_dt.strftime("%y%m%d"),
                'year':cycle_dt.strftime("%Y"),
                'month':cycle_dt.strftime("%m"),
                'day':cycle_dt.strftime("%d")
            }
        url = url_base.format(**fmt)
        logging.debug("Formatted URL: " + url)
        return url

    def getDecoderAndURL(self, stn, cycle_dt, outlet_num=0):
        logging.debug("Getting the decoder and the URL to the data ...")
        outlet = self._getOutletWithProfile(stn, cycle_dt, outlet_num=outlet_num)
        decoder = self._outlets[outlet].getDecoder()
        url = self.getURL(stn, cycle_dt, outlet_num, outlet=outlet)
        return decoder, url

    def getURLList(self, outlet_num=None):
        return self._get('getURL', outlet_num=outlet_num, flatten=False)

    def getName(self):
        return self._name

    def isEnsemble(self):
        return self._ensemble

    def isObserved(self):
        return self._observed

    def getPoint(self, stn):
        for outlet in self._outlets.items():
            for pnt in outlet[1].getPoints():
                if stn in pnt['icao'] or stn in pnt['iata'] or stn in pnt['srcid']:
                    return pnt

if __name__ == "__main__":
    ds = loadDataSources('./')
    ds = dict( (n, ds[n]) for n in ['Observed', 'GFS', 'HRRR', 'NAM'] )
    print(ds['GFS'].updateTimeSpan())
    print(ds['HRRR'].updateTimeSpan())
#    for n, d in ds.items():
#       print n, d.getMostRecentCycle()
        #times = d.getAvailableTimes()
        #for t in times:
        #    print(n, t, [ s['srcid'] for s in d.getAvailableAtTime(t) ])
