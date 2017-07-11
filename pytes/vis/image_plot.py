# MatPlotLib for colors and basic plotting
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.image as mpimg
from pylab import rcParams

import pandas as pd
import geopandas as gpd

from itertools import chain
from functools import singledispatch

import numpy as np

__all__ = ['plot_hist', 'plot_kde', 'graph_images']

def plot_hist(arr, bins=32,**kwargs):
    """
    Plots a histogram from an Nd array.

    Parameters
    ----------
    arr : Array
          Array to be plotted.

    bins : int
           Number of bins to used (Optional, default is 32)

    **kwargs : Keyward args to pass to plt.hist()

    Returns
    -------
    """
    rc = rcParams['figure.figsize']
    rcParams['figure.figsize'] = 15, 5

    arr = arr.ravel()
    arr = arr[~np.isnan(arr)]  # filter out NANs

    try:
        plt.hist(arr, bins=bins, range=kwargs['range'], **kwargs)
        plt.xlabel('TI')
        plt.ylabel('Count')
    except Exception as e:
        plt.hist(arr.ravel(), bins=bins, **kwargs)
        plt.xlabel('TI')
        plt.ylabel('Count')

    plt.show()
    rcParams['figure.figsize'] = rc

def plot_kde(arr, **kwargs):
    """
    Kernel density estimation plot from an Nd array.

    Parameters
    ----------
    arr : Array
          Array to be plotted.

    **kwargs : Keyword args to pass to pandas.plot.density

    Returns
    -------
    """
    rc = rcParams['figure.figsize']
    rcParams['figure.figsize'] = 15, 5
    pd.Series(arr.ravel()).plot.density(**kwargs)
    plt.show()
    rcParams['figure.figsize'] = rc

@singledispatch
def graph_images(image, cmap='coolwarm',**kwargs):
    """
    Plots a histogram from an Nd array.

    Parameters
    ----------
    arr : Array
          Array to be plotted.

    **kwargs : dict
               Keyword args to pass to pandas.plot.density
    Returns
    -------
    """
    rc = rcParams['figure.figsize']
    rcParams['figure.figsize'] = 7, 7
    plt.imshow(image, interpolation='none', cmap=cmap, **kwargs)
    plt.colorbar(orientation='horizontal')
    plt.show()
    rcParams['figure.figsize'] = rc
    return

@graph_images.register(list)
def _(images, cmap='coolwarm',limit=40,**kwargs):
    """
    Used for plotting indivdual images or arbirtary length list of images.

    Parameters
    ----------
    images : list of 2D arrays or 2D Array

    cmap : string (Optional, default 'coolwarm')
           A MatPlotLib color map string (https://matplotlib.org/examples/color/colormaps_reference.html)

    limit : int (Optional, default is 40)
            upper bound of images to plot

    **kwargs : dict
               Keyward args to pass into plt.imshow()

    Returns
    -------
    """
    imgs = images[:limit]
    length = len(imgs)
    shape = (int(length/4) + (1 if int(length%4) else 0), 4 if length >= 4 else length)
    rc = rcParams['figure.figsize']
    rcParams['figure.figsize'] = shape[1]*5, shape[0]*5

    f, axx_arr = plt.subplots(shape[0], shape[1], sharex='all', sharey='all')
    try:
        for ax, arr in zip(chain(*axx_arr),imgs):
            im = ax.imshow(arr, interpolation='none', cmap=cmap, **kwargs)
    except:
        for ax, arr in zip(axx_arr,imgs):
            im = ax.imshow(arr, interpolation='none', cmap=cmap, **kwargs)

    f.subplots_adjust(bottom=.15)
    cbar_ax = f.add_axes([.2, 0.015, .6, 0.04])
    f.colorbar(im, cax=cbar_ax, orientation='horizontal')
    plt.show()
    rcParams['figure.figsize'] = rc
