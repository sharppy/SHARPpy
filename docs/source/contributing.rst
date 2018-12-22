.. _Contributing_:

Contributing
============

Welcome to the SHARPpy project!  We are eager to hear that you are interested
in contributing to the development of this community tool.  

So, you'd like to contribute to the SHARPpy project, eh?  What the heck is a pull request, anyways?  Regardless of your coding experience, congratulations!  You've take the first step to helping grow something incredible.  SHARPpy exists in its current state today largely because of public contributions to the project.  

If you are a first-time contributor (or even a seasoned one), you may want to read up on how people can contribute to open-source projects.  Below are some links you may find helpful!

* `How Junior Developers Can Contribute to Open Source Projects <https://rubygarage.org/blog/how-contribute-to-open-source-projects>`_
* `How to Contribute! <https://opensource.guide/how-to-contribute/>`_

We appreciate your contributions to the program and wish you well in your coding!

Some Norms 
^^^^^^^^^^

Contributions to the program should follow some norms and need to align with the broader philosophy of SHARPpy:

1. Input and output files for SHARPpy must be human readable text.  We are actively trying to avoid using a binary file format in SHARPpy because we do not want to force users to use SHARPpy to read, write, or understand their data.  In particular, we do not want data files floating around the Internet that require you to install SHARPpy to know what's in them.  We believe that the capability of viewing your data should not come with an additional software dependency. 
2. A primary philosophy of the SHARPpy program is that the routines should not modify the data provided by the user.  For example, SHARPpy does not run quality control routines to clean up the data prior to lifting parcels.  This philosophy tries to minimize the number of steps in data analysis and places the responsiblity of quality control in the hands of the user.  Your code should not do unexpected things to your data!
3. SHARPpy attempts to help resolve the reproduceabiltiy crisis in science.  Additions should attempt to cite source material in the docstrings in order to encourage tracable science.  As SHARPpy was inspired by the differences inherent in sounding lifting routines, it aims to provide a source of routines that have been used widely across the science (SHARPpy is descended from SHARP-95).
3. Small, incremental pull requests are desired as they allow the community (and other developers) to adapt their code to new changes in the codebase.
4. If you want to make a large change to the codebase, we recommended you contact the primary developers of the code so they can assist you in finding the best way to incorporate your code!
5. Communicate, communicate, communicate.  Use the `Github Issues page <https://github.com/sharppy/SHARPpy/issues>`_ to work through your ideas with the broader community of SHARPpy users.

Some Ideas
^^^^^^^^^^

Some possible (broad) ideas for contributions:

1. Contribute additional data sources so other program users can view other observed and NWP data (*cough*-ECMWF-*cough*)!
2. Add in additional insets into the program to facilitate additional analysis of the data.  
3. Work on documentation of the code base.
4. Develop unit tests to test various aspects of the code. 
5. Search through the `GitHub Issues page <https://github.com/sharppy/SHARPpy/issues>`_ for additional ideas!



