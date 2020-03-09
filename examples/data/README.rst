This folder shows some example datasets that SHARPpy can read in using the code in sharppy.io

14061619.OAX - a file showing observed sounding data in the SPC tabular format (uses spc_decoder.py)
ABR.txt - MPAS point forecast sounding at the ABR site (uses pecan_decoder.py)
OUN.txt - NCAR Ensemble point forecast sounding (10 members) at OUN site (read in by pecan_decoder.py)
oun_rap.buf - a BUFKIT file showing the point forecast sounding for OUN (read in by buf_decoder.py)
bufkit_parameters.txt - a file describing the units and headers in the BUFKIT format

Note: the pecan_decoder formats in OUN.txt and ABR.txt are a simplified version of the BUFKIT format.
