import numpy as np
import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from datetime import datetime
from sharppy.io.decoder import Decoder

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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
        loc = None
        for m in file_profiles:
            try:
                prof, dt_obj, member = self._parseSection(m)
            except:
                continue

            loc = prof.location
            # Try to add the profile object to the list of profiles for this member
            try:
                profiles[member] = profiles[member] + [prof]
            except Exception as e:
                profiles[member] = [prof]
            if not dt_obj in dates:
                dates.append(dt_obj)
        prof_coll = prof_collection.ProfCollection(profiles, dates)
        if "MEAN" in list(profiles.keys()):
            prof_coll.setHighlightedMember("MEAN")
        prof_coll.setMeta('observed', False)
        prof_coll.setMeta('base_time', dates[0])
        prof_coll.setMeta('loc', loc)
        return prof_coll

    def _parseSection(self, section):
        parts = section.split('\n')
        dt_obj = datetime.strptime(parts[1], 'TIME = %y%m%d/%H%M')
        member = parts[0].split('=')[-1].strip()
        location = parts[2].split('SLAT')[0].split('=')[-1].strip()
        headers = [ h.lower() for h in parts[4].split(", ") ]
        data = '\n'.join(parts[5:])
        sound_data = StringIO( data )

        prof_vars = np.genfromtxt( sound_data, delimiter=',', unpack=True)
        prof_var_dict = dict(zip(headers, prof_vars))

        def maybe_replace(old_var, new_var):
            if old_var in prof_var_dict:
                prof_var_dict[new_var] = prof_var_dict[old_var]
                del prof_var_dict[old_var]

        maybe_replace('omga', 'omeg')
        maybe_replace('temp', 'tmpc')
        maybe_replace('dewp', 'dewp')

        prof = profile.create_profile(profile='raw', location=location, date=dt_obj, missing=-999.0, **prof_var_dict)
        return prof, dt_obj, member

if __name__ == '__main__':
	file = PECANDecoder("http://arctic.som.ou.edu/OUN.txt")
	print(file.getProfileTimes())
