import requests
from sharppy._version import get_versions
from dateutil import parser

## Code to check to see if this version of SHARPpy is the most recent one.

__version__ = get_versions()['version']
ver = get_versions() # A dictionary with the date of the most recent commit.
del get_versions

# SEE https://developer.github.com/v3/repos/releases/
url = 'https://api.github.com/repos/sharppy/SHARPpy/releases/latest'

def get_latest_ver():
    response = requests.get(url)

    # Raise an exception if the API call fails.
    response.raise_for_status()

    data = response.json()
    return data

def get_tag_name(data):
    return data['tag_name']

def get_url(data):
    return data['html_url']

def compare_versions(data):
    # Checks to see if the publication date of the most recent Github Release
    # is less than the current version's date.
    ver_date = parser.parse(ver['date'])
    latest_date = parser.parse(data['published_at'])
#    print(ver_date, latest_date)
    return isLatest(ver_date, latest_date)

def isLatest(cur, github):
    return cur >= github

def check_latest():
    data = get_latest_ver()
    latest = compare_versions(data)
    html_url = get_url(data)
    tag_name = get_tag_name(data)
    return latest, tag_name, html_url

#   latest = check_latest()
