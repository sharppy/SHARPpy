import numpy as np
import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from datetime import datetime, timedelta
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
        print("Found", len(file_profiles), " profile chunks in the file")  
        profiles = {}
        dates = []
        date_init = None
        loc = None
        for m in file_profiles:
            try:
                prof, dt_obj, init_dt, member = self._parseSection(m)
            except Exception as e:
                print(e)
                continue
            
            loc = prof.location
            # Try to add the profile object to the list of profiles for this member
            try:
                profiles[member] = profiles[member] + [prof]
            except Exception as e:
                print('THERE WAS AN EXCEPTION:', e)
                profiles[member] = [prof]
                print("Length of profiles:", len(prof.tmpc))
            if not dt_obj in dates:
                dates.append(dt_obj)
            if date_init is None or init_dt < date_init:
                date_init = init_dt
            #print(profiles)
        print(profiles, dates) 
        prof_coll = prof_collection.ProfCollection(profiles, dates)
        if "MEAN" in list(profiles.keys()):
            prof_coll.setHighlightedMember("MEAN")
        prof_coll.setMeta('observed', False)
        prof_coll.setMeta('base_time', date_init)
        prof_coll.setMeta('loc', loc)
        return prof_coll

    def _parseSection(self, section):
        print("TYPE OF SECTION:", type(section)) 
        parts = section.split('\n')
        if ' F' in parts[1]:
            valid, fhr = parts[1].split(' F')
            print(valid, fhr)
            fhr = int(fhr)
        else:
            valid = parts[1]
            fhr = 0
        print("TYPE OF VALID:", type(valid)) 
        dt_obj = datetime.strptime(valid, 'TIME = %y%m%d/%H%M')
        member = parts[0].split('=')[-1].strip()
        location = parts[2].split('SLAT')[0].split('=')[-1].strip()
        headers = [ h.lower() for h in parts[4].split(", ") ]
        data = '\n'.join(parts[5:])
        print("TYPE OF DATA:", type(data))
        sound_data = StringIO( data )
        
        prof_vars = np.genfromtxt( sound_data, delimiter=',', unpack=True)
        prof_var_dict = dict(zip(headers, prof_vars))
        
        def maybe_replace(old_var, new_var):
            if old_var in prof_var_dict:
                prof_var_dict[new_var] = prof_var_dict[old_var]
                del prof_var_dict[old_var]

        maybe_replace('omga', 'omeg')
        maybe_replace('temp', 'tmpc')
        maybe_replace('dewp', 'dwpc')
        print('STUFF GOING TO BE PASSED TO THE PROFILE OBJECT:', prof_var_dict.keys(), location, dt_obj)
        prof = profile.create_profile(profile='raw', location=location, date=dt_obj, missing=-999.0, **prof_var_dict)
        
        return prof, dt_obj, dt_obj - timedelta(hours=fhr), member

if __name__ == '__main__':
    prof_col = PECANDecoder("../../examples/data/ABR.txt")
    print(prof_col.getProfiles())
    #file.getProfs()


