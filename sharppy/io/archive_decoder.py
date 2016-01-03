
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from decoder import Decoder

from datetime import datetime
from dateutil import parser
from bson import loads
from bz2 import decompress

__fmtname__ = "archive"
__classname__ = "ArchiveDecoder"

class ArchiveDecoder(Decoder):
    def __init__(self, file_name):
        super(ArchiveDecoder, self).__init__(file_name)

    def _parse(self):
        file_data = self._downloadFile()
        
        serialized_data = loads(decompress(file_data))
        dates = []
        for mem in serialized_data['profiles']:
            for prof in range(len(serialized_data['profiles'][mem])):
                #serialized_data['profiles'][mem][prof]['date'] = parser.parse(serialized_data['profiles'][mem][prof]['date'])
                if serialized_data['profiles'][mem][prof]['date'] not in dates:
                    dates.append(serialized_data['profiles'][mem][prof]['date'])
                serialized_data['profiles'][mem][prof]['profile'] = 'raw'
                serialized_data['profiles'][mem][prof] = profile.create_profile(**serialized_data['profiles'][mem][prof])
        
        #serialized_data['dates'] = [parser.parse(date) for date in serialized_data['dates']]
        
        prof_coll = prof_collection.ProfCollection(serialized_data['profiles'], dates)
        prof_coll.setHighlightedMember(serialized_data['highlighted'])
        for key in serialized_data['meta']:
            prof_coll.setMeta(key, serialized_data['meta'][key])
        return prof_coll