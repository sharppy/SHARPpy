
import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from .decoder import Decoder

from datetime import datetime

__fmtname__ = "uwyo"
__classname__ = "UWYODecoder"

class UWYODecoder(Decoder):
    MISSING = -9999.00

    def __init__(self, file_name):
        super(UWYODecoder, self).__init__(file_name)

    def _parse(self):
        file_data = self._downloadFile()
        snfile = [l for l in file_data.split('\n')]

        bgn = -1
        end = -1
        ttl = -1
        stl = -1

        for i in range(len(snfile)):
            if snfile[i] == "<PRE>": 
                bgn = i+5
            if snfile[i][:10] == "</PRE><H3>": 
                end = i-1
            if snfile[i][:4] == "<H2>" and snfile[i][-5:] == "</H2>": 
                ttl = i
            if 'Station latitude' in snfile[i]:
                stl = i

        if bgn == -1 or end == -1 or ttl == -1:
            raise IOError("Looks like the server had difficulty handling the request.  Try again in a few minutes.")

        snd_data = []
        for i in range(bgn, end+1):
            vals = []
            for j in [ 0, 1, 2, 3, 6, 7 ]:
                val = snfile[i][(7 * j):(7 * (j + 1))].strip()

                if val == "":
                    vals.append(UWYODecoder.MISSING)
                else:
                    vals.append(float(val))
            snd_data.append(vals)

        col_names = ['pres', 'hght', 'tmpc', 'dwpc', 'wdir', 'wspd']
        snd_dict = dict((v, p) for v, p in zip(col_names, list(zip(*snd_data))))

        snd_date = datetime.strptime(snfile[ttl][-20:-5], "%HZ %d %b %Y")

        loc = snfile[ttl][10:14]
        if stl == -1:
            lat = 35.
        else:
            lat = float(snfile[stl].split(':')[-1].strip())

        prof = profile.create_profile(profile='raw', location=loc, date=snd_date, latitude=lat, missing=UWYODecoder.MISSING, **snd_dict)

        prof_coll = prof_collection.ProfCollection(
            {'':[ prof ]},
            [ snd_date ],
        )

        prof_coll.setMeta('loc', loc)
        prof_coll.setMeta('observed', True)
        return prof_coll

#if __name__ == "__main__":
    
