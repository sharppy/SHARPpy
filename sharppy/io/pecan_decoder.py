import numpy as np
import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from datetime import datetime
from sharppy.io.decoder import Decoder
from StringIO import StringIO

__fmtname__ = "pecan"
__classname__ = "PECANDecoder"

class PECANDecoder(Decoder):
    def __init__(self, file_name):
        super(PECANDecoder, self).__init__(file_name)

    def _parse(self):
        file_data = self._downloadFile()

        file_profiles = file_data.split('\n\n\n')

        profiles = {}
        dates = []
        for m in file_profiles:
            try:
                prof, dt_obj, member = self._parseSection(m)
            except:
                continue

            # Try to add the profile object to the list of profiles for this member
            try:
                profiles[member] = profiles[member] + [prof]
            except Exception,e:
                profiles[member] = [prof]
            dates.append(dt_obj)

        prof_coll = prof_collection.ProfCollection(profiles, dates)
        prof_coll.setMeta('observed', False)
        prof_coll.setMeta('base_time', dates[0])
        return prof_coll

    def _parseSection(self, section):
        parts = section.split('\n')
        dt_obj = datetime.strptime(parts[1], 'TIME = %y%m%d/%H%M')
        member = parts[0].split('=')[-1].strip()
        location = parts[2].split('SLAT')[0].split('=')[-1].strip()
        data = '\n'.join(parts[5:])
        sound_data = StringIO( data )
        p, h, t, td, wdir, wspd, omeg = np.genfromtxt( sound_data, delimiter=',', unpack=True)

        prof = profile.create_profile(profile='raw', pres=p[1:], hght=h[1:], tmpc=t[1:], dwpc=td[1:], wspd=wspd[1:],\
                                      wdir=wdir[1:], omeg=omeg[1:], location=location, date=dt_obj, missing=-999.0)
        return prof, dt_obj, member

if __name__ == '__main__':
	file = PECANDecoder("http://arctic.som.ou.edu/OUN.txt")
	print file.getProfileTimes()
