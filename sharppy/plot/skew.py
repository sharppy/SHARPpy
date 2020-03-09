# Copyright (c) 2014,2015,2016,2017 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""Make Skew-T Log-P based plots.

Contain tools for making Skew-T Log-P plots, including the base plotting class,
`SkewT`, as well as a class for making a `Hodograph`.
"""

import matplotlib
from matplotlib.axes import Axes
import matplotlib.axis as maxis
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
from matplotlib.patches import Circle
from matplotlib.projections import register_projection
import matplotlib.spines as mspines
from matplotlib.ticker import MultipleLocator, NullFormatter, ScalarFormatter
from matplotlib.pyplot import title
import matplotlib.transforms as transforms
import numpy as np
import sharppy.sharptab as tab

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
pb_plot=1050
pt_plot=100
dp_plot=10
plevs_plot = presvals = np.arange(pb_plot,pt_plot-1,-dp_plot)


def draw_dry_adiabats(ax, tmin=-50, tmax=210, delta=10, color='r', alpha=.2):
    # plot the dry adiabats
    for t in np.arange(tmin,tmax,delta):
        ax.semilogy(thetas(t, presvals), presvals, '-', color=color, alpha=alpha)
    return ax

def draw_mixing_ratio_lines(ax, spacing=[2,4,10,12,14,16,18,20], color='g', lw=.7):
    # plot the mixing ratio lines
    for w in spacing:
        line = tab.thermo.temp_at_mixrat(w, np.arange(1000,600,-1))
        ax.semilogy(line, np.arange(1000,600,-1), '--', color=color, lw=lw)
    return ax

def draw_moist_adiabats(ax, tmin=-50, tmax=50, delta=10, color='k', alpha=0.5):
    # plot the moist adiabats
    for i in np.arange(tmin,tmax,delta):
        t = []
        for pres in np.arange(1000,90,-10):
            t.append(tab.thermo.wetlift(1000,i,pres))
        ax.semilogy(t, np.arange(1000,90,-10), color=color, lw=1, alpha=alpha)
    return ax

def draw_title(ax, t):
    title(t, fontsize=14, loc='left')
    return ax

# Routine to plot the axes for the wind profile
def plot_wind_axes(axes):
    # plot wind barbs
    draw_wind_line(axes)
    axes.set_axis_off()
    axes.axis([-1,1,pb_plot,pt_plot])

     
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

# Routine to calculate the dry adiabats.
def thetas(theta, presvals):
    return ((theta + tab.thermo.ZEROCNK) / (np.power((1000. / presvals),tab.thermo.ROCP))) - tab.thermo.ZEROCNK

def plot_sig_levels(ax, prof):
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

    return ax

def draw_heights(ax, prof):
    trans = transforms.blended_transform_factory(ax.transAxes,ax.transData)

    # Plot the height values on the skew-t, if there's an issue, inform the user.
    for h in [1000,2000,3000,4000,5000,6000,9000,12000,15000]:
        p = tab.interp.pres(prof, tab.interp.to_msl(prof, h))
        try:
            ax.text(0.01, p, str(h/1000) +' km -', verticalalignment='center', fontsize=9, transform=trans, color='r')
        except:
            print("problem plotting height label:", h)

    ax.text(0.01, prof.pres[prof.sfc], 'Sfc', verticalalignment='center', fontsize=9, transform=trans, color='r')
    return ax

def draw_effective_inflow_layer(ax, prof):
    # Plot the effective inflow layer on the Skew-T, like with the GUI (TODO: include the effective SRH on the top like in the GUI).
    trans = transforms.blended_transform_factory(ax.transAxes,ax.transData)
    ax.plot([0.2,0.3], [prof.ebottom, prof.ebottom], color='c', lw=2, transform=trans)
    ax.plot([0.25,0.25], [prof.etop, prof.ebottom], color='c', lw=2, transform=trans)
    ax.plot([0.2,0.3], [prof.etop, prof.etop], color='c', lw=2, transform=trans)

def draw_hodo_inset(ax, prof):
    # Draw the hodograph axes on the plot.
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    inset_axes = inset_axes(ax,width=1.7, # width = 30% of parent_bbox
                                        height=1.7, # height : 1 inch
                                        loc=1)
    inset_axes.get_xaxis().set_visible(False)
    inset_axes.get_yaxis().set_visible(False)

    # Draw the range rings around the hodograph.
    for i in range(10,90,10):
        circle = Circle((0,0),i,color='k',alpha=.3, fill=False)
        if i % 10 == 0 and i <= 50:
            inset_axes.text(-i,2,str(i), fontsize=8, horizontalalignment='center')
        inset_axes.add_artist(circle)
    inset_axes.set_xlim(-60,60)
    inset_axes.set_ylim(-60,60)
    inset_axes.axhline(y=0, color='k')
    inset_axes.axvline(x=0, color='k')
    #srwind = tab.params.bunkers_storm_motion(prof)

    return inset_axes

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


