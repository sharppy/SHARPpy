import warnings # Silence the warnings from SHARPpy
warnings.filterwarnings("ignore")
from pylab import *
import sys
import numpy as np
from io import StringIO
import sharppy
import sharppy.sharptab.profile as profile
import skew_axes
# Now make a simple example using the custom projection.
from matplotlib.ticker import ScalarFormatter, MultipleLocator
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.transforms as transforms
from matplotlib.axes import Axes
import matplotlib.transforms as transforms
import matplotlib.axis as maxis
import matplotlib.spines as mspines
import matplotlib.path as mpath
from matplotlib.projections import register_projection
import numpy as np
from matplotlib import gridspec
from sharppy.sharptab import winds, utils, params, thermo, interp
from sharppy.io.decoder import getDecoders

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

    for k in profs._profs.keys():
        all_prof = profs._profs[k]
        dates = profs._dates
        for i in range(len(all_prof)):
            prof = all_prof[i]
            new_prof = profile.create_profile(pres=prof.pres, hght=prof.hght, tmpc=prof.tmpc, dwpc=prof.dwpc, wspd=prof.wspd, \
                                              wdir=prof.wdir, strictQC=False, profile='convective', date=dates[i])
            return new_prof, dates[i], stn_id 
 
"""
    plot_sounding.py
    Author: Greg Blumberg (OU/CIMMS)
    Date Created: 4/14/2016

    This script was originally created to convert the "SHARPpy format" sounding files
    (really the text files similar to the SPC sounding text files found online) into a 
    simple image.  It was written to convert historical sounding files for the OWL 
    2016 spring chase case, and may be released in a future version of SHARPpy or 
    in an educational package to pull random historical severe weather cases for analysis.
    It could easily be used to create sounding images in bulk.

    To run this script, use the command line arguments:
        python plot_sounding.py <FILENAME>

    FILENAME is the file with the column formatted data (e.g. the OAX file).
    
    This script will plot a Skew-T with various lines using a similar color scheme that
    the SHARPpy GUI uses (red-temperature, green-dewpoint, cyan-wet bulb temperature, dashed-red virtual temp.)
    It also plots the MU parcel trace and LCL, LFC, and EL markers.  Also assumes observed data in the title.
        
    It also plots a hodograph with the RM and LM storm motion vectors on the hodograph, as well as the
    hodograph segments (0-3, 3-6, 6-9, 9-12 km) that SHARPpy uses (although with different colors). 

    This script also runs several SHARPpy routines on the data and plots the associated indices below the sounding.
    Users could change the routines that are run in this script to focus on specific indices that may be relevant
    to their research.

"""

# Bounds of the pressure axis 
pb_plot=1050
pt_plot=100
dp_plot=10
plevs_plot = np.arange(pb_plot,pt_plot-1,-dp_plot)
    
# Routine to plot the wind barbs.
def plot_wind_barbs(axes, p, u, v):
    for i in np.arange(0,len(p)):
        if (p[i] > pt_plot):
            if np.ma.is_masked(v[i]) is True:
                continue
            axes.barbs(0,p[i],u[i],v[i], length=7, clip_on=False, linewidth=1)

# Routine to draw the line for the wind barbs
def draw_wind_line(axes):
    wind_line = []
    for p in plevs_plot:
        wind_line.append(0)
    axes.semilogy(wind_line, plevs_plot, color='black', linewidth=.5)

# Routine to plot the axes for the wind profile
def plot_wind_axes(axes):
    # plot wind barbs
    draw_wind_line(axes)
    axes.set_axis_off()
    axes.axis([-1,1,pb_plot,pt_plot])

# Open up the text file with the data in columns (e.g. the sample OAX file distributed with SHARPpy)
prof, time, location = decode(sys.argv[1])
title = time.strftime('%Y%m%d/%H%M') + ' ' + location + '   (Observed)'

# Set up the figure in matplotlib.
fig = plt.figure(figsize=(9, 8))
#ax = plt.subplot2grid((4,4), (0,0), colspan=2, rowspan=4, projection='skewx')
gs = gridspec.GridSpec(4,4, width_ratios=[1,5,1,1])
#fig = plt.figure(1, figsize=(10, 8), dpi=300, edgecolor='k')
ax = plt.subplot(gs[0:3, 0:2], projection='skewx')
plt.title(title, fontsize=14, loc='left')
#ax.axes([])
ax.grid(True)
plt.grid(True)
# Plot the background variables
presvals = np.arange(1000, 0, -10)

# Routine to calculate the dry adiabats.
def thetas(theta, presvals):
    return ((theta + thermo.ZEROCNK) / (np.power((1000. / presvals),thermo.ROCP))) - thermo.ZEROCNK

### Plot some of the key lines for the Skew-T (dry adiabats, etc.) ###

# plot the dry adiabats
for t in np.arange(-50,210,10):
    ax.semilogy(thetas(t, presvals), presvals, 'r-', alpha=.2)

# plot the mixing ratio lines
for w in [2,4,10,12,14,16,18,20]:
    line = thermo.temp_at_mixrat(w, np.arange(1000,600,-1))
    ax.semilogy(line, np.arange(1000,600,-1), 'g--', lw=.7)

# plot the moist adiabats
for i in np.arange(-50,50,10):
    t = []
    for pres in np.arange(1000,90,-10):
        t.append(thermo.wetlift(1000,i,pres))
    ax.semilogy(t, np.arange(1000,90,-10), 'k', lw=1, alpha=0.5)


# Plot the data using normal plotting functions, in this case using
# log scaling in Y, as dicatated by the typical meteorological plot
print(prof.tmpc)
ax.semilogy(prof.tmpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'r', lw=2)
ax.semilogy(prof.dwpc[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'g', lw=2)
ax.semilogy(prof.vtmp[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'r--')
ax.semilogy(prof.wetbulb[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'c-')

# Plot the parcel trace, but this may fail.  If it does so, inform the user.
try:
    ax.semilogy(prof.mupcl.ttrace, prof.mupcl.ptrace, 'k--')
except:
    print("Couldn't plot parcel traces...")

# Plot LCL, LFC, EL labels (if it fails, inform the user.)
trans = transforms.blended_transform_factory(ax.transAxes, ax.transData)
try:    
    ax.text(0.90, prof.mupcl.lclpres, '- LCL', verticalalignment='center', transform=trans, color='k', alpha=0.7)
except:
    print("couldn't plot LCL")

if np.isfinite(prof.mupcl.lfcpres):
    ax.text(0.90, prof.mupcl.lfcpres, '- LFC', verticalalignment='center', transform=trans, color='k', alpha=0.7)
else:    
    print("couldn't plot LFC")

try:
    ax.text(0.90, prof.mupcl.elpres, '- EL', verticalalignment='center', transform=trans, color='k', alpha=0.7)
except:
    print("couldn't plot EL")

# Plot the height values on the skew-t, if there's an issue, inform the user.
for h in [1000,2000,3000,4000,5000,6000,9000,12000,15000]:
    p = interp.pres(prof, interp.to_msl(prof, h))
    try:
        ax.text(0.01, p, str(h/1000) +' km -', verticalalignment='center', fontsize=9, transform=trans, color='r')
    except:
        print("problem plotting height label:", h)

ax.text(0.01, prof.pres[prof.sfc], 'Sfc', verticalalignment='center', fontsize=9, transform=trans, color='r')

# Plot the effective inflow layer on the Skew-T, like with the GUI (TODO: include the effective SRH on the top like in the GUI).
ax.plot([0.2,0.3], [prof.ebottom, prof.ebottom], color='c', lw=2, transform=trans)
ax.plot([0.25,0.25], [prof.etop, prof.ebottom], color='c', lw=2, transform=trans)
ax.plot([0.2,0.3], [prof.etop, prof.etop], color='c', lw=2, transform=trans)

# Highlight the 0 C and -20 C isotherms.
l = ax.axvline(0, color='b', ls='--')
l = ax.axvline(-20, color='b', ls='--')

# Disables the log-formatting that comes with semilogy
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.set_yticks(np.linspace(100,1000,10))
ax.set_ylim(1050,100)
#ax.plot([10,20],[1000,1000], 'b')

# Draw the hodograph axes on the plot.
from mpl_toolkits.axes_grid.inset_locator import inset_axes
inset_axes = inset_axes(ax,width=1.7, # width = 30% of parent_bbox
                                    height=1.7, # height : 1 inch
                                    loc=1)
inset_axes.get_xaxis().set_visible(False)
inset_axes.get_yaxis().set_visible(False)

# Draw the range rings around the hodograph.
for i in range(10,90,10):
    circle = plt.Circle((0,0),i,color='k',alpha=.3, fill=False)
    if i % 10 == 0 and i <= 50:
        inset_axes.text(-i,2,str(i), fontsize=8, horizontalalignment='center')
    inset_axes.add_artist(circle)
inset_axes.set_xlim(-60,60)
inset_axes.set_ylim(-60,60)
inset_axes.axhline(y=0, color='k')
inset_axes.axvline(x=0, color='k')
srwind = params.bunkers_storm_motion(prof)

# Routine to plot the hodograph in segments (0-3 km, 3-6 km, etc.)
def plotHodo(axes, h, u, v, color='k'):
    for color, min_hght in zip(['r', 'g', 'b', 'k'], [3000,6000,9000,12000]):
        below_12km = np.where((h <= min_hght) & (h >= min_hght - 3000))[0]
        if len(below_12km) == 0:
            continue
        below_12km = np.append(below_12km, below_12km[-1] + 1)
        # Try except to ensure missing data doesn't cause this routine to fail.
        try:
            axes.plot(u[below_12km][~u.mask[below_12km]],v[below_12km][~v.mask[below_12km]], color +'-', lw=2)
        except:
            continue

# Plot the hodograph data.
plotHodo(inset_axes, prof.hght, prof.u, prof.v, color='r')
inset_axes.text(srwind[0], srwind[1], 'RM', color='r', fontsize=8)
inset_axes.text(srwind[2], srwind[3], 'LM', color='b', fontsize=8)

# Draw the wind barbs axis and everything that comes with it.
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.set_xlim(-50,50)
ax2 = plt.subplot(gs[0:3,2])
ax3 = plt.subplot(gs[3,0:3])
plot_wind_axes(ax2)
plot_wind_barbs(ax2, prof.pres, prof.u, prof.v)
gs.update(left=0.05, bottom=0.05, top=0.95, right=1, wspace=0.025)

# Calculate indices to be shown.  More indices can be calculated here using the tutorial and reading the params module.
p1km = interp.pres(prof, interp.to_msl(prof, 1000.))
p6km = interp.pres(prof, interp.to_msl(prof, 6000.))
sfc = prof.pres[prof.sfc]
sfc_1km_shear = winds.wind_shear(prof, pbot=sfc, ptop=p1km)
sfc_6km_shear = winds.wind_shear(prof, pbot=sfc, ptop=p6km)
srh3km = winds.helicity(prof, 0, 3000., stu = srwind[0], stv = srwind[1])
srh1km = winds.helicity(prof, 0, 1000., stu = srwind[0], stv = srwind[1])
scp = params.scp(prof.mupcl.bplus, prof.right_esrh[0], prof.ebwspd)
stp_cin = params.stp_cin(prof.mlpcl.bplus, prof.right_esrh[0], prof.ebwspd, prof.mlpcl.lclhght, prof.mlpcl.bminus)
stp_fixed = params.stp_fixed(prof.sfcpcl.bplus, prof.sfcpcl.lclhght, srh1km[0], utils.comp2vec(prof.sfc_6km_shear[0], prof.sfc_6km_shear[1])[1])
ship = params.ship(prof)

# A routine to perform the correct formatting when writing the indices out to the figure.
def fmt(value, fmt='int'):
    if fmt == 'int':
        try:
            val = int(value)
        except:
            val = str("M")
    else:
        try:
            val = round(value,1)
        except:
            val = "M"
    return val

# Setting a dictionary that is a collection of all of the indices we'll be showing on the figure.
# the dictionary includes the index name, the actual value, and the units.
indices = {'SBCAPE': [fmt(prof.sfcpcl.bplus), 'J/kg'],\
           'SBCIN': [fmt(prof.sfcpcl.bminus), 'J/kg'],\
           'SBLCL': [fmt(prof.sfcpcl.lclhght), 'm AGL'],\
           'SBLFC': [fmt(prof.sfcpcl.lfchght), 'm AGL'],\
           'SBEL': [fmt(prof.sfcpcl.elhght), 'm AGL'],\
           'SBLI': [fmt(prof.sfcpcl.li5), 'C'],\
           'MLCAPE': [fmt(prof.mlpcl.bplus), 'J/kg'],\
           'MLCIN': [fmt(prof.mlpcl.bminus), 'J/kg'],\
           'MLLCL': [fmt(prof.mlpcl.lclhght), 'm AGL'],\
           'MLLFC': [fmt(prof.mlpcl.lfchght), 'm AGL'],\
           'MLEL': [fmt(prof.mlpcl.elhght), 'm AGL'],\
           'MLLI': [fmt(prof.mlpcl.li5), 'C'],\
           'MUCAPE': [fmt(prof.mupcl.bplus), 'J/kg'],\
           'MUCIN': [fmt(prof.mupcl.bminus), 'J/kg'],\
           'MULCL': [fmt(prof.mupcl.lclhght), 'm AGL'],\
           'MULFC': [fmt(prof.mupcl.lfchght), 'm AGL'],\
           'MUEL': [fmt(prof.mupcl.elhght), 'm AGL'],\
           'MULI': [fmt(prof.mupcl.li5), 'C'],\
           '0-1 km SRH': [fmt(srh1km[0]), 'm2/s2'],\
           '0-1 km Shear': [fmt(utils.comp2vec(sfc_1km_shear[0], sfc_1km_shear[1])[1]), 'kts'],\
           '0-3 km SRH': [fmt(srh3km[0]), 'm2/s2'],\
           '0-6 km Shear': [fmt(utils.comp2vec(sfc_6km_shear[0], sfc_6km_shear[1])[1]), 'kts'],\
           'Eff. SRH': [fmt(prof.right_esrh[0]), 'm2/s2'],\
           'EBWD': [fmt(prof.ebwspd), 'kts'],\
           'PWV': [round(prof.pwat, 2), 'inch'],\
           'K-index': [fmt(params.k_index(prof)), ''],\
           'STP(fix)': [fmt(stp_fixed, 'flt'), ''],\
           'SHIP': [fmt(ship, 'flt'), ''],\
           'SCP': [fmt(scp, 'flt'), ''],\
           'STP(cin)': [fmt(stp_cin, 'flt'), '']}

# List the indices within the indices dictionary on the side of the plot.
trans = transforms.blended_transform_factory(ax.transAxes,ax.transData)

# Write out all of the indices to the figure.
print("##############")
print("   INDICES    ")
print("##############")
string = ''
keys = np.sort(list(indices.keys()))
x = 0
counter = 0
for key in keys:
    string = string + key + ': ' + str(indices[key][0]) + ' ' + indices[key][1] + '\n'
    print(key + ": " + str(indices[key][0]) + ' ' + indices[key][1])
    if counter < 7:
        counter += 1
        continue
    else:
        counter = 0
        ax3.text(x, 1, string, verticalalignment='top', transform=ax3.transAxes, fontsize=11)
        string = ''
        x += 0.3
ax3.text(x, 1, string, verticalalignment='top', transform=ax3.transAxes, fontsize=11)
ax3.set_axis_off()

# Show SARS matches (edited for Keith Sherburn)
try:
    supercell_matches = prof.supercell_matches
    hail_matches = prof.matches 
except:
    supercell_matches = prof.right_supercell_matches
    hail_matches = prof.right_matches
"""
print
print "#############"
print " SARS OUTPUT "
print "#############"
for mtype, matches in zip(['Supercell', 'Hail'], [supercell_matches, hail_matches]):
    print mtype
    print '-----------'
    if len(matches[0]) == 0:
        print "NO QUALITY MATCHES"
    for i in range(len(matches[0])):
        print matches[0][i] + ' ' + matches[1][i]
    print "Total Loose Matches:", matches[2]
    print "# of Loose Matches that met Criteria:", matches[3]
    print "SVR Probability:", matches[4]
    print 
"""
# Finalize the image formatting and alignments, and save the image to the file.
gs.tight_layout(fig)
fn = time.strftime('%Y%m%d.%H%M') + '_' + location + '.png'
fn = fn.replace('/', '')
print("SHARPpy Skew-T image output at:", fn)
plt.savefig(fn, bbox_inches='tight', dpi=180)


