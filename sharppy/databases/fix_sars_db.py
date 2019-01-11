import sars
import numpy as np
from datetime import datetime

supercell_db = np.loadtxt('sars_supercell.txt', skiprows=1, dtype=bytes, comments="%%%%") 
hail_db = np.loadtxt('sars_hail.txt', skiprows=1, dtype=bytes)
print(supercell_db)
print(hail_db)

for f in supercell_db[:,0]:
    f = f.decode("utf-8") 
    try:
        raw = sars.getSounding(str(f), 'supercell')
    except:
        print("NO DATA FILE FOR:", f)
        continue
    lines = open(raw, 'r').readlines()
    title = lines[1]
    loc = f.split('.')[1]
    print(title.strip(), f, loc)
    if 'RUC' in title.strip():
        #print("it's a model")
        new_title = title.replace(loc.lower(), '')
        new_title = new_title.replace('RUC', loc)
        new_title = new_title.replace('F000', '')
        new_title = new_title.replace(';', ',')
    elif "MRF" in title.strip():
        new_title = title.replace("MRF", loc.upper())
        fname = f.split('.')[0]
        new_title = loc.upper() + ' ' + fname[:6] + '/' + fname[6:8] + '00\n\n'
    else:
        continue
    note = '\n----- Note -----\nOld Title: ' + title + '\n' 
    #print("MODIFY:")
    #print("Old Title:", title)
    #print("New Title:", new_title)
    print("BEFORE:")
    print(''.join(lines))   
    lines[1] = " " + new_title
    new_data = ''.join(lines) + note
 
    print("AFTER:")
    print(new_data)
    #if "MRF" in title:
    #    break 
    f = open(raw, 'w')
    f.write(new_data)
    f.close() 
