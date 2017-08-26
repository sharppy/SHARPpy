from re import compile, search, sub
from datetime import datetime
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
import sharppy.sharptab.constants as constants
from sharppy.io.decoder import Decoder
from os.path import join as path_join

station_types = {'II': 'mobile', 'TT': 'land', 'XX': 'dropsonde', 'PP': 'wind aloft'}

msg_regex = compile(r'([IiTtXxPp]{2})([AaBbCcDd]{2})\s+([^\s]*)?\s+(?:[0-9/]{5}\s*)+')
valid_section_regex = compile(r'[0-9/]{5}')

__fmtname__ = "wmo"
__classname__ = "WMODecoder"

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

def interp_values(pres, field):
    start_points = []
    end_points = []
    for i in range(len(pres)):
        if not np.isnan(field[i]):
            if len(start_points) == 0:
                start_points.append(i)
            else:
                end_points.append(i)
                start_points.append(i)
    start_points = start_points[:-1]
    j = 0
    for i in range(len(pres)):
        if np.isnan(field[i]):
            while not (pres[start_points[j]]>=pres[i] and pres[i]>=pres[end_points[j]]):
                j += 1
                if j >= len(start_points):
                    break
            if j >= len(start_points):
                break
            field[i] = field[start_points[j]] - (field[start_points[j]] - field[end_points[j]])/(pres[start_points[j]]-pres[end_points[j]])*(pres[start_points[j]]-pres[i])
            #print(((field[start_points[j]], field[end_points[j]]), (pres[start_points[j]], pres[end_points[j]]), pres[i], field[i]))
    return field

def interp_height(pres, field):
    start_points = []
    end_points = []
    for i in range(len(pres)):
        if not np.isnan(field[i]):
            if len(start_points) == 0:
                start_points.append(i)
            else:
                end_points.append(i)
                start_points.append(i)
    start_points = start_points[:-1]
    j = 0
    h = (field[end_points[j]] - field[start_points[j]])/np.log(pres[start_points[j]]/pres[end_points[j]])
    for i in range(len(pres)):
        if np.isnan(field[i]):
            if j < len(start_points):
                while not (pres[start_points[j]]>=pres[i] and pres[i]>=pres[end_points[j]]):
                    j += 1
                    if j < len(start_points):
                        h = (field[end_points[j]] - field[start_points[j]])/np.log(pres[start_points[j]]/pres[end_points[j]])
                    else:
                        break
                if j < len(start_points):
                    field[i] = h*np.log(pres[start_points[j]]/pres[i]) + field[start_points[j]]
                else:
                    field[i] = h*np.log(pres[end_points[-1]]/pres[i]) + field[end_points[-1]]    
            else:
                field[i] = h*np.log(pres[end_points[-1]]/pres[i]) + field[end_points[-1]]
    return field

def interp_pres(pres_hght, hght):
    start_points = []
    end_points = []
    for i in range(len(pres)):
        if not np.isnan(field[i]):
            if len(start_points) == 0:
                start_points.append(i)
            else:
                end_points.append(i)
                start_points.append(i)
    start_points = start_points[:-1]
    j = 0
    h = (field[end_points[j]] - field[start_points[j]])/np.log(pres[start_points[j]]/pres[end_points[j]])
    for i in range(len(pres)):
        if np.isnan(field[i]):
            if j < len(start_points):
                while not (pres[start_points[j]]>=pres[i] and pres[i]>=pres[end_points[j]]):
                    j += 1
                    if j < len(start_points):
                        h = (field[end_points[j]] - field[start_points[j]])/np.log(pres[start_points[j]]/pres[end_points[j]])
                    else:
                        break
                if j < len(start_points):
                    field[i] = h*np.log(pres[start_points[j]]/pres[i]) + field[start_points[j]]
                else:
                    field[i] = h*np.log(pres[end_points[-1]]/pres[i]) + field[end_points[-1]]    
            else:
                field[i] = h*np.log(pres[end_points[-1]]/pres[i]) + field[end_points[-1]]
    return field

class WMODecoder(Decoder):
    def __init__(self, file_name):
        super(WMODecoder, self).__init__(file_name)
    def _parse(self):
        file_data = self._downloadFile()
        station_type = ''
        station_name, date, stn, hght, tmpc, dwpc, wdir, wspd = ([],[],[],[],[],[],[],[])
        wmo_messages = [None, None, None, None, None]
        wmo_message = search(msg_regex, file_data)
        if wmo_message is None:
            raise ValueError('No WMO type message fround.')
        while wmo_message is not None:
            if wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'AA':
                wmo_messages[0] = wmo_message
            elif wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'BB':
                wmo_messages[1] = wmo_message
            elif wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'CC':
                wmo_messages[2] = wmo_message
            elif wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'DD':
                wmo_messages[3] = wmo_message
            elif wmo_message.group(1) == 'PP':
                wmo_messages[4] = wmo_message
            file_data = file_data.replace(wmo_message.group(0), '')
            wmo_message = search(msg_regex, file_data)
        for wmo_message in wmo_messages:
            if wmo_message is not None:
                if station_type == '':
                    station_type = station_types[wmo_message.group(1)]
                if search(valid_section_regex, wmo_message.group(3)) == None:
                    mstation_name = wmo_message.group(3)
                else:
                    mstation_name = False
                message = self._clean_msg(wmo_message.group(0), station_name=mstation_name)
                if wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'AA':
                    mdate, mstn, mhght, mtmpc, mdwpc, mwdir, mwspd = self._parse_AA(message)
                elif wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'BB':
                    mdate, mstn, mhght, mtmpc, mdwpc, mwdir, mwspd = self._parse_BB(message)
                elif wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'CC':
                    mdate, mstn, mhght, mtmpc, mdwpc, mwdir, mwspd = self._parse_CC(message)
                elif wmo_message.group(1) != 'PP' and wmo_message.group(2) == 'DD':
                    mdate, mstn, mhght, mtmpc, mdwpc, mwdir, mwspd = self._parse_DD(message)
                elif wmo_message.group(1) == 'PP':
                    pass #mdate, mstn, mhght, mtmpc, mdwpc, mwdir, mwspd = self._parse_PP(message, hght)
                station_name.append(mstation_name)
                date.append(mdate)
                stn.append(mstn)
                hght.extend(mhght)
                tmpc.extend(mtmpc)
                dwpc.extend(mdwpc)
                wdir.extend(mwdir)
                wspd.extend(mwspd)
                # file_data = file_data.replace(wmo_message.group(0), '')
                # wmo_message = search(msg_regex, file_data)
        for i in range(1, len(date)):
            if date[i] != date[0]:
                raise ValueError('Multiple dates found in file, not supported')
            if station_name[i] != station_name[0]:
                raise ValueError('Multiple station names found in file, not supported')
            if stn[i][0] != stn[0][0] and stn[i][1] != stn[0][1]:
                raise ValueError('Multiple stations found in files, not supported')
        if station_name[0]:
            location = '{0:s}(lat={1:.2f}{2:s},lon={3:.2f}{4:s},elev={5:.2f}m)'.format(station_name[0], abs(stn[0][0]), 'N' if stn[0][0] > 0 else 'S', abs(stn[0][1]), 'W' if stn[0][1] < 0 else 'E', min([stn[i][2] for i in range(len(stn))]))
        else:
            if stn[0][3] != '':
                location = stn[0][3]
            else:
                location = 'lat={0:.2f}{1:s},lon={2:.2f}{3:s},elev={4:.2f}m'.format(abs(stn[0][0]), 'N' if stn[0][0] > 0 else 'S', abs(stn[0][1]), 'W' if stn[0][1] < 0 else 'E', min([stn[i][2] for i in range(len(stn))]))
        pres, hght, tmpc, dwpc, wdir, wspd = self._make_arrays(hght, tmpc, dwpc, wdir, wspd, min([stn[i][2] for i in range(len(stn))]))
        
        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc,
            wdir=wdir, wspd=wspd, location=location, date=date[0], latitude=stn[0][0])

        prof_coll = prof_collection.ProfCollection(
            {'':[ prof ]}, 
            [ date[0] ],
        )

        prof_coll.setMeta('loc', location)
        prof_coll.setMeta('observed', True)
        prof_coll.setMeta('base_time', date[0])
        return prof_coll
    def _parse_AA(self, message):
        man_levels = {'00':[1000, 0], '92':[925, 0], '85':[850, 1000], '70':[700, 2000], '50':[500, 0], \
                      '40':[400, 0], '30':[300, 0], '25':[250, 10000], '20':[200, 10000], '15':[150, 10000], \
                      '10':[100, 10000], '99':[9999]}
        hght, tmpc, dwpc, wdir, wspd = ([], [], [], [], [])
        date, stn, is_kts = self._get_header(message)
        for i in range(3, len(message)):
            if message[i][0:2] == '99':
                sounding_start = i
                break
        for i in range(sounding_start, len(message), 3):
            if message[i][0:2] in man_levels:
                lhght, ltmpc, ldwpc, lwdir, lwspd = self._parse_man_level(message[i:i+3], man_levels, is_kts)
                hght.append(lhght)#(lhght[0], stn[2]) if np.isnan(lhght[1]) else lhght)
                tmpc.append(ltmpc)
                dwpc.append(ldwpc)
                wdir.append(lwdir)
                wspd.append(lwspd)
        return date, stn, hght, tmpc, dwpc, wdir, wspd
    def _parse_BB(self, message):
        hght, tmpc, dwpc, wdir, wspd = ([], [], [], [], [])
        date, stn, is_kts = self._get_header(message)
        for i in range(3, len(message)):
            if message[i][0:2] == '00':
                sounding_start = i
                break
        sig_type = 0 # temperature
        i = sounding_start
        while i is not None:
            if message[i][0:2] in ['{0:d}{0:d}'.format(x) for x in range(10)] and sig_type < 2:
                lhght, ltmpc, ldwpc, lwdir, lwspd = self._parse_sig_level(message[i:i+2], sig_type, is_kts, cross_over_pressure=100.0)
                hght.append(lhght)
                tmpc.append(ltmpc)
                dwpc.append(ldwpc)
                wdir.append(lwdir)
                wspd.append(lwspd)
                i += 2
            elif message[i] == '21212' and sig_type < 2:
                sig_type = 1 # wind
                i += 1
            else:
                sig_type = 2
                i += 1
            if i == len(message):
                i = None
        return date, stn, hght, tmpc, dwpc, wdir, wspd
    def _parse_CC(self, message):
        pres, hght, tmpc, dwpc, wdir, wspd = ([], [], [], [], [], [])
        date, stn, is_kts = self._get_header(message)
        return date, stn, hght, tmpc, dwpc, wdir, wspd
    def _parse_DD(self, message):
        pres, hght, tmpc, dwpc, wdir, wspd = ([], [], [], [], [], [])
        date, stn, is_kts = self._get_header(message)
        return date, stn, hght, tmpc, dwpc, wdir, wspd
    def _parse_PP(self, message):
        pres, hght, tmpc, dwpc, wdir, wspd = ([], [], [], [], [], [])
        date, stn, is_kts = self._get_header(message)
        for i in range(3, len(message)):
            if message[i][0:2] == '00':
                sounding_start = i
                break
        #i = sounding_start
        return date, stn, hght, tmpc, dwpc, wdir, wspd
    def _clean_msg(self, message, station_name=False):
        if station_name:
            message = message.replace(station_name, '')
        message = sub('\s+', ' ', message).strip()
        return message.split(' ')
    def _make_date(self, day, hour):
        now = datetime.utcnow().replace(hour=hour, minute=0, second=0, microsecond=0)
        date = None
        while date is None:
            try:
                date = now.replace(day=day)
                if date > now:
                    if date.month == 1:
                        date = date.replace(month=12, year=date.year-1)
                    else:
                        date = date.replace(month=date.month-1)
            except:
                if now.month == 1:
                    now = now.replace(month=12, year=now.year-1)
                else:
                    now = now.replace(month=now.month-1)
                date = None
        return date
    def _get_header(self, message):
        day = int(message[1][0:2])
        if day > 50:
            is_kts = True
            day -= 50
        else:
            is_kts = False
        date = self._make_date(day, int(message[1][2:4]))
        if message[2][0:2] == '99':
            stn = (float(message[2][2:])/10.0 if message[3][0] == 3 or message[3][0] == 5 else float(message[2][2:])/-10.0, \
                   float(message[3][1:])/10.0 if message[3][0] == 7 or message[3][0] == 5 else float(message[3][1:])/-10.0, \
                   float(message[5][:4]) if message[5][4] < 5 else 0.3048 * float(message[5][:4]), '')
        else:
            stn = self._get_synop_station(message[2])
        return date, stn, is_kts
    def _parse_man_level(self, level, man_levels, is_kts):
        pres = hght = tmpc = dwpc = wdir = wspd = np.NaN
        if level[0][0:2] == '99':
            pres = float(level[0][2:])
            if pres < 500:
                pres += 1000
            hght = np.inf
        else:
            pres = man_levels[level[0][:2]][0]
            hght = float(level[0][2:])
            if pres == 700:
                if hght < 500:
                    hght += man_levels[level[0][:2]][1] + 1000
                else:
                    hght += man_levels[level[0][:2]][1]
            elif pres == 300:
                if hght < 500:
                    hght *= 10
                    hght += man_levels[level[0][:2]][1] + 1000
                else:
                    hght *= 10
                    hght += man_levels[level[0][:2]][1]
            elif pres > 500:
                hght += man_levels[level[0][:2]][1]
            else:
                hght *= 10
                hght += man_levels[level[0][:2]][1]
        if level[1][0:3] != '///':
            tmpc = float(level[1][0:3])/-10.0 if bool(int(level[1][2])%2) else float(level[1][0:3])/10.0
        if level[1][3:] != '//':
            dwpc = float(level[1][3:])
            dwpc = tmpc - ((dwpc / 10.0) if dwpc <= 50.0 else (dwpc - 50.0))
        if level[2] != '/////':
            wspd = float(level[2][2:])
            wdir = float(level[2][:2]) * 10.0 + (5.0 if wspd >= 500.0 else 0.0)
            wspd -= 500.0 if wspd >= 500.0 else 0.0
            if not is_kts:
                wspd *= 1.94384
        return (pres, hght), (pres, tmpc), (pres, dwpc), (pres, wdir), (pres, wspd)
    def _parse_sig_level(self, level, sig_type, is_kts, cross_over_pressure=100.0):
        pres = hght = tmpc = dwpc = wdir = wspd = np.NaN
        pres = float(level[0][2:])
        if pres < 100.0:
            pres += 1000.0
        if level[0][0:2] == '00':
            hght = np.inf
        if sig_type == 0:
            if level[1][0:3] != '///':
                tmpc = float(level[1][0:3])/-10.0 if bool(int(level[1][2])%2) else float(level[1][0:3])/10.0
            if level[1][3:] != '//':
                dwpc = float(level[1][3:])
                dwpc = tmpc - ((dwpc / 10.0) if dwpc <= 50.0 else (dwpc - 50.0))
        elif sig_type == 1:
            if level[1] != '/////':
                wspd = float(level[1][2:])
                wdir = float(level[1][:2]) * 10.0 + (5.0 if wspd >= 500.0 else 0.0)
                wspd -= 500.0 if wspd >= 500.0 else 0.0
                if not is_kts:
                    wspd *= 1.94384
        return (pres, hght), (pres, tmpc), (pres, dwpc), (pres, wdir), (pres, wspd)
    def _get_synop_station(self, synop_id):
        # stns[0][20:24], stns[0][26:29], stns[0][32:37], stns[0][39:41], stns[0][42:44], stns[0][44], stns[0][47:50], stns[0][51:53], stns[0][53], stns[0][55:59]
        lat = lon = elev = 0.0
        stn_name = synop_id
        with open(path_join(__file__.replace('wmo_decoder.py', ''), 'stations.txt') ,'r') as stn_file:
            line = stn_file.readline()
            while line != '':
                if len(line) == 84 and line[0] != '!':
                    if line[32:37] == synop_id:
                        lat = float(line[39:41]) + float(line[42:44])/60.0
                        if line[44].upper() == 'S':
                            lat *= -1.0
                        lon = float(line[47:50]) + float(line[51:53])/60.0
                        if line[53].upper() == 'W':
                            lon *= -1.0
                        elev = float(line[55:59])
                        stn_name = line[26:29] if line[26:29] != '   ' else line[20:24]
                line = stn_file.readline()
        return (lat, lon, elev, stn_name)
    def _make_arrays(self, hght, tmpc, dwpc, wdir, wspd, elev):
        hght = self._qc_dict(hght)
        tmpc = self._qc_dict(tmpc)
        dwpc = self._qc_dict(dwpc)
        wdir = self._qc_dict(wdir)
        wspd = self._qc_dict(wspd)
        pres = []
        for x in [hght, tmpc, dwpc, wdir, wspd]:
            pres.extend(x.keys())
        pres = list(set(pres))
        pres.sort(reverse=True)
        lpres, lhght, ltmpc, ldwpc, lwdir, lwspd = ([], [], [], [], [], [])
        for i in range(len(pres)):
            lpres.append(pres[i])
            lhght.append((hght[pres[i]] if not np.isinf(hght[pres[i]]) else elev) if pres[i] in hght else np.NaN)
            ltmpc.append(tmpc[pres[i]] if pres[i] in tmpc else np.NaN)
            ldwpc.append(dwpc[pres[i]] if pres[i] in dwpc else np.NaN)
            lwdir.append(wdir[pres[i]] if pres[i] in wdir else np.NaN)
            lwspd.append(wspd[pres[i]] if pres[i] in wspd else np.NaN)
        lhght = np.array(lhght)
        ltmpc = np.array(ltmpc)
        ldwpc = np.array(ldwpc)
        lwdir = np.array(lwdir)
        lwspd = np.array(lwspd)
        lpres = np.array(lpres)
        mask = np.isfinite(ltmpc) + np.isfinite(ldwpc) + np.isfinite(lwdir) + np.isfinite(lwspd)
        lpres = lpres[mask]
        lhght = lhght[mask]
        ltmpc = ltmpc[mask]
        ldwpc = ldwpc[mask]
        lwdir = lwdir[mask]
        lwspd = lwspd[mask]
        #lpres, ltmpc, ldwpc = interp_winds_levels(lpres, ltmpc, ldwpc)
        #lpres, ltmpc, ldwpc = interp_winds_levels(lpres, ltmpc, ldwpc)
        lhght = interp_height(lpres, lhght)
        ltmpc = interp_values(lpres, ltmpc)
        ldwpc = interp_values(lpres, ldwpc)

        mask = np.array([True]+list((np.diff(lhght, 1)>0)*(np.diff(lpres, 1)<0)))

        while sum(mask) != len(mask):
            print(str(len(mask)) + " errors found")
            lpres = lpres[mask]
            lhght = lhght[mask]
            ltmpc = ltmpc[mask]
            ldwpc = ldwpc[mask]
            lwdir = lwdir[mask]
            lwspd = lwspd[mask]
            mask = np.array([True]+list((np.diff(lhght, 1)>0)*(np.diff(lpres, 1)<0)))

        lwdir[np.isnan(lwdir)] = constants.MISSING
        lwspd[np.isnan(lwspd)] = constants.MISSING
        
        return lpres, lhght, ltmpc, ldwpc, lwdir, lwspd
    def _qc_dict(self, field_list):
        pres = {}
        drop = []
        for i in range(len(field_list)):
            if field_list[i][0] not in pres:
                pres[field_list[i][0]] = i
            else:
                if np.isnan(field_list[pres[field_list[i][0]]][1]) and not np.isnan(field_list[i][1]):
                    drop.append(pres[field_list[i][0]])
                    pres[field_list[i][0]] = i
                elif not ((field_list[pres[field_list[i][0]]][1] == field_list[i][1]) or \
                          (np.isnan(field_list[pres[field_list[i][0]]][1]) and np.isnan(field_list[i][1])) or \
                          (np.isinf(field_list[pres[field_list[i][0]]][1]) and np.isinf(field_list[i][1]))):
                    #raise ValueError('Multiple values found for single pressure level, not supported')
                    drop.append(i)
        drop.sort(reverse=True)
        for i in drop:
            field_list.pop(i)
        return dict(field_list)
    def _to_pressure_index(self, hght, tmpc, dwpc, wdir, wspd):
        pres = {}
        drop = []
        for i in range(len(hght)):
            if hght[i][0] not in pres:
                pres[hght[i][0]] = i
            else:
                if np.isnan(hght[pres[hght[i][0]]][1]) and not np.isnan(hght[i][1]):
                    drop.append(pres[hght[i][0]])
                    pres[hght[i][0]] = i
                else:
                    if not ((hght[pres[hght[i][0]]][1] == hght[i][1]) or (np.isnan(hght[pres[hght[i][0]]][1]) and np.isnan(hght[i][1]))):
                        raise ValueError('Multiple values found for single pressure level, not supported')
            if tmpc[i][0] not in pres:
                pres[tmpc[i][0]] = i
            else:
                if np.isnan(tmpc[pres[tmpc[i][0]]][1]) and not np.isnan(tmpc[i][1]):
                    drop.append(pres[tmpc[i][0]])
                    pres[tmpc[i][0]] = i
                else:
                    if not ((tmpc[pres[tmpc[i][0]]][1] == tmpc[i][1]) or (np.isnan(tmpc[pres[tmpc[i][0]]][1]) and np.isnan(tmpc[i][1]))):
                        raise ValueError('Multiple values found for single pressure level, not supported')
            if dwpc[i][0] not in pres:
                pres[dwpc[i][0]] = i
            else:
                if np.isnan(dwpc[pres[dwpc[i][0]]][1]) and not np.isnan(dwpc[i][1]):
                    drop.append(pres[dwpc[i][0]])
                    pres[dwpc[i][0]] = i
                else:
                    if not ((dwpc[pres[dwpc[i][0]]][1] == dwpc[i][1]) or (np.isnan(dwpc[pres[dwpc[i][0]]][1]) and np.isnan(dwpc[i][1]))):
                        raise ValueError('Multiple values found for single pressure level, not supported')
            if wdir[i][0] not in pres:
                pres[wdir[i][0]] = i
            else:
                if np.isnan(wdir[pres[wdir[i][0]]][1]) and not np.isnan(wdir[i][1]):
                    drop.append(pres[wdir[i][0]])
                    pres[wdir[i][0]] = i
                else:
                    if not ((wdir[pres[wdir[i][0]]][1] == wdir[i][1]) or (np.isnan(wdir[pres[wdir[i][0]]][1]) and np.isnan(wdir[i][1]))):
                        raise ValueError('Multiple values found for single pressure level, not supported')
            if wspd[i][0] not in pres:
                pres[wspd[i][0]] = i
            else:
                if np.isnan(wspd[pres[wspd[i][0]]][1]) and not np.isnan(wspd[i][1]):
                    drop.append(pres[wspd[i][0]])
                    pres[wspd[i][0]] = i
                else:
                    if not ((wspd[pres[wspd[i][0]]][1] == wspd[i][1]) or (np.isnan(wspd[pres[wspd[i][0]]][1]) and np.isnan(wspd[i][1]))):
                        raise ValueError('Multiple values found for single pressure level, not supported')
        drop.sort(reverse=True)
        for i in drop:
            hght.pop(i)
            tmpc.pop(i)
            dwpc.pop(i)
            wdir.pop(i)
            wspd.pop(i)
        return dict(hght), dict(tmpc), dict(dwpc), dict(wdir), dict(wspd)
        
                    
if __name__ == '__main__':
    from os import listdir, getcwd
    from os.path import splitext
    import warnings
    warnings.filterwarnings("ignore")
    for x in listdir(getcwd()):
        if splitext(x)[1] not in [ ".py", '.txt']:
            print(x)
            a = WMODecoder(x)
            b = a.getProfiles()
            c = b.getCurrentProfs()
            c[''].toFile(x.replace('.wmo', '.txt'))