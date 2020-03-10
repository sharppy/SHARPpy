
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from .decoder import Decoder
from sutils.utils import is_py3

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO
from datetime import datetime, timedelta

__fmtname__ = "spc"
__classname__ = "SPCDecoder"

class SPCDecoder(Decoder):
    def __init__(self, file_name):
        super(SPCDecoder, self).__init__(file_name)

    def _parse(self):
        file_data = self._downloadFile()
        ## read in the file
        data = np.array([l.strip() for l in file_data.split('\n')])

        ## necessary index points
        title_idx = np.where( data == '%TITLE%')[0][0]
        start_idx = np.where( data == '%RAW%' )[0][0] + 1
        finish_idx = np.where( data == '%END%')[0][0]

        ## create the plot title
        data_header = data[title_idx + 1].split()
        location = data_header[0]
        time = datetime.strptime(data_header[1][:11], '%y%m%d/%H%M')
        if len(data_header) > 2:
            lat, lon = data_header[2].split(',')
            lat = float(lat)
            lon = float(lon)
        else:
            lat = 35.
            lon = -97.

        if time > datetime.utcnow() + timedelta(hours=1): 
            # If the strptime accidently makes the sounding in the future (like with SARS archive)
            # i.e. a 1957 sounding becomes 2057 sounding...ensure that it's a part of the 20th century
            time = datetime.strptime('19' + data_header[1][:11], '%Y%m%d/%H%M')

        ## put it all together for StringIO
        full_data = '\n'.join(data[start_idx : finish_idx][:])

        if not is_py3():
            sound_data = StringIO( full_data )
        else:
            sound_data = BytesIO( full_data.encode() )

        ## read the data into arrays
        p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, delimiter=',', comments="%", unpack=True )
#       idx = np.argsort(p, kind='mergesort')[::-1] # sort by pressure in case the pressure array is off.

        pres = p #[idx]
        hght = h #[idx]
        tmpc = T #[idx]
        dwpc = Td #[idx]
        wspd = wspd #[idx]
        wdir = wdir #[idx]

        # Br00tal hack
        if hght[0] > 30000:
            hght[0] = -9999.00

        # Force latitude to be 35 N. Figure out a way to fix this later.
        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc,
            wdir=wdir, wspd=wspd, location=location, date=time, latitude=lat, missing=-9999.00)

        prof_coll = prof_collection.ProfCollection(
            {'':[ prof ]}, 
            [ time ],
        )

        prof_coll.setMeta('loc', location)
        prof_coll.setMeta('observed', True)
        prof_coll.setMeta('base_time', time)
        return prof_coll

#if __name__ == '__main__':
#    import sys
#    SPCDecoder(sys.argv[1])
