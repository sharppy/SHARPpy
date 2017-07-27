import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
import sharppy.sharptab.constants as constants
from decoder import Decoder

from datetime import datetime
from re import split

__fmtname__ = "fsl"
__classname__ = "FSLDecoder"

MISSING = '99999'

MONTHS = dict([(datetime.now().replace(month=x).strftime('%b').upper(), x) for x in range(1,13)])
DIRECTIONS = {'N':1, 'S':-1, 'E':1, 'W':-1}

def qc_float(value):
    if value == MISSING:
        value = np.NaN#constants.MISSING
    else:
        value = float(value)
    return value

def interp_winds_levels(pres, tmpc, dwpc):
    last_good = -1
    next_good = 0
    for i in range(len(pres)):
        if np.isnan(tmpc[i]) or np.isnan(dwpc[i]):
            if pres[i] < pres[next_good]:
                for j in range(i, len(pres)):
                    if not np.isnan(tmpc[j]) and not np.isnan(dwpc[j]):
                        next_good = j
                        break
                if np.isnan(tmpc[i]):
                    tmpc[i] = tmpc[last_good] - (tmpc[last_good] - tmpc[next_good])/(pres[last_good]-pres[next_good])*(pres[last_good]-pres[i])
                if np.isnan(dwpc[i]):
                    dwpc[i] = dwpc[last_good] - (dwpc[last_good] - dwpc[next_good])/(pres[last_good]-pres[next_good])*(pres[last_good]-pres[i])
        else:
            last_good = i
    return pres, tmpc, dwpc

class FSLDecoder(Decoder):
    def __init__(self, file_name):
        super(FSLDecoder, self).__init__(file_name)
    def _parse(self):
        file_data = self._downloadFile().split('\n')
        wind_units = 'kt'
        pres = []
        hght = []
        tmpc = []
        dwpc = []
        wspd = []
        wdir = []
        for x in file_data:
            line_type = int(x[:7])
            line = split('\s*', x[7:].strip())
            if line_type == 254:
                time = datetime(int(line[3]), MONTHS[line[2]], int(line[1]), int(line[0]))
            elif line_type == 1:
                lat = float(line[2][:-1]) * DIRECTIONS[line[2][-1]]
                lon = float(line[3][:-1]) * DIRECTIONS[line[3][-1]]
                elev = int(line[4])                
            elif line_type == 2:
                pass
            elif line_type == 3:
                location = line[0]
                wind_units = line[2]
            elif line_type == 4:
                if qc_float(line[1]) > hght[-1]:# and qc_float(line[2]) != constants.MISSING and qc_float(line[3]) != constants.MISSING:
                    pres.append(qc_float(line[0])/10.0)
                    hght.append(qc_float(line[1]))
                    tmpc.append(qc_float(line[2])/10.0)
                    dwpc.append(qc_float(line[3])/10.0)
                    wdir.append(qc_float(line[4]))
                    wspd.append(qc_float(line[5]) if wind_units == 'kt' else qc_float(line[5])/10.0)
            elif line_type == 5:
                if qc_float(line[1]) > hght[-1]:# and qc_float(line[2]) != constants.MISSING and qc_float(line[3]) != constants.MISSING:
                    pres.append(qc_float(line[0])/10.0)
                    hght.append(qc_float(line[1]))
                    tmpc.append(qc_float(line[2])/10.0)
                    dwpc.append(qc_float(line[3])/10.0)
                    wdir.append(qc_float(line[4]))
                    wspd.append(qc_float(line[5]) if wind_units == 'kt' else qc_float(line[5])/10.0)
            elif line_type == 6:
                if qc_float(line[1]) > hght[-1]:# and qc_float(line[2]) != constants.MISSING and qc_float(line[3]) != constants.MISSING:
                    pres.append(qc_float(line[0])/10.0)
                    hght.append(qc_float(line[1]))
                    tmpc.append(qc_float(line[2])/10.0)
                    dwpc.append(qc_float(line[3])/10.0)
                    wdir.append(qc_float(line[4]))
                    wspd.append(qc_float(line[5]) if wind_units == 'kt' else qc_float(line[5])/10.0)
            elif line_type == 7:
                pass
            elif line_type == 8:
                pass
            elif line_type == 9:
                pres.append(qc_float(line[0])/10.0)
                hght.append(qc_float(line[1]))
                tmpc.append(qc_float(line[2])/10.0)
                dwpc.append(qc_float(line[3])/10.0)
                wdir.append(qc_float(line[4]))
                wspd.append(qc_float(line[5]) if wind_units == 'kt' else qc_float(line[5])/10.0)
        
        pres = np.array(pres)
        hght = np.array(hght)
        tmpc = np.array(tmpc)
        dwpc = np.array(dwpc)
        wdir = np.array(wdir)
        wspd = np.array(wspd)
        pres, tmpc, dwpc = interp_winds_levels(pres, tmpc, dwpc)
        pres, tmpc, dwpc = interp_winds_levels(pres, tmpc, dwpc)


        wdir[np.isnan(wdir)] = constants.MISSING
        wspd[np.isnan(wspd)] = constants.MISSING

        # qc_filter = (tmpc != constants.MISSING) + (dwpc != constants.MISSING)

        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc,
            wdir=wdir, wspd=wspd, location=location, date=time, latitude=lat)

        prof_coll = prof_collection.ProfCollection(
            {'':[ prof ]}, 
            [ time ],
        )

        prof_coll.setMeta('loc', location)
        prof_coll.setMeta('observed', True)
        prof_coll.setMeta('base_time', time)
        return prof_coll
