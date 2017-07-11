import geopandas as gpd
import pandas as pd

from functools import singledispatch
import numpy as np

__all__ = ["group_by", "get_images", "spatial_query"]

def group_by(df, **options):    # pragma: nocover
    """
    @TODO only works with spatiotemporal data, make more generic?
    Groupby Function for dataframes, returns a list of dataframes representing
    similarity classes

    Pass in a key values pairs of fields and there desired bin behaviors
    EX:

        Bin by every one year and every 90 lsubs
        >>> group_by(df, year:1, lsubs:90)
        Returns a list of dataframes with values grouped every 90 lsubs for every year

        Bin all years (TES years are only 24-27)every 180 lsubs
        >>> group_by(df, year=4, lsubs=180)

        Alternitively...
        >>> params = {'year':4, 'lsubs':180}
        >>> group_by(df, **params)

    Parameters
    ----------
    df : DataFrame
         DataFrame to be grouped

    **options : key value pairs of bin options
    """
    def get_group(g, key):
        """
        Helper function, get group from Pandas group object, makes
        sure to return None if it doesn't exist
        """
        try:
            return g.get_group(key)
        except:
            return None

    def binval(val, floor=0, ceil=361, step=10):
        """
        Generic Bin function, uses Numpies arange + digitize to get similarity classes
        """
        # Make sure the bins is only instantiated once during runtime
        global bins
        if not 'bins' in locals(): bins = np.arange(floor,ceil,step)
        if val <= floor:
            return bins[0]
        try:
            return bins[np.digitize(val, bins)-1]
        except:
            return bins[-1]

    # Smarter way to do this?
    # set the parameters to binval depedning on value being binned
    binfuncs = {
        'year' : lambda x, step=10: binval(x, floor=24, ceil=28, step=step),
        'lsubs' : lambda x, step=10: binval(x, floor=0, ceil=361, step=step),
        'local_time' : lambda x, step=10: binval(x, floor=0, ceil=24, step=step)
    }

    cdf = df.copy(deep=True)
    for key in options.keys():
        cdf[key] = df[key].apply(binfuncs[key], step=options[key])

    cdf = cdf.groupby(sorted(list(options.keys()), reverse=True))
    keys = sorted(cdf.groups.keys())
    return [df for df in [get_group(cdf, key) for key in keys] if df is not None]


def get_images(dataframes, query=None, col='col', row='row', data='ti'): # pragma: nocover
    """
    Convert a list of dataframes to a list of images. Images are 2D
    arrays with values being the average of all values in that row and columns.
    That is, with a dataframe where row and column are not unique, all values
    at the same location are averaged out to get the final pixel value.
    """
    dfs = dataframes
    if query:
        dfs = [df for df in [df.query(query) for df in dfs] if not df.empty]

    dfs = [df.groupby([col, row], as_index=False).agg({data:np.mean}) for df in dfs]

    if isinstance(dfs, list):
        arrays = [np.zeros((df[col].max()-df[col].min(),df[row].max()-df[row].min())) for df in dfs]
        for arr in arrays: arr[:] = np.NAN

    for arr, df in zip(arrays, dfs):
        if len(arr) and not df.empty:
            indices = np.vstack(np.array([df[row]-df[row].min(), df[col]-df[col].min()]).transpose())
            arr[indices[:,1]-1, indices[:,0]-1] = df[data]
            arr = arr

    return [arr.transpose()[::,::-1] for arr in arrays]

@singledispatch
def spatial_query(df, geom): # pragma: nocover
    """
    Allows for a query on a dataframe. Returns a new Dataframe with the
    new data.

    Parameters
    ----------
    df : DataFrame
         A GeoPandas GeoDataFrame to query on

    geom : Shapely Geometry
           The Geometry to query on, everyhing located in the bounds
           of the Geometry is returned.
    """
    rdf = df[df.within(geom)]
    return rdf

@spatial_query.register(list)
def _(dfs, geom): # pragma: no cover
    try:
        return [df[df.within(geom)] for df in dfs]
    except Excaption as e:
        print(e)
        print('Input must be a list of Pandas or GeoPandas DataFrames')
