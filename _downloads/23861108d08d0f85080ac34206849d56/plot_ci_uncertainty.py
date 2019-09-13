"""
Estimating the uncertainty of convection indices
================================================

This example uses the SHARPpy functions to estimate the uncertainty inherent within
convection indices.  It uses Monte Carlo sampling and estimates of the systematic and 
random errors contained within Vaisala RS-90/92 radiosonde measurements.  

This methodology and code is was used in `Blumberg et al. 2017, JAMC`__ to demonstrate
the uncertainty of convection indices within radiosonde measurements and AERI retrievals.

.. _link: https://journals.ametsoc.org/doi/10.1175/JAMC-D-17-0036.1
__ link_

"""

import sharppy.sharptab as tab
import numpy as np
import os
from sharppy.io.spc_decoder import SPCDecoder
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import sharppy.plot.skew as skew
np.random.seed(0)

FILENAME = 'data/14061619.OAX'

# Read in the sounding data and generate a Profile object
dec = SPCDecoder(FILENAME)
profs = dec.getProfiles()
stn_id = dec.getStnId()
prof = profs._profs[""][0]
dates = profs._dates

# Get rid of all of the missing data
idx = np.where((prof.tmpc != -9999) & (prof.dwpc != -9999))[0]
prof = tab.profile.create_profile(pres=prof.pres[idx], hght=prof.hght[idx], tmpc=prof.tmpc[idx], dwpc=prof.dwpc[idx], wspd=prof.wspd[idx], \
                                  wdir=prof.wdir[idx], strictQC=False, profile='default', date=dates[0], missing=-9999)

deterministic_cape = tab.params.parcelx(prof, flag=1).bplus
print("Deterministic SBCAPE:", deterministic_cape)

# RS-90 and RS-92 accuracy values (see ARM SONDE handbook)
rand_sigma_rh = 2/2. # % RH (converts to 1-sigma)
syst_sigma_rh = 3 # % RH
rand_sigma_t = 0.15/2. #C (converts to 1-sigma)
syst_sigma_t = 0.2 # C

def perturb_radiosonde(prof, num_perts):
    '''
        Pertrub the radiosonde profiles to generate data to create a covariance matrix

        Parameters
        ----------
        prof : profile, object
            Profile object
        num_perts : number
            Number of perturbations to perform
        
        Returns
        -------
        new_t : array_like
            2D array showing the pertrubed temperature profiles (C)
        new_q : array_like
            2D array showing the pertrubed water vapor mixing ratio profiles (g/kg)
    '''
    new_t = np.empty((num_perts,len(prof.tmpc)))
    new_q = np.empty((num_perts,len(prof.tmpc)))
    for i in range(num_perts):
        new_t[i,:] = prof.tmpc + (syst_sigma_t*np.random.normal(0, 1, 1)) + (rand_sigma_t*np.random.normal(0, 1, len(prof.tmpc)))
        rh_sample =  prof.relh + (syst_sigma_rh*np.random.normal(0, 1, 1)) + (rand_sigma_rh*np.random.normal(0, 1, len(prof.tmpc)))
        idx = np.where(rh_sample < 0)[0]
        rh_sample[idx] = 0.000001
        idx = np.where(rh_sample > 100)[0]
        rh_sample[idx] = 100
        e_s = tab.thermo.vappres(prof.tmpc)
        
        new_q[i,:] = tab.thermo.mixratio(prof.pres, tab.thermo.temp_at_vappres((rh_sample/100.) * e_s))
        #plt.plot(new_q[i,:], prof.hght)
        #plt.show()
    return new_t, new_q

def hypsometric(temp, alt, sfc_pres):
    '''
        Calculate the pressure profile using the hypometric equation

        Parameters
        ----------
        temp : array_like
            Temperature profile in C
        alt : array_like
            Height array in m
        sfc_pres : number
            Surface pressure value in hPa

        Returns
        -------
        pres : array_like
            The pressure array in hPa
    '''
    R = 287. # J/kg*K
    temp = tab.thermo.ctok(temp)
    g = 9.81 #m/s^2

    pres_arr = np.ones((temp.shape))
    pres_arr[0] = sfc_pres

    for l in np.arange(1,len(pres_arr.T),1):
        avg_temp = (temp[l] + temp[l-1])/2.
        delta_z = (alt[l-1] - alt[l])
        a = (g/(R*avg_temp))
        p_2 = pres_arr[l-1]
        pres_arr[l] = p_2*np.exp(a*delta_z)

    return pres_arr

# Generate the error covariance matrix for the sounding 
t_dist, q_dist = perturb_radiosonde(prof, 10000)
Sop = np.ma.asarray(np.cov(np.hstack((t_dist, q_dist)).T))
Xop = np.ma.concatenate((prof.tmpc, prof.wvmr))
u,l,v = np.linalg.svd(Sop)
Ssqrt = np.dot(np.dot(u, np.diag(np.sqrt(l))), v)

num_samples = 300
cape_values = np.empty(num_samples)

# Make a figure to show the soundings from the Monte Carlo sampling and the distribution of CAPE
fig = plt.figure(figsize=(12, 5))
ax = plt.subplot(121, projection='skewx')
ax2 = plt.subplot(122)
ax.grid(True)
plt.grid(True)

# Plot the "deterministic" sounding 
ax.semilogy(prof.tmpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'r-', lw=2)
ax.semilogy(prof.dwpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'g-', lw=2)

for i in np.arange(num_samples):
    # Monte Carlo sample the data
    Z = np.random.normal(0,1, len(Xop))
    Z_hat = np.dot(Z, Ssqrt) + Xop

    # Get the perturbed temperature and water vapor profiles
    pert_tmpc = Z_hat[:len(prof.tmpc)]
    pert_wvmr = Z_hat[len(prof.tmpc):]

    # Calculate the new pressure profile using the hypsometric equation and calculate the dewpoint.
    pert_pres = hypsometric(pert_tmpc, prof.hght, prof.pres[prof.sfc])
    pert_dwpc = tab.thermo.temp_at_mixrat(pert_wvmr, pert_pres)

    # Create a BasicProfile object using the perturbed sounding data 
    pert_prof = tab.profile.create_profile(pres=pert_pres, hght=prof.hght, tmpc=pert_tmpc, dwpc=pert_dwpc, wspd=prof.wspd, \
                                      wdir=prof.wdir, strictQC=False, profile='default', date=dates[0], missing=-9999)
    # Lift a parcel
    pcl = tab.params.parcelx(pert_prof, flag=1) 
    cape_values[i] = pcl.bplus

    #TODO: Plot the parcel trace and the pertrubed profile on a skew-T.
    ax.semilogy(pert_prof.tmpc[~pert_prof.tmpc.mask], pert_prof.pres[~pert_prof.tmpc.mask], 'r-', lw=.5)
    ax.semilogy(pert_prof.dwpc[~pert_prof.tmpc.mask], pert_prof.pres[~pert_prof.tmpc.mask], 'g-', lw=.5)

print("Probablisitic SBCAPE (25,50,75th percentiles):", np.percentile(cape_values, (25,50,75)))
# Label and format the axes
presvals = np.arange(1000, 0, -10)
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.set_yticks(np.linspace(100,1000,10))
ax.set_ylim(1050,100)
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.set_xlim(-50,50)
ax.set_ylabel("Pressure [mb]")
ax.set_xlabel("Temperature [C]")
ax2.set_ylabel("Count")
ax2.set_xlabel("SBCAPE [J/kg]")
ax2.hist(cape_values, 15)

# Plot the data
plt.savefig('plot_ci.png', bbox_inches='tight', dpi=180)
