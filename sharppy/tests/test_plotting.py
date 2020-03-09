import pytest
matplotlib = pytest.importorskip('matplotlib')
#import matplotlib
matplotlib.use('Agg')
import sharppy.io.spc_decoder as spc_decoder
import sharppy.plot.skew as skew
import sharppy.sharptab.profile as profile
from matplotlib.ticker import ScalarFormatter, MultipleLocator
from matplotlib.collections import LineCollection
import matplotlib.transforms as transforms
from matplotlib import gridspec
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

"""
    Unit tests to test to see if decoders work on different file types
"""
files = ['examples/data/14061619.OAX']
 
def test_plotting():
   
    dec = spc_decoder.SPCDecoder(files[0])
    profs = dec.getProfiles()
    stn_id = dec.getStnId()

    print(profs) 
    all_profs = profs._profs
    print(all_profs)
    prof = all_profs[''][0]
    dates = profs._dates
    print(dates)
    prof = profile.create_profile(pres=prof.pres, hght=prof.hght, tmpc=prof.tmpc, dwpc=prof.dwpc, wspd=prof.wspd, \
                                      wdir=prof.wdir, strictQC=False, profile='convective', date=dates[0])
    time = dates[0]
    location = "OAX"
    pb_plot=1050
    pt_plot=100
    dp_plot=10
    plevs_plot = np.arange(pb_plot,pt_plot-1,-dp_plot)
    # Open up the text file with the data in columns (e.g. the sample OAX file distributed with SHARPpy)
    title = time.strftime('%Y%m%d/%H%M') + ' ' + location + '   (Observed)'

    # Set up the figure in matplotlib.
    fig = plt.figure(figsize=(9, 8))
    gs = gridspec.GridSpec(4,4, width_ratios=[1,5,1,1])
    ax = plt.subplot(gs[0:3, 0:2], projection='skewx')
    skew.draw_title(ax, title)
    skew.draw_dry_adiabats(ax)
    skew.draw_mixing_ratio_lines(ax)
    skew.draw_moist_adiabats(ax)
    skew.draw_heights(ax, prof)
    skew.draw_effective_inflow_layer(ax, prof)
    
    ax.grid(True)
    plt.grid(True)

    # Plot the background variables
    presvals = np.arange(1000, 0, -10)

    ax.semilogy(prof.tmpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'r', lw=2)
    ax.semilogy(prof.dwpc[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'g', lw=2)
    ax.semilogy(prof.vtmp[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'r--')
    ax.semilogy(prof.wetbulb[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'c-')

    # Plot the parcel trace, but this may fail.  If it does so, inform the user.
    try:
        ax.semilogy(prof.mupcl.ttrace, prof.mupcl.ptrace, 'k--')
    except:
        print("Couldn't plot parcel traces...")
    
    skew.plot_sig_levels(ax, prof)

    # Highlight the 0 C and -20 C isotherms.
    l = ax.axvline(0, color='b', ls='--')
    l = ax.axvline(-20, color='b', ls='--')

    # Disables the log-formatting that comes with semilogy
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_yticks(np.linspace(100,1000,10))
    ax.set_ylim(1050,100)

    # Plot the hodograph data.
    inset_axes = skew.draw_hodo_inset(ax, prof)
    skew.plotHodo(inset_axes, prof.hght, prof.u, prof.v, color='r')
    #inset_axes.text(srwind[0], srwind[1], 'RM', color='r', fontsize=8)
    #inset_axes.text(srwind[2], srwind[3], 'LM', color='b', fontsize=8)

    # Draw the wind barbs axis and everything that comes with it.
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.set_xlim(-50,50)
    ax2 = plt.subplot(gs[0:3,2])
    ax3 = plt.subplot(gs[3,0:3])
    skew.plot_wind_axes(ax2)
    skew.plot_wind_barbs(ax2, prof.pres, prof.u, prof.v)
    gs.update(left=0.05, bottom=0.05, top=0.95, right=1, wspace=0.025)
    #plt.show()


test_plotting()
