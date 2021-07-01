import shutil, os
from contextlib import closing
import urllib.request as request

# Define the home directory where the .csv files will be stored.
HIDDEN_DSDIR = os.path.join(os.path.expanduser("~"), ".sharppy", "datasources")

# Download CSVs for all satellite-regions to HIDDEN_DSDIR.
def downloadAlaska_NOAA20():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/j01/csv/j01_alaska.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'j01_alaska.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass

def downloadCaribbean_NOAA20():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/j01/csv/j01_caribbean.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'j01_caribbean.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass

def downloadCONUS_NOAA20():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/j01/csv/j01_conus.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'j01_conus.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass

##########################
##########################

# def downloadAlaska_SNPP():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/npp/csv/npp_alaska.csv')) as r:
#            with open(os.path.join(HIDDEN_DSDIR, 'npp_alaska.csv'), 'wb') as f:
#                shutil.copyfileobj(r, f)
#     except:
#         pass
#
# def downloadCaribbean_SNPP():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/npp/csv/npp_caribbean.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'npp_caribbean.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass
#
# def downloadCONUS_SNPP():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/npp/csv/npp_conus.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'npp_conus.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass

##########################
##########################

# def downloadAlaska_Aqua():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/aq0/csv/aq0_alaska.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'aq0_alaska.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass
#
# def downloadCaribbean_Aqua():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/aq0/csv/aq0_caribbean.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'aq0_caribbean.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass

def downloadCONUS_Aqua():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/aq0/csv/aq0_conus.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'aq0_conus.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass

##########################
##########################

# def downloadAlaska_MetopA():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/m01/csv/m01_alaska.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'm01_alaska.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass
#
# def downloadCaribbean_MetopA():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/m01/csv/m01_caribbean.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'm01_caribbean.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass

def downloadCONUS_MetopA():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m01/csv/m01_conus.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'm01_conus.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass

##########################
##########################

# def downloadAlaska_MetopB():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/m02/csv/m02_alaska.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'm02_alaska.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass
#
# def downloadCaribbean_MetopB():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/m02/csv/m02_caribbean.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'm02_caribbean.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass

def downloadCONUS_MetopB():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m02/csv/m02_conus.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'm02_conus.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass

##########################
##########################

# def downloadAlaska_MetopC():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/m03/csv/m03_alaska.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'm03_alaska.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass
#
# def downloadCaribbean_MetopC():
#     try:
#         with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/m03/csv/m03_caribbean.csv')) as r:
#             with open(os.path.join(HIDDEN_DSDIR, 'm03_caribbean.csv'), 'wb') as f:
#                 shutil.copyfileobj(r, f)
#     except:
#         pass

def downloadCONUS_MetopC():
    try:
        with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m03/csv/m03_conus.csv')) as r:
            with open(os.path.join(HIDDEN_DSDIR, 'm03_conus.csv'), 'wb') as f:
                shutil.copyfileobj(r, f)
    except:
        pass
