import matplotlib.pyplot as pyplot
import numpy
from csep.utils.constants import SECONDS_PER_DAY

"""
This module contains plotting routines that generate figures for the stochastic event sets produced from
CSEP2 experiments.

Example:
    TODO: Write example for the plotting functions.
    TODO: Ensure this function works with generators using itertools.islice
"""

def plot_cumulative_events_versus_time(stochastic_event_set, observation, percentiles=(5,95), filename=None, show=False):
    """
    Plots cumulative number of events against time for both the observed catalog and a stochastic event set.
    The stochastic event set will be visualized through the 5% and 95% confidence intervals shaded with the
    median value in the center.

    Args:
        stochastic_event_set (iterable): iterable of :class:`~csep.core.catalogs.BaseCatalog` objects
        observation (:class:`~csep.core.catalogs.BaseCatalog`): single catalog, typically observation catalog
        percentiles (tuple): tuple of percentiles to compute bounds on stochastic event set
        filename (str): filename of file to save, if not None will save to that file
        show (bool): whether to making blocking call to display figure
    """
    # set up figure
    fig = pyplot.figure()
    ax = fig.add_subplot(111)

    # need to get the index of the stochastc event sets to plot
    ses_event_counts = []
    for catalog in stochastic_event_set:
        ses_event_counts.append(catalog.get_number_of_events())
    ses_event_counts = numpy.array(ses_event_counts)

    # get indexes of percentiles
    p_low, p_high = percentiles
    ind_low = abs(ses_event_counts-numpy.percentile(ses_event_counts,p_low,interpolation='nearest')).argmin()
    ind_med = abs(ses_event_counts-numpy.percentile(ses_event_counts,50,interpolation='nearest')).argmin()
    ind_high = abs(ses_event_counts-numpy.percentile(ses_event_counts,p_high,interpolation='nearest')).argmin()

    # plot median index
    cat_low = stochastic_event_set[ind_low]
    cat_med = stochastic_event_set[ind_med]
    cat_high = stochastic_event_set[ind_high]

    # plotting timestamps for now, until I can format dates on axis properly
    f = lambda x: numpy.array(x.timestamp()) / SECONDS_PER_DAY

    # probably put this in some type of loop
    days_low = numpy.array(list(map(f, cat_low.get_datetimes())))
    days_low_zero = days_low - days_low[0]

    days_med = numpy.array(list(map(f, cat_med.get_datetimes())))
    days_med_zero = days_med - days_med[0]

    days_high = numpy.array(list(map(f, cat_high.get_datetimes())))
    days_high_zero = days_high - days_high[0]

    days_obs = numpy.array(list(map(f, observation.get_datetimes())))
    days_obs_zero = days_obs - days_obs[0]

    ax.plot(days_low_zero, cat_low.get_cumulative_number_of_events(), '--b', label='{}% Confidence'.format(p_low))
    ax.plot(days_high_zero, cat_high.get_cumulative_number_of_events(), '--b', label='{}% Confidence'.format(p_high))
    ax.plot(days_med_zero, cat_med.get_cumulative_number_of_events(), '-b', label='Median')
    ax.plot(days_obs_zero, observation.get_cumulative_number_of_events(), '-k',label=observation.name)

    # do some labeling
    ax.set_title(cat_med.name, fontsize=16, color='black')
    ax.set_xlabel('Days Elapsed')
    ax.set_ylabel('Cumulative Number of Events')
    ax.legend(loc='best')

    # save figure
    if filename is not None:
        fig.savefig(filename)




    #
