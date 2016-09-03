''' Frequently used meteorological constants '''

__all__ = ['MISSING', 'ROCP', 'ZEROCNK', 'G', 'TOL', 'WHITE', 'RED',
           'ORANGE', 'YELLOW', 'MAGENTA', 'DBROWN', 'LBROWN', 'LBLUE',
           'CYAN', 'BLACK', 'GREEN', 'DGREEN', 'HAINES_HIGH', 'HAINES_MID',
           'HAINES_LOW']

# Meteorological Constants
MISSING = -9999.0       # Missing Flag
ROCP = 0.28571426       # R over Cp
ZEROCNK = 273.15        # Zero Celsius in Kelvins
G = 9.80665             # Gravity
TOL = 1e-10             # Floating Point Tolerance

# Color code constants for easy access
WHITE = '#FFFFFF'
BLACK = '#000000'
RED = '#FF0000'
ORANGE = '#FF4000'
YELLOW = '#FFFF00'
MAGENTA = '#E700DF'
DBROWN = '#775000'
LBROWN = '#996600'
LBLUE = '#06B5FF'
CYAN = '#00FFFF'
GREEN = '#00FF00'
DGREEN = '#006000'

# Haines Index elevation constants for easy access
HAINES_HIGH = 2
HAINES_MID  = 1
HAINES_LOW  = 0


