import sharppy.sharptab.profile as profile
from sharppy.io.decoder import getDecoders
import sys

def decode(filename):

    for decname, deccls in getDecoders().items():
        try:
            dec = deccls(filename)
            break
        except:
            dec = None
            continue

    if dec is None:
        raise IOError("Could not figure out the format of '%s'!" % filename)

    # Returns the set of profiles from the file that are from the "Profile" class.
    profs = dec.getProfiles()
    stn_id = dec.getStnId()

    return profs, stn_id

def test_url():
    path = 'examples/data/14061619.OAX'
    # Sys.argv[1] should be the URL to the file that is being tested.
    profs, stn_id = decode(path)
    print((profs._profs))

    for k in profs._profs.keys():
        all_prof = profs._profs[k]
        dates = profs._dates
        for i in range(len(all_prof)):
            prof = all_prof[i]
            new_prof = profile.create_profile(pres=prof.pres, hght=prof.hght, tmpc=prof.tmpc, dwpc=prof.dwpc, wspd=prof.wspd, \
                                              wdir=prof.wdir, strictQC=False, profile='convective', date=dates[i])
            #for key in dir(new_prof):
            #    print((key, getattr(new_prof,key)))
    
    
    print(new_prof.mupcl.bplus)

