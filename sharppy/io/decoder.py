
import numpy as np

import sharppy.sharptab.profile as profile

import urllib2
from datetime import datetime
import glob
import os
import imp
import os.path

class abstract(object):
    def __init__(self, func):
        self._func = func
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Function or method '%s' is abstract.  Override it in a subclass!" % self._func.__name__)

# Comment this file

HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy", "decoders")
_decoders = {}

def findDecoders():
    global _decoders

    built_ins = [ 'buf_decoder', 'spc_decoder', 'archive_decoder', 'ibufr_decoder', 'fsl_decoder', 'wmo_decoder' ]
    io = __import__('sharppy.io', globals(), locals(), built_ins, -1)

    for dec in built_ins:
        # Load build-in decoders
        print "Loading decoder '%s'." % dec
        dec_imp = getattr(io, dec)

        dec_name = dec_imp.__classname__
        fmt_name = dec_imp.__fmtname__

        _decoders[fmt_name] = getattr(dec_imp, dec_name)

    custom = glob.glob(os.path.join(HOME_DIR, '*.py'))

    for dec in custom:
        # Find and load custom decoders
        dec_mod_name = os.path.basename(dec)[:-3]
        print "Found custom decoder '%s'." % dec_mod_name
        dec_imp = imp.load_source(dec_mod_name, dec)
        
        dec_name = dec_imp.__classname__
        fmt_name = dec_imp.__fmtname__

        _decoders[fmt_name] = getattr(dec_imp, dec_name)

def getDecoder(dec_name):
    return getDecoders()[dec_name]

def getDecoders():
    if _decoders == {}:
        findDecoders()

    return _decoders

class Decoder(object):
    def __init__(self, file_name):
        self._file_name = file_name
        self._prof_collection = self._parse()

    @abstract
    def _parse(self):
        pass

    def _downloadFile(self):
        # Try to open the file.  This is a dirty hack right now until
        # I can figure out a cleaner way to make sure the file (either local or URL)
        # gets opened.
        try:
            r = urllib2.Request(self._file_name)
            r.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; rv:40.0) Gecko/20100101 Firefox/40.1')
            r.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
            r.add_header('Accept-Language', 'en-US,en;q=0.8')
            r.add_header('Referer', '{0:s}://{1:s}{2:s}'.format(r.get_type(), r.get_host(), os.path.split(r.get_selector())[0]))
            o = urllib2.build_opener()
            f = o.open(r)
        except (ValueError, IOError):
            try:
                f = open(self._file_name, 'rb')
            except IOError:
                raise IOError("File '%s' cannot be found" % self._file_name)
        file_data = f.read()
#       f.close() # Apparently, this multiplies the time this function takes by anywhere from 2 to 6 ... ???
        return file_data

    def getProfiles(self, indexes=None):
        '''
            Returns a list of profile objects generated from the
            file that was read in.

            Parameters
            ----------
            prof_idxs : list (optional)
                A list of indices corresponding to the profiles to be returned.
                Default is to return the full list of profiles

        '''
        prof_col = self._prof_collection
        if indexes is not None:
            prof_col = prof_col.subset(indexes)
        return prof_col

    def getStnId(self):
        return self._prof_collection.getMeta('loc')

if __name__ == "__main__":
    print "Creating bufkit decoder ..."
    bd = BufDecoder()
