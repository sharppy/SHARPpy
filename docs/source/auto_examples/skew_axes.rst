.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_skew_axes.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_skew_axes.py:

Make Skew-T Log-P based plots.

Contain tools for making Skew-T Log-P plots, including the base plotting class,
`SkewT`, as well as a class for making a `Hodograph`.



.. code-block:: python


    import matplotlib
    from matplotlib.axes import Axes
    import matplotlib.axis as maxis
    from matplotlib.collections import LineCollection
    import matplotlib.colors as mcolors
    from matplotlib.patches import Circle
    from matplotlib.projections import register_projection
    import matplotlib.spines as mspines
    from matplotlib.ticker import MultipleLocator, NullFormatter, ScalarFormatter
    import matplotlib.transforms as transforms
    import numpy as np


    class SkewXTick(maxis.XTick):
        r"""Make x-axis ticks for Skew-T plots.

        This class adds to the standard :class:`matplotlib.axis.XTick` dynamic checking
        for whether a top or bottom tick is actually within the data limits at that part
        and draw as appropriate. It also performs similar checking for gridlines.
        """

        def update_position(self, loc):
            """Set the location of tick in data coords with scalar *loc*."""
            # This ensures that the new value of the location is set before
            # any other updates take place.
            self._loc = loc
            super(SkewXTick, self).update_position(loc)

        def _has_default_loc(self):
            return self.get_loc() is None

        def _need_lower(self):
            return (self._has_default_loc()
                    or transforms.interval_contains(self.axes.lower_xlim, self.get_loc()))

        def _need_upper(self):
            return (self._has_default_loc()
                    or transforms.interval_contains(self.axes.upper_xlim, self.get_loc()))

        @property
        def gridOn(self):  # noqa: N802
            """Control whether the gridline is drawn for this tick."""
            return (self._gridOn and (self._has_default_loc()
                    or transforms.interval_contains(self.get_view_interval(), self.get_loc())))

        @gridOn.setter
        def gridOn(self, value):  # noqa: N802
            self._gridOn = value

        @property
        def tick1On(self):  # noqa: N802
            """Control whether the lower tick mark is drawn for this tick."""
            return self._tick1On and self._need_lower()

        @tick1On.setter
        def tick1On(self, value):  # noqa: N802
            self._tick1On = value

        @property
        def label1On(self):  # noqa: N802
            """Control whether the lower tick label is drawn for this tick."""
            return self._label1On and self._need_lower()

        @label1On.setter
        def label1On(self, value):  # noqa: N802
            self._label1On = value

        @property
        def tick2On(self):  # noqa: N802
            """Control whether the upper tick mark is drawn for this tick."""
            return self._tick2On and self._need_upper()

        @tick2On.setter
        def tick2On(self, value):  # noqa: N802
            self._tick2On = value

        @property
        def label2On(self):  # noqa: N802
            """Control whether the upper tick label is drawn for this tick."""
            return self._label2On and self._need_upper()

        @label2On.setter
        def label2On(self, value):  # noqa: N802
            self._label2On = value

        def get_view_interval(self):
            """Get the view interval."""
            return self.axes.xaxis.get_view_interval()


    class SkewXAxis(maxis.XAxis):
        r"""Make an x-axis that works properly for Skew-T plots.

        This class exists to force the use of our custom :class:`SkewXTick` as well
        as provide a custom value for interview that combines the extents of the
        upper and lower x-limits from the axes.
        """

        def _get_tick(self, major):
            return SkewXTick(self.axes, None, '', major=major)

        def get_view_interval(self):
            """Get the view interval."""
            return self.axes.upper_xlim[0], self.axes.lower_xlim[1]


    class SkewSpine(mspines.Spine):
        r"""Make an x-axis spine that works properly for Skew-T plots.

        This class exists to use the separate x-limits from the axes to properly
        locate the spine.
        """

        def _adjust_location(self):
            pts = self._path.vertices
            if self.spine_type == 'top':
                pts[:, 0] = self.axes.upper_xlim
            else:
                pts[:, 0] = self.axes.lower_xlim


    class SkewXAxes(Axes):
        r"""Make a set of axes for Skew-T plots.

        This class handles registration of the skew-xaxes as a projection as well as setting up
        the appropriate transformations. It also makes sure we use our instances for spines
        and x-axis: :class:`SkewSpine` and :class:`SkewXAxis`. It provides properties to
        facilitate finding the x-limits for the bottom and top of the plot as well.
        """

        # The projection must specify a name.  This will be used be the
        # user to select the projection, i.e. ``subplot(111,
        # projection='skewx')``.
        name = 'skewx'

        def __init__(self, *args, **kwargs):
            r"""Initialize `SkewXAxes`.

            Parameters
            ----------
            args : Arbitrary positional arguments
                Passed to :class:`matplotlib.axes.Axes`

            position: int, optional
                The rotation of the x-axis against the y-axis, in degrees.

            kwargs : Arbitrary keyword arguments
                Passed to :class:`matplotlib.axes.Axes`

            """
            # This needs to be popped and set before moving on
            self.rot = kwargs.pop('rotation', 30)
            Axes.__init__(self, *args, **kwargs)

        def _init_axis(self):
            # Taken from Axes and modified to use our modified X-axis
            self.xaxis = SkewXAxis(self)
            self.spines['top'].register_axis(self.xaxis)
            self.spines['bottom'].register_axis(self.xaxis)
            self.yaxis = maxis.YAxis(self)
            self.spines['left'].register_axis(self.yaxis)
            self.spines['right'].register_axis(self.yaxis)

        def _gen_axes_spines(self, locations=None, offset=0.0, units='inches'):
            # pylint: disable=unused-argument
            spines = {'top': SkewSpine.linear_spine(self, 'top'),
                      'bottom': mspines.Spine.linear_spine(self, 'bottom'),
                      'left': mspines.Spine.linear_spine(self, 'left'),
                      'right': mspines.Spine.linear_spine(self, 'right')}
            return spines

        def _set_lim_and_transforms(self):
            """Set limits and transforms.

            This is called once when the plot is created to set up all the
            transforms for the data, text and grids.

            """
            # Get the standard transform setup from the Axes base class
            Axes._set_lim_and_transforms(self)

            # Need to put the skew in the middle, after the scale and limits,
            # but before the transAxes. This way, the skew is done in Axes
            # coordinates thus performing the transform around the proper origin
            # We keep the pre-transAxes transform around for other users, like the
            # spines for finding bounds
            self.transDataToAxes = (self.transScale
                                    + (self.transLimits
                                       + transforms.Affine2D().skew_deg(self.rot, 0)))

            # Create the full transform from Data to Pixels
            self.transData = self.transDataToAxes + self.transAxes

            # Blended transforms like this need to have the skewing applied using
            # both axes, in axes coords like before.
            self._xaxis_transform = (
                transforms.blended_transform_factory(self.transScale + self.transLimits,
                                                     transforms.IdentityTransform())
                + transforms.Affine2D().skew_deg(self.rot, 0)) + self.transAxes

        @property
        def lower_xlim(self):
            """Get the data limits for the x-axis along the bottom of the axes."""
            return self.axes.viewLim.intervalx

        @property
        def upper_xlim(self):
            """Get the data limits for the x-axis along the top of the axes."""
            return self.transDataToAxes.inverted().transform([[0., 1.], [1., 1.]])[:, 0]


    # Now register the projection with matplotlib so the user can select
    # it.
    register_projection(SkewXAxes)



**Total running time of the script:** ( 0 minutes  0.000 seconds)


.. _sphx_glr_download_auto_examples_skew_axes.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: skew_axes.py <skew_axes.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: skew_axes.ipynb <skew_axes.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
