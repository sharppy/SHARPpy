
import numpy as np

import sharppy.sharptab.profile as profile

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
        f.close()
        return file_data

    def getProfiles(self, prof_idxs=[0], prog=None):
        profiles = []
        mean_idx = 0
        for idx, (mem_name, mem_profs) in enumerate(self._profiles.iteritems()):
            profs = []
            nprofs = len(mem_profs) if prof_idxs is None else len(prof_idxs)

            for pidx, prof_idx in enumerate(prof_idxs):
                if 'mean' in mem_name.lower() or len(self._profiles) == 1:
                    mean_idx = idx
                    if prog is not None:
                        prog.emit(pidx, nprofs)
                    profs.append(profile.ConvectiveProfile.copy(mem_profs[prof_idx]))
                else:
                    profs.append(profile.BasicProfile.copy(mem_profs[prof_idx]))

            profiles.append(profs)

        mean = profiles[mean_idx]
        profiles = [ mean ] + profiles[:mean_idx] + profiles[(mean_idx + 1):]

        if len(profiles) > 1:
            profiles = [ list(p) for p in zip(*profiles) ]
        else:
            profiles = profiles[0]

        return profiles

    def getProfileTimes(self, prof_idxs=None):
        if prof_idxs is None:
            dates = self._dates
        else:
            dates = [ self._dates[i] for i in prof_idxs ]
        return dates

    def getStnId(self):
        return self._profiles.values()[0][0].location

if __name__ == "__main__":
    print "Creating bufkit decoder ..."
    bd = BufDecoder()
