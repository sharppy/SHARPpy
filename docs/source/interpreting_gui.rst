.. _Interpreting_with_the_GUI:

Interpreting the GUI
========================

`Blumberg et al. 2017 <http://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-15-00309.1>`_ provides an overview of the various insets and information included in the SHARPpy sounding window.  Included within the paper is a list of references to journal articles which describe the relevance of each aspect of the SHARPpy sounding window to research in atmospheric science and the scientific forecasting process.

Additional resources for interpreting the GUI include the `SPC Sounding Analysis Help <http://www.spc.noaa.gov/exper/soundings/help/>`_ and `Explanation of SPC Severe Weather Parameters <http://www.spc.noaa.gov/sfctest/help/sfcoa.html>`_ webpages.  The first site describes the SHARP GUI, which is the basis for the SHARPpy GUI.  The second can be used to help interpret some of the various convection indices shown in the SHARPpy GUI.  Not all features shown on these two sites are shown in the SHARPpy GUI.

Skew-T
------

Various profiles are displayed in the Skew-T:

    * Solid red – temperature profile
    * Solid green – dewpoint profile
    * Dashed red – virtual temperature profile.
    * Cyan – wetbulb temperature profile
    * Dashed white – parcel trace (e.g., MU, SFC, ML) (the parcel trace of the parcel highlighted in yellow in the Thermodynamic Inset (I).
    * Dashed purple – downdraft parcel trace (parcel origin height is at minimum 100-mb mean layer equivalent potenial temperature).
    * Winds are in knots (unless switched i the preferences) and are interpolated to 50-mb intervals for visibility purposes.
    * If a vertical velocity profile (omega) is found (e.g., sounding is from a model), it is plotted on the left. Blue bars indicate sinking motion, red bars rising motion. Dashed purple lines indicate the bounds of synopic scale vertical motion.

Parcel LCL, LFC, and EL are denoted on the right-hand side in green, yellow and purple, respectively.

.. image:: tutorial_imgs/effective_inflow.png
    :scale: 30%
    :align: center

Information about the effective inflow layer may be found in `Thompson et al. 2007 <https://www.spc.noaa.gov/publications/thompson/effective.pdf>`_.

Wind Speed Profile
------------------

.. figure:: tutorial_imgs/wind_speed_height.png
    :scale: 30%
    :align: center

    The tick marks for this plot are every 20 knots (should knots be the default unit selected in the preferences).

Inferred Temperature Advection Profile
--------------------------------------

.. image:: tutorial_imgs/temp_adv_height.png
    :scale: 30%
    :align: center

Hodograph
---------

Although the hodograph plotted follows the traditional convention used throughout meteorology, the hodograph shown here is broken up into layers by color.  In addition, several vectors are also plotted from different SHARPpy algorithms.

Bunkers Storm Motion Vectors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: tutorial_imgs/hodograph_bunkers.png
    :scale: 30%
    :align: center

The storm motion vectors here are computed using the updated `Bunkers et al. 2014 <http://www.weather.gov/media/unr/soo/scm/2014-JOM11.pdf>`_ algorithm, which takes into account the effective inflow layer.


Corfidi Vectors
^^^^^^^^^^^^^^^

.. figure:: tutorial_imgs/hodograph_corfidi.png
    :scale: 30%
    :align: center

The Corfidi vectors may be used to estimate mesoscale convective system (MCS) motion.  See `Corfidi 2003 <https://www.spc.noaa.gov/publications/corfidi/mcs2003.pdf>`_ for more information about how these are calculated.

LCL-EL Mean Wind
^^^^^^^^^^^^^^^^

.. figure:: tutorial_imgs/hodograph_mean_wind.png
    :scale: 30%
    :align: center

Critical Angle
^^^^^^^^^^^^^^

.. figure:: tutorial_imgs/hodograph_critical.png
    :scale: 30%
    :align: center

See `Esterheld and Guiliano 2008 <http://www.ejssm.org/ojs/index.php/ejssm/article/view/33>`_ for more information on the use of critical angle in forecasting.

Storm Slinky
------------

.. image:: tutorial_imgs/slinky_description.png
    :scale: 30%
    :align: center

Examples
^^^^^^^^

.. image:: tutorial_imgs/slinky_supercell.png
    :scale: 30%
    :align: center

.. image:: tutorial_imgs/slinky_single_cell.png
    :scale: 30%
    :align: center

.. image:: tutorial_imgs/slinky_warning.png
    :scale: 30%
    :align: center

Theta-E w/ Pressure
-------------------

.. image:: tutorial_imgs/theta-e.png
    :scale: 30%
    :align: center

See `Atkins and Wakimoto 1991 <https://journals.ametsoc.org/doi/pdf/10.1175/1520-0434%281991%29006%3C0470%3AWMAOTS%3E2.0.CO%3B2>`_ for more information on what to look for in this inset when forecasting wet microbursts. 

Storm-Relative Winds w/ Height
------------------------------

.. image:: tutorial_imgs/srw.png
    :scale: 30%
    :align: center

See `Rasmussen and Straka 1998 <https://journals.ametsoc.org/doi/pdf/10.1175/1520-0493%281998%29126%3C2406%3AVISMPI%3E2.0.CO%3B2>`_ for more information on how the anvil-level storm relative winds may be used to predict supercell morphology.  See `Thompson et al. 2003 <https://www.spc.noaa.gov/publications/thompson/ruc_waf.pdf>`_ for information on using the 4-6 km storm-relative winds to predict tornado environments. 

Possible Hazard Type
--------------------

.. image:: tutorial_imgs/pht.png
    :scale: 30%
    :align: center

Flowchart
^^^^^^^^^

.. image:: tutorial_imgs/pht_flowchart.png
    :scale: 30%
    :align: center

