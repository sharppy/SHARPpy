import urllib2
import sys
import numpy as np
from datetime import datetime
from StringIO import StringIO


'''
    SPC/SND Decoders
    Written by Greg Blumberg (OU/CIMMS) and Kelton Halbert (OU)

    This class acts to decode text files formatted like the SPC observed
    sounding files.  This class also will decode the text files dumped out
    by the GEMPAK program SNLIST.

    To use this file, you'll need to initate a SNDFile Object:

    snd_file = SNDFile(<path_to_file>)

    The file passed to the object can either be a URL or local file.

    Here are the attributes that describe the file:

    filename - the filename
    profile_length - the profile size
    location - the location ID

    The SNDFile object will hold these data variables from the file as attributes:

    tmpc - temperature profiles (Celsius)
    dwpc - dewpoint profiles (Celsius)
    pres - pressure profiles (millibar)
    hght - height profiles (meters)
    wspd - wind speed profiles (knots)
    wdir - wind direction profiles (degrees from North)

'''

class SNDFile(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.__readFile()
   
    def __readFile(self):
        # Try to open the file.  This is a dirty hack right now until
        # I can figure out a cleaner way to make sure the file (either local or URL)
        # gets opened.
        try:
            file_data = urllib2.urlopen(self.filename)
        except:
            try:
                file_data = open(self.filename, 'r')
            except:
                print self.filename + " unable to be opened."
                sys.exit()
        ## read in the file
        data = np.array(file_data.read().split('\n'))
        ## necessary index points
        title_idx = np.where( data == '%TITLE%')[0][0]
        start_idx = np.where( data == '%RAW%' )[0] + 1
        finish_idx = np.where( data == '%END%')[0]

        ## create the plot title
        data_header = data[title_idx + 1].split()
        self.location = data_header[0]
        self.time = data_header[1]

        ## put it all together for StringIO
        full_data = '\n'.join(data[start_idx : finish_idx][:])
        sound_data = StringIO( full_data )

        ## read the data into arrays
        p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, delimiter=',', comments="%", unpack=True )
        idx = np.argsort(p)[::-1] # sort by pressure in case the pressure array is off.

        self.pres = p[idx]
        self.hght = h[idx]
        self.tmpc = T[idx]
        self.dwpc = Td[idx]
        self.wspd = wspd[idx]
        self.wdir = wdir[idx]

        self.profile_length = len(self.pres)

    def getProfileLength(self):
        return self.profile_length

    def getLocation(self):
        return self.location

    def getTime(self):
        return self.time

