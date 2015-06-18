
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from decoder import Decoder

from StringIO import StringIO
from datetime import datetime

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
        start_idx = np.where( data == '%RAW%' )[0] + 1
        finish_idx = np.where( data == '%END%')[0]

        ## create the plot title
        data_header = data[title_idx + 1].split()
        location = data_header[0]
        time = data_header[1][:11]

        ## put it all together for StringIO
        full_data = '\n'.join(data[start_idx : finish_idx][:])
        sound_data = StringIO( full_data )

        ## read the data into arrays
        p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, delimiter=',', comments="%", unpack=True )
#       idx = np.argsort(p, kind='mergesort')[::-1] # sort by pressure in case the pressure array is off.

        pres = p #[idx]
        hght = h #[idx]
        tmpc = T #[idx]
        dwpc = Td #[idx]
        wspd = wspd #[idx]
        wdir = wdir #[idx]

        # Force latitude to be 35 N. Figure out a way to fix this later.
        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc,
            wdir=wdir, wspd=wspd, location=location, latitude=35.)

        prof_coll = prof_collection.ProfCollection(
            {'':[ prof ]}, 
            [ datetime.strptime(time, '%y%m%d/%H%M') ],
        )

        prof_coll.setMeta('loc', location)
        return prof_coll
