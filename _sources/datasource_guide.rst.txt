.. _Custom_Data_Sources:

Custom Data Sources
===================

Sometimes, you may want to load your own custom data into SHARPpy.

This section of the documentation covers just that.

Valid Data Formats
^^^^^^^^^^^^^^^^^^

SHARPpy hosts a variety of decoders within the :ref:`sharppy.io` to help decode various human-readable text files:

.. csv-table:: SHARPpy Decoders
    :header: "Name", "Data Type"
    :widths: 20,50
    
    "buf_decoder.py", "BUFKIT files which includes deterministic and ensemble point forecast soundings"
    "pecan_decoder.py", "Point forecast soundings for deterministic and ensemble models"
    "spc_decoder.py", "Observed soundings"
    "uwyo_decoder.py", "University of Wyoming sounding archive text format"

All decoders in the SHARPpy program inherit from the Decoder class described in :ref:`sharppy.io`.  Each decoder
returns a ProfCollection object, which contains Profile objects generated from the extended Decoder class.
For example, the SPCDecoder returns a ProfileCollection object with only one Profile object, as the SPCDecoder
reads in data files meant for only observed soundings.

Examples of these various input files may be found within the `examples/data` folder.


**Notes about the SPC file format:**

While SHARPpy can be configured to accept multiple different sounding formats, the tabular (or SPC format) format is the most common format used.  This text file format requires several tags (%TITLE%, %RAW%, and %END%) to indicate where the header information is for the sounding and where the actual data is kept in the file.

The header format should be of this format, where SITEID is the three or four letter identifier and YYMMDD/HHMM is the 2-letter year, month, day, hour, and minute time of the sounding.  LAT, LON denote the latitude and longitude of the sounding - SHARPpy uses this information for hemispheric-dependent calculations.  "..." is where the sections of the file ends and continues in this example and are not included in the actual data file:

::

  %TITLE%
   SITEID   YYMMDD/HHMM LAT,LON

     LEVEL       HGHT       TEMP       DWPT       WDIR       WSPD
  -------------------------------------------------------------------
  ...

The data within the file should be of the format (Pressure [mb], Height MSL [m], Temperature [C], Dewpoint [C], Wind Direction [deg], Wind Speed [kts]).  If the temperature, dewpoint, wind direction, or wind direction values are all set to -9999 (such as in the example below), SHARPpy will treat that isobaric level as being below the ground.  -9999 is the placeholder for missing data:


::

  ...
  %RAW%
   1000.00,    34.00,  -9999.00,  -9999.00,  -9999.00,  -9999.00
   965.00,    350.00,     27.80,     23.80,    150.00,     23.00
   962.00,    377.51,     27.40,     22.80,  -9999.00,  -9999.00
  %END%

Upon loading the data into the SHARPpy GUI, the program first does several checks on the integrity of the data.  As many of the program's routines are repeatedly checked, incorrect or bad values from the program are usually a result of the quality of the data.  The program operates on the principle that if the data is good, all the resulting calculations will be good.  Some of the checks include:

1. Making sure that no temperature or dewpoint values are below 273.15 K.
2. Ensuring that wind speed and wind direction values are WSPD ≥ 0 and 0 ≤ WDIR < 360, respectively.
3. Making sure that no repeat values of pressure or height occur.
4. Checking to see that pressure decreases with height within the profile.

The GUI should provide an error message explaining the variable type (e.g., wind speed, height) that is failing these checks.  As of version 1.4, the GUI will try to plot the data should the user desire.


Loading in Sounding Data Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SHARPpy supports opening up multiple observed sounding data files in the sounding window.  While in the SHARPpy Sounding Picker, use File->Open menu to open up your text file in the sounding window.  With each file, SHARPpy will search through the list of decoders in the :ref:`sharppy.io` to find the correct one for your file.  Example files to test this are included in the `examples/data` folder.

Adding Custom Data Sources
^^^^^^^^^^^^^^^^^^^^^^^^^^

Although SHARPpy maintains a variety of different sounding data sources in the distributed program, you may want to add your own to the program.  In the past, the developers have incorporated datastreams from other experimental NWP runs including the `MPAS <https://mpas-dev.github.io>`_ and the `NCAR Realtime Ensemble <https://ensemble.ucar.edu>`_ into the program.  We welcome the opportunity to expand the set of sounding data sources available to the general SHARPpy user base.

To do this, add to the `datasources/` directory an XML file containing the data source information and a CSV file containing all the location information.  We do not recommend modifying the `standard.xml` file, as it may break SHARPpy, and your custom data source information may get overwritten when you update SHARPpy.  If you have a reliable data source that you wish to share with the broader community, please consider submitting a pull request with your proposed changes to Github!

1. Make your sounding data files.  You may wish to use either the SPC format, the BUFKIT format, or the PECAN format.  You may wish to store these locally or on a server.  Either way, they should be viewable by login credentials you will be using when running the SHARPpy GUI.

2. Make a new XML file
The XML file contains the information for how the data source behaves. Questions like "Is this data source an ensemble?" or "How far out does this data source forecast?" are answered in this file. It should be a completely new file.  It can be named whatever you like, as long as the extension is `.xml`. The format should look like the `standard.xml` file in the `datasources/` directory, but an example follows:

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8" standalone="no" ?>
  <sourcelist>
      <datasource name="My Data Source" observed="false" ensemble="false">
          <outlet name="My Server" url="http://www.example.com/myprofile_{date}{cycle}_{srcid}.buf" format="bufkit" >
              <time range="24" delta="1" cycle="6" offset="0" delay="2" archive="24" start="2012/04/01" end="now"/>
              <points csv="mydatasource.csv" />
          </outlet>
      </datasource>
  </sourcelist>

For the ``outlet`` tag:

* ``url``: The URL for the profiles. The names in curly braces are special variables that SHARPpy fills in the following manner:
    * ``date``: The current date in YYMMDD format (e.g. 150602 for 2 June 2015).
    * ``cycle``: The current cycle hour in HHZ format (e.g. 00Z).
    * ``srcid``: The source's profile ID (will be filled in with the same column from the CSV file; see below).
    * ``day``: The day of the data (not shown)
    * ``hour``: the hour of the data (not shown)
    * ``month``: the month of the data (not shown)
    * ``year``: the year of the data (not shown)
* ``name``: A name for the data source outlet
* ``format``: The format of the data source.  Currently, the only supported formats are `bufkit` and `pecan` for model profiles and `spc` for observed profiles. Others may be available in the future.

For the ``time`` tag:

* ``range``: The forecast range in hours for the data source. Observed data sources should set this to 0.
* ``delta``: The time step in hours between profiles. Observed data sources should set this to 0.
* ``cycle``: The amount of time in hours between cycles for the data source.
* ``offset``: The time offset in hours of the cycles from 00 UTC.
* ``delay``: The time delay in hours between the cycle and the data becoming available.
* ``archive``: The length of time in hours that data are kept on the server.

These should all be integer numbers of hours; support for sub-hourly data is forthcoming.

* ``start``: A start date of the data in the outlet "YYYY/MM/DD", "now", or "-"
* ``end``: A end date of the data in the outlet "YYYY/MM/DD", "now", or "-"

These two tags are used to grey out parts of the Calendar that is shown on the Sounding Picker.
For example, a sounding archive in SHARPpy may have a start date of "1946/01/01" and an end value
of "now" as the archive keeps growing.  If these tags are not specified, or "-" is used for the
``start`` and ``end``, then dates outside those available or determined by the ``archive`` value
are greyed out.

3. Make a new CSV file
The CSV file contains information about where your profiles are located and what the locations are called. It should look like the following:

::

  icao,iata,synop,name,state,country,lat,lon,elev,priority,srcid
  KTOP,TOP,72456,Topeka/Billard Muni,KS,US,39.08,-95.62,268,3,ktop
  KFOE,FOE,,Topeka/Forbes,KS,US,38.96,-95.67,320,6,kfoe
  ...

The only columns that are strictly required are the ``lat``, ``lon``, and ``srcid`` columns.  The rest must be present, but can be left empty. However, SHARPpy will use as much information as it can get to make a pretty name for the station on the picker map.

*Optional*

4. Run ``python setup.py install``
This will install your new data source and allow SHARPpy to find it. If the installation was successful, you should see it in the "Data Sources" drop-down menu.  You should only do this step if you have edited the `datasources/` directory underneath the root of the SHARPpy Github directory.  If you made these modifications within the `~/.sharppy` directory, you will not need to do this step.

