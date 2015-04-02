
import numpy as np

from sharppy.sharptab.profile import create_profile, ConvectiveProfile

import urllib2
from datetime import datetime

class abstract(object):
    def __init__(self, func):
        self._func = func
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Function or method '%s' is abstract.  Override it in a subclass!" % self._func.__name__)

class Decoder(object):
    def __init__(self, file_name):
        self._profiles, self._dates = self._parse(file_name)

    @abstract
    def _parse(self):
        pass

    def getProfiles(self, prof_idxs, prog):
        profiles = []
        mean_idx = None
        for idx, (mem_name, mem_profs) in enumerate(self._profiles.iteritems()):
            if 'mean' in mem_name.lower() or len(self._profiles) == 1:
                mean_idx = idx
                profs = []
                for idx, prof in enumerate(mem_profs):
                    if idx in prof_idxs:
                        profs.append(ConvectiveProfile.copy(prof))
                        prog.emit()
            else:
                profs = [ mem_profs[i] for i in prof_idxs ]

            profiles.append(profs)

        mean = profiles[mean_idx]
        profiles = [ mean ] + profiles[:mean_idx] + profiles[(mean_idx + 1):]

        if len(profiles) > 1:
            profiles = [ list(p) for p in zip(*profiles) ]
        else:
            profiles = profiles[0]

        return profiles

    def getProfileTimes(self, prof_idxs):
        return [ self._dates[i] for i in prof_idxs ]

    def getStnId(self):
        return self._profiles.values()[0][0].location

class BufDecoder(Decoder):
    def __init__(self, file_name):
        super(BufDecoder, self).__init__(file_name)

    def _parse(self, file_name):
        try:
            f = urllib2.urlopen(file_name)
        except IOError:
            try:
                f = open(file_name, 'r')
            except IOError:
                raise IOError("File '%s' cannot be found" % file_name)

        file_data = f.read()
        string = '\r\n\r\n\r\n'
        members = np.array(file_data.split(string))
        members = members[0:len(members)-1]
        num_members = len(members)
        profiles = {}
        dates = None

        for n, mem_txt in enumerate(members):
            mem_name, mem_profs, mem_dates = self._parseMember(mem_txt)
            profiles[mem_name] = mem_profs
            dates = mem_dates
        #f.close()
        return profiles, dates

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

            prof = create_profile(profile='default', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc, 
                wdir=wdir, wspd=wspd, omeg=omeg, location=station)

            profiles.append(prof)

        return member_name, profiles, dates

if __name__ == "__main__":
    print "Creating bufkit decoder ..."
    bd = BufDecoder()
