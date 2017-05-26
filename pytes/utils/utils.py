from angles import normalize

def mgs84_norm_lat(angle):
    """
    Noralize latitude to the MGS84 datum. For storing data where only MGS84 is supported
    (e.g. MongoDB)

    Parameters
    ----------
    angle : double
            The angle to normalize

    Returns
    -------
    : double
      The new Angle normalized between [-90, 90]
    """
    return normalize(angle, lower=-90, upper=90)

def mgs84_norm_long(angle):  
    """
    Noralize longitude to the MGS84 datum. For storing data where only MGS84 is supported
    (e.g. MongoDB)

    Parameters
    ----------
    angle : double
            The angle to normalize

    Returns
    -------
    : double
      The new Angle normalized between [-180, 180]
    """
    return normalize(angle, lower=-180, upper=180)
