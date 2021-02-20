import shutil
from contextlib import closing
import urllib.request as request
import numpy as np
import glob
import os

# Define the home directory where the .csv files will be stored.
HIDDEN_DSDIR = os.path.join(os.path.expanduser("~"), ".sharppy", "datasources")
SHARPPY_DIR = os.path.abspath(os.curdir)

# Download CSVs for all satellites and regions to SHARPPY_DIR.
def downloadNewCSVs():
    # Download Alaska, Caribbean and CONUS CSVs for NOAA-20.
    with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/j01/csv/j01_alaska.csv')) as r:
        with open('j01_alaska.csv', 'wb') as f:
            shutil.copyfileobj(r, f)

    with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/j01/csv/j01_caribbean.csv')) as r:
        with open('j01_caribbean.csv', 'wb') as f:
            shutil.copyfileobj(r, f)

    with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/j01/csv/j01_conus.csv')) as r:
        with open('j01_conus.csv', 'wb') as f:
            shutil.copyfileobj(r, f)

    # Download Alaska, Caribbean and CONUS CSVs for Suomi-NPP.
    with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/npp/csv/npp_alaska.csv')) as r:
        with open('npp_alaska.csv', 'wb') as f:
            shutil.copyfileobj(r, f)

    with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/npp/csv/npp_caribbean.csv')) as r:
        with open('npp_caribbean.csv', 'wb') as f:
            shutil.copyfileobj(r, f)

    with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/npp/csv/npp_conus.csv')) as r:
        with open('npp_conus.csv', 'wb') as f:
            shutil.copyfileobj(r, f)

    # # Download Alaska, Caribbean and CONUS CSVs for Metop-A.
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/m01/csv/m01_alaska.csv')) as r:
    #     with open('m01_alaska.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/m01/csv/m01_caribbean.csv')) as r:
    #     with open('m01_caribbean.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m01/csv/m01_conus.csv')) as r:
    #     with open('m01_conus.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # # Download Alaska, Caribbean and CONUS CSVs for Metop-B.
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/m02/csv/m02_alaska.csv')) as r:
    #     with open('m02_alaska.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/m02/csv/m02_caribbean.csv')) as r:
    #     with open('m02_caribbean.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m02/csv/m02_conus.csv')) as r:
    #     with open('m02_conus.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # # Download Alaska, Caribbean and CONUS CSVs for Metop-C.
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/alaska/sharppy/m03/csv/m03_alaska.csv')) as r:
    #     with open('m03_alaska.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/caribbean/sharppy/m03/csv/m03_caribbean.csv')) as r:
    #     with open('m03_caribbean.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)
    #
    # with closing(request.urlopen(f'https://geo.nsstc.nasa.gov/SPoRT/jpss-pg/nucaps/gridded/conus/sharppy/m03/csv/m03_conus.csv')) as r:
    #     with open('m03_conus.csv', 'wb') as f:
    #         shutil.copyfileobj(r, f)

def removeOldCSVs():
    # Remove old CSVs from HIDDEN_DSDIR before moving new CSVs to that directory.
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "j01_alaska.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "j01_alaska.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "npp_alaska.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "npp_alaska.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m01_alaska.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m01_alaska.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m02_alaska.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m02_alaska.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m02_alaska.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m03_alaska.csv"))

    if os.path.exists(os.path.join(HIDDEN_DSDIR, "j01_caribbean.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "j01_caribbean.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "npp_caribbean.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "npp_caribbean.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m01_caribbean.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m01_caribbean.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m02_caribbean.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m02_caribbean.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m03_caribbean.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m03_caribbean.csv"))

    if os.path.exists(os.path.join(HIDDEN_DSDIR, "j01_conus.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "j01_conus.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "npp_conus.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "npp_conus.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m01_conus.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m01_conus.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m02_conus.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m02_conus.csv"))
    if os.path.exists(os.path.join(HIDDEN_DSDIR, "m03_conus.csv")):
        os.remove(os.path.join(HIDDEN_DSDIR, "m03_conus.csv"))

def moveNewCSVs():
    # Move CSVs from SHARPPY_DIR to HIDDEN_DSDIR
    j01CSVs = glob.glob(os.path.join(SHARPPY_DIR, "j01*.csv"))
    for j01csv in j01CSVs:
        shutil.move(j01csv, HIDDEN_DSDIR)

    nppCSVs = glob.glob(os.path.join(SHARPPY_DIR, "npp*.csv"))
    for nppcsv in nppCSVs:
        shutil.move(nppcsv, HIDDEN_DSDIR)

    # m01CSVs = glob.glob(os.path.join(SHARPPY_DIR, "m01*.csv"))
    # for m01csv in m01CSVs:
    #     shutil.move(m01csv, HIDDEN_DSDIR)
    #
    # m02CSVs = glob.glob(os.path.join(SHARPPY_DIR, "m02*.csv"))
    # for m02csv in m02CSVs:
    #     shutil.move(m02csv, HIDDEN_DSDIR)
    #
    # m03CSVs = glob.glob(os.path.join(SHARPPY_DIR, "m03*.csv"))
    # for m03csv in m03CSVs:
    #     shutil.move(m03csv, HIDDEN_DSDIR)
