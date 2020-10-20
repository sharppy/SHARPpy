import shutil
from contextlib import closing
import urllib.request as request
import numpy as np
import glob as glob
import os
import requests
from bs4 import BeautifulSoup
import re

# Download CSV for all satellites and regions.
# CSVs will go in /home/<user>/.sharppy/datasources
def downloadCSV():
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

## MAIN ##
downloadCSV()
