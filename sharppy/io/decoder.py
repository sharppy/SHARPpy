
import numpy as np

import sharppy.sharptab.profile as profile

import urllib2
from datetime import datetime

class abstract(object):
    def __init__(self, func):
        self._func = func
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Function or method '%s' is abstract.  Override it in a subclass!" % self._func.__name__)

# Comment this file
# Move inherited decoders to ~/.sharppy/decoders
# Write function to figure out what custom decoders we have

class Decoder(object):
    def __init__(self, file_name):
        self._prof_collection = self._parse(file_name)

    @abstract
    def _parse(self):
        pass

    def _downloadFile(self, file_name):
        # Try to open the file.  This is a dirty hack right now until
        # I can figure out a cleaner way to make sure the file (either local or URL)
        # gets opened.
        try:
            f = urllib2.urlopen(file_name)
        except (ValueError, IOError):
            try:
                f = open(file_name, 'r')
            except IOError:
                raise IOError("File '%s' cannot be found" % file_name)
        file_data = f.read()
#       f.close() # Apparently, this multiplies the time this function takes by anywhere from 2 to 6 ... ???
        return file_data

    def getProfiles(self, indexes=[0]):
        '''
            Returns a list of profile objects generated from the
            file that was read in.

            Parameters
            ----------
            prof_idxs : list (optional)
                A list of indices corresponding to the profiles to be returned.
                Default is [0]

        '''
        return self._prof_collection.subset(indexes)

    def getStnId(self):
        return self._prof_collection.getMeta('stn')

if __name__ == "__main__":
    print "Creating bufkit decoder ..."
    bd = BufDecoder()
