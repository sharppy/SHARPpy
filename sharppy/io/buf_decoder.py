import urllib2
import sys
import numpy as np
from datetime import datetime

class BufkitFile(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.dates = []
        self.dates_loaded = False
        self.member_names = []
        self.__readFile()
        self.num_profiles = 0
 
    def parseBUF(self, text):
        data = np.array(text.split('\r\n'))
        data_idxs = []
        new_record = False
        begin_idx = 0
        self.member_names.append(data[0])
        # Figure out the indices for the data chunks
        for i in range(len(data)):
            if "STID" in data[i]:
                # Here is information about the record
                spl = data[i].split()
                self.station = spl[2]
                self.wmo_id = spl[5]
                if self.dates_loaded == False:
                    self.dates.append(datetime.strptime(spl[8], '%y%m%d/%H%M'))
                self.slat = float(data[i+1].split()[2])
                self.slon = float(data[i+1].split()[5])
                self.selv = float(data[i+1].split()[8])
                self.stim = float(data[i+2].split()[2])
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
                    #print data[i]
        
        data_idxs = data_idxs[1:]
        # Make arrays to store the data
        profile_length = len(data[data_idxs[0][0]: data_idxs[0][1]])/2
        numProfiles = len(self.dates)
        hght = np.zeros((numProfiles, profile_length), dtype=float)
        pres = np.zeros((numProfiles, profile_length), dtype=float)
        tmpc = np.zeros((numProfiles, profile_length), dtype=float)
        dwpc = np.zeros((numProfiles, profile_length), dtype=float)
        wdir = np.zeros((numProfiles, profile_length), dtype=float)
        wspd = np.zeros((numProfiles, profile_length), dtype=float)
        omeg = np.zeros((numProfiles, profile_length), dtype=float)
        
        # Parse out the profiles
        for i in range(len(data_idxs)):
            data_stuff = data[data_idxs[i][0]: data_idxs[i][1]]
            for j in np.arange(0, profile_length*2,2):
                if len(data_stuff[j+1].split()) == 1:
                    hght[i,j/2] = float(data_stuff[j+1].split()[0])
                else:
                    hght[i,j/2] = float(data_stuff[j+1].split()[1])
                tmpc[i,j/2] = float(data_stuff[j].split()[1])
                dwpc[i,j/2] = float(data_stuff[j].split()[3])
                pres[i,j/2] = float(data_stuff[j].split()[0])
                wspd[i,j/2] = float(data_stuff[j].split()[6])
                wdir[i,j/2] = float(data_stuff[j].split()[5])
                omeg[i,j/2] = float(data_stuff[j].split()[7])

        self.dates_loaded = True

        return hght, pres, tmpc, dwpc, wdir, wspd, omeg, numProfiles, profile_length

   
    def __readFile(self):
        # Try to open the file.  This is a dirty hack right now until
        # I can figure out a cleaner way to make sure the file (either local or URL)
        # gets opened.
        try:
            f = urllib2.urlopen(self.filename)
        except:
            try:
                f = open(self.filename, 'r')
            except:
                print self.filename + " unable to be opened."
                sys.exit()
        file_data = f.read()
        string = '\r\n\r\n\r\n'
        members = np.array(file_data.split(string))
        members = members[0:len(members)-1]
        self.num_members = len(members)
        self.hght = []
        self.pres = []
        self.tmpc = []
        self.dwpc = []
        self.wdir = []
        self.wspd = []
        self.omeg = []
        self.numProfiles = None
        self.profile_length = None
        for n, i in enumerate(members):
            hght, pres, tmpc, dwpc, wdir, wspd, omeg, numProfiles, profile_length = self.parseBUF(i)
            self.hght.append(hght)
            self.pres.append(pres)
            self.tmpc.append(tmpc)
            self.dwpc.append(dwpc)
            self.wdir.append(wdir)
            self.wspd.append(wspd)
            self.omeg.append(omeg)
            self.numProfiles = numProfiles
            self.profile_length = profile_length

        self.hght = np.asarray(self.hght)
        self.pres = np.asarray(self.pres)
        self.tmpc = np.asarray(self.tmpc)
        self.dwpc = np.asarray(self.dwpc)
        self.wdir = np.asarray(self.wdir)
        self.wspd = np.asarray(self.wspd)
        self.omeg = np.asarray(self.omeg)

    def getNumMembers(self):
        return self.num_members

    def getNumProfiles(self):
        return self.numProfiles
    
    def getProfileLength(self):
        return self.profile_length

    def getMemberNames(self):
        return self.member_names

