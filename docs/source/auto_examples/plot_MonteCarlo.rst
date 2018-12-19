.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_plot_MonteCarlo.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_plot_MonteCarlo.py:


Estimating the uncertainty of convection indices
================================================






.. image:: /auto_examples/images/sphx_glr_plot_MonteCarlo_001.png
    :class: sphx-glr-single-img





.. code-block:: python


    import sharppy.sharptab as tab
    import numpy as np
    import os
    from sharppy.io.spc_decoder import SPCDecoder
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter, MultipleLocator
    import sharppy.plot.skew as skew
    np.random.seed(0)

    FILENAME = 'data/14061619.OAX'

    dec = SPCDecoder(FILENAME)
    profs = dec.getProfiles()
    stn_id = dec.getStnId()
    prof = profs._profs[""][0]
    dates = profs._dates

    idx = np.where((prof.tmpc != -9999) & (prof.dwpc != -9999))[0]
    prof = tab.profile.create_profile(pres=prof.pres[idx], hght=prof.hght[idx], tmpc=prof.tmpc[idx], dwpc=prof.dwpc[idx], wspd=prof.wspd[idx], \
                                      wdir=prof.wdir[idx], strictQC=False, profile='default', date=dates[0], missing=-9999)

    # RS-90 and RS-92 accuracy values (see ARM SONDE handbook)
    rand_sigma_rh = 2/2. # % RH (converts to 1-sigma)
    syst_sigma_rh = 3 # % RH
    rand_sigma_t = 0.15/2. #C (converts to 1-sigma)
    syst_sigma_t = 0.2 # C

    def perturb_radiosonde(prof, num_perts):
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

    def hypsometric(temp, alt, sfc_press_ts):
        R = 287. # J/kg*K
        temp = temp + 273.15
        g = 9.81 #m/s^2

        pres_arr = np.ones((temp.shape))
        pres_arr[0] = sfc_press_ts

        for l in np.arange(1,len(pres_arr.T),1):
            avg_temp = (temp[l] + temp[l-1])/2.
            delta_z = (alt[l-1] - alt[l])
            a = (g/(R*avg_temp))
            p_2 = pres_arr[l-1]
            pres_arr[l] = p_2*np.exp(a*delta_z)

        return pres_arr
 
    t_dist, q_dist = perturb_radiosonde(prof, 10000)
    Sop = np.ma.asarray(np.cov(np.hstack((t_dist, q_dist)).T))
    Xop = np.ma.concatenate((prof.tmpc, prof.wvmr))
    u,l,v = np.linalg.svd(Sop)
    Ssqrt = np.dot(np.dot(u, np.diag(np.sqrt(l))), v)

    num_samples = 300
    cape_values = np.empty(num_samples)

    fig = plt.figure(figsize=(12, 5))
    ax = plt.subplot(121, projection='skewx')
    ax2 = plt.subplot(122)
    ax.grid(True)
    plt.grid(True)

    ax.semilogy(prof.tmpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'r-', lw=2)
    ax.semilogy(prof.dwpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'g-', lw=2)

    for i in np.arange(num_samples):
        Z = np.random.normal(0,1, len(Xop))
        Z_hat = np.dot(Z, Ssqrt) + Xop
        pert_tmpc = Z_hat[:len(prof.tmpc)]
        pert_wvmr = Z_hat[len(prof.tmpc):]
        pert_pres = hypsometric(pert_tmpc, prof.hght, prof.pres[prof.sfc])
        pert_dwpc = tab.thermo.temp_at_mixrat(pert_wvmr, pert_pres)
 
        pert_prof = tab.profile.create_profile(pres=pert_pres, hght=prof.hght, tmpc=pert_tmpc, dwpc=pert_dwpc, wspd=prof.wspd, \
                                          wdir=prof.wdir, strictQC=False, profile='default', date=dates[0], missing=-9999)
        # Lift a parcel
        pcl = tab.params.parcelx(pert_prof, flag=1) 
        cape_values[i] = pcl.bplus

        #TODO: Plot the parcel trace and the pertrubed profile on a skew-T.
        ax.semilogy(pert_prof.tmpc[~pert_prof.tmpc.mask], pert_prof.pres[~pert_prof.tmpc.mask], 'r-', lw=.5)
        ax.semilogy(pert_prof.dwpc[~pert_prof.tmpc.mask], pert_prof.pres[~pert_prof.tmpc.mask], 'g-', lw=.5)

    # Plot the background variables
    presvals = np.arange(1000, 0, -10)
    # Disables the log-formatting that comes with semilogy
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_yticks(np.linspace(100,1000,10))
    ax.set_ylim(1050,100)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.set_xlim(-50,50)

    ax2.set_ylabel("Count")
    ax2.set_xlabel("CAPE [J/kg]")
    ax2.hist(cape_values, 20)#bins=np.arange(4000,6100,100))
    #ax2.set_xlim(4000,6000)
    plt.savefig('plot_montecarlo.png', bbox_inches='tight', dpi=180)

**Total running time of the script:** ( 1 minutes  15.539 seconds)


.. _sphx_glr_download_auto_examples_plot_MonteCarlo.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: plot_MonteCarlo.py <plot_MonteCarlo.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: plot_MonteCarlo.ipynb <plot_MonteCarlo.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
