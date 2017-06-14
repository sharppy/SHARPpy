
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from decoder import Decoder

from datetime import datetime
from urlparse import urlparse
from os.path import split
from cStringIO import StringIO
from zipfile import ZipFile, BadZipfile

__fmtname__ = "bufkit"
__classname__ = "BufDecoder"

__first_guess_models__ = {'gfs3': 'GFS', 'nam': 'NAM', 'namm': 'NAM', 'rap': 'RAP', 'hrrr':'HRRR', 'sref': 'SREF', \
                          'nam4km': '4km NAM', 'nam4kmm': '4km NAM', 'arw': 'ARW', 'nmb': 'NMB', 'hiresw': 'HiResW'}

class BufDecoder(Decoder):
    def __init__(self, file_name):
        super(BufDecoder, self).__init__(file_name)

    def _getBaseFile(self):
        return split(urlparse(self._file_name).path)[1]

    def _parse(self):
        file_data = self._downloadFile()

        if self._file_name.find('buz') > -1:
            data_io = StringIO(file_data)
            buz_file = ZipFile(data_io, mode='r')
            buf_file = buz_file.open(buz_file.filelist[0].filename, mode='r')
            file_data = buf_file.read()
            buf_file.close()
            buz_file.close()
            data_io.close()

        string = '\r\n\r\n\r\n'
        members = np.array(file_data.split(string))
        members = members[0:len(members)-1]
        num_members = len(members)
        profiles = {}
        dates = None
        mean_member = None
        location = None        

        for n, mem_txt in enumerate(members):
            mem_name, mem_profs, mem_dates = self._parseMember(mem_txt)
            profiles[mem_name] = mem_profs
            dates = mem_dates

            if mean_member is None:
                mean_member = mem_name
            if location is None:
                location = mem_profs[0].location

        prof_coll = prof_collection.ProfCollection(profiles, dates)
        
        if self._getBaseFile().split('_')[0].lower() in __first_guess_models__:
            prof_coll.setMeta('model', __first_guess_models__[self._getBaseFile().split('_')[0].lower()])
        else:
            prof_coll.setMeta('model', '')

        prof_coll.setMeta('observed', False)
        prof_coll.setMeta('loc', location)
        prof_coll.setMeta('runs', dates[0].hour)
        prof_coll.setHighlightedMember(mean_member)
        prof_coll.setMeta('loc', profiles[mean_member][0].location)
        return prof_coll

    def _parseMember(self, text):
        data = np.array(text.split('\r\n'))
        data_idxs = []
        new_record = False
        begin_idx = 0
        member_name = data[0]
        dates = []
        # Figure out the indices for the data chunks
        for i in range(len(data)):
            if "STID" in data[i]:
                # Here is information about the record
                spl = data[i].split()

                if spl[2].strip() == "STNM":
                    station = "" # The bufkit file has a blank space for the station name
                    wmo_id = spl[4]
                    dates.append(datetime.strptime(spl[7], '%y%m%d/%H%M'))
                else:
                    station = spl[2]
                    wmo_id = spl[5]
                    dates.append(datetime.strptime(spl[8], '%y%m%d/%H%M'))

                slat = float(data[i+1].split()[2])
                slon = float(data[i+1].split()[5])
                selv = float(data[i+1].split()[8])
                stim = float(data[i+2].split()[2])

            if data[i].find('HGHT') >= 0 and new_record == False:
                # we've found a new data chunk
                new_record = True
                begin_idx = i+1
            elif 'STID' in data[i] and new_record == True:
                # We've found the end of the data chunk
                new_record = False
                data_idxs.append((begin_idx, i-1))
            elif 'STN' in data[i] and new_record == True:
                # We've found the end of the last data chunk of the file
                new_record = False
                data_idxs.append((begin_idx, i))
            elif new_record == True:
                continue
                    ##print data[i]
        
        data_idxs = data_idxs[1:]
        # Make arrays to store the data
        profiles = []        

        # Parse out the profiles
        for i in range(len(data_idxs)):
            data_stuff = data[data_idxs[i][0]: data_idxs[i][1]]
            profile_length = len(data[data_idxs[i][0]: data_idxs[i][1]])/2

            hght = np.zeros((profile_length,), dtype=float)
            pres = np.zeros((profile_length,), dtype=float)
            tmpc = np.zeros((profile_length,), dtype=float)
            dwpc = np.zeros((profile_length,), dtype=float)
            wdir = np.zeros((profile_length,), dtype=float)
            wspd = np.zeros((profile_length,), dtype=float)
            omeg = np.zeros((profile_length,), dtype=float)

            for j in np.arange(0, profile_length * 2, 2):
                if len(data_stuff[j+1].split()) == 1:
                    hght[j / 2] = float(data_stuff[j+1].split()[0])
                else:
                    hght[j / 2] = float(data_stuff[j+1].split()[1])
                tmpc[j / 2] = float(data_stuff[j].split()[1])
                dwpc[j / 2] = float(data_stuff[j].split()[3])
                pres[j / 2] = float(data_stuff[j].split()[0])
                wspd[j / 2] = float(data_stuff[j].split()[6])
                wdir[j / 2] = float(data_stuff[j].split()[5])
                omeg[j / 2] = float(data_stuff[j].split()[7])

            prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc, 
                wdir=wdir, wspd=wspd, omeg=omeg, location=station, date=dates[i], latitude=slat)

            profiles.append(prof)

        return member_name, profiles, dates
