# Pyspark for computation
import pyspark
from pyspark import SparkContext, SQLContext, SparkConf
from pyspark.sql.functions import udf, col
from pyspark.sql.types import FloatType

# Sqlalchemy for database interation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy import text
from geoalchemy2 import Geometry
from geoalchemy2 import select
from geoalchemy2.functions import ST_Contains

# MatPlotLib for colors and basic plotting
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.image as mpimg
from pylab import rcParams

# Pandas for in memory processing
import geopandas as gpd
import pandas as pd

from itertools import chain
from functools import singledispatch

from shapely.geometry.base import BaseGeometry
from shapely.geometry import box
from shapely.geometry import Point
from shapely import wkb

# Numpy for number crunching
import numpy as np

import os
import collections
import re

__all__ = ["query_postgres", "connect_postgres"]

# TODO: Added more drivers & data sources
# Cassandra is not tested
db_driver = {
    'mongodb' : 'org.mongodb.spark:mongo-spark-connector_2.11:2.0.0',
    'cassandra' : 'com.datastax.spark:spark-cassandra-connector_2.11:2.0.1-s_2.11'
}

db_datasource = {
    'mongodb' : 'com.mongodb.spark.sql.DefaultSource',
    'cassandra' : 'org.apache.spark.sql.cassandra'
}

def create_spark_session(flavor, config=SparkConf()): # pragma: no cover
    """
    Initialize a PySpark instance given some configuration and database type

    Parameters
    ----------
    flavor : str
             The name of the database you want to connect to (e.g. "mongodb" or "cassandra")

    config : SparkConf
             A Spark configuration object with parameters used to intantiate the PySpark
             instance
    """
    flavor = flavor.lower()

    # Create configuration and start connection
    config.set('spark.jars.packages', db_driver[flavor])
    sc = SparkContext(conf=config)
    sqlcontext = SQLContext(sc)
    reader = sqlcontext.read.format(db_datasource[flavor])
    return sqlcontext, reader

def spark_from_mongodb(host='localhost', port=27017, db='test', collection='collection'): # pragma: nocover
    """
    Create a SparkClient instance for a mongodb database.
    """

    # TODO: Better way of conveniently creating DB specific PySpark sessions? Code smell is icky
    mongo_config = SparkConf()
    mongo_config.set('spark.mongodb.input.uri', 'mongodb://{}:{}/{}.{}'.format(host, port,db, collection))
    mongo_config.set('spark.mongodb.output.uri', 'mongodb://{}:{}/{}.{}'.format(host, port, db, collection))

    return create_spark_session(flavor='mongodb', config=mongo_config)


def connect_postgres(host='localhost', port=5432, user='postgres', password='pass', schema=None, db='tes'): # pragma: nocover
    """
    Returns a SQLAlchemy Engine and Metadata.

    Parameters
    ----------
    host : string (Optional, default is 'localhost')
           Hostname/IP address string

    port : int, string (Optional, default is 5432)
           int or string with port number.

    user : string (optional, default is 'postgres')
           String with Username

    password : string (optional, default is 'pass')
               string representing the user password

    schema : string (optional, default is None)
             string with desired Schema

    db : string (optional, default is 'tes')
         desired database to connect to

    Returns
    -------
    : SQLAlchemy Engine
    : SqlAlchemy MetaData
    """
    engine = create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(user,password,host,int(port),db))
    metadata = MetaData(engine)
    if schema:
        metadata.reflect(bind=engine, schema=schema)
    else:
        metadata.reflect(bind=engine)
    return engine, metadata


def query_postgres(conn, columns=[], shape=(), year=[],ls=[],local_time=[], verbose=False):  # pragma: nocover
    """
    @TODO Hardcoded for spatiotemporal searches, update for more generic searches?

    Given a SQLAlchemy connection, retrieve a table from the TES database as a
    pandas dataframe.

        Example of using shape and range
        >>> get_dataframe(engine, shape=(-10, -15, 40, 45), ls=range(10,170))

        Example of using a discrete list
        >>> get_dataframe(engine, year=[24,26], local_time=range())

    Paramters
    ---------
    conn : SQLAlchemy connectable i,e engine or connection
           Using SQLAlchemy makes it possible to use any DB supported by that library

    columns : List (Optional, Default is empty)
              List of columns. If empty, all columns are returned.

    shape : Tuple or Shapely Object (Optional, Default is an empty Tuple)
            Shape used for Spatial Queries. Tuple in the form of (minX, minY, maxX, maxY) If left empty, then global data is returned.
            TES data has a longitude range of [0,360] and latitude range of [-90,90]

    year : List or Range of years (Optional, Default is an empty List)
           Specifies the range of years for temporal queries. All years are returned if
           left empty. TES year range is [24,27].

    ls : List or Range of Solar Longitude angles (Optional, Default is an empty List)
           Specifies the range of Solar Longitude angles for temporal queries. All Ls values are returned if
           left empty. Ls range is [0,360]

    local_time : List or Range of decimal hours (Optional, Default is an empty :ist)
                 Specifies the range of local time for temporal queries in decimal hours. All Ls values are returned if
                 left empty. Local time range is [0,24]

    verbose : bool (Optional, Default is False)
              If true, prints out more information to stdout of what the function is going in the background

    Returns
    -------
     : Dataframe
       Either a Pandas DataFrame or a GeoDataFrame.
    """

    @singledispatch
    def queryval(val,selobj,field):
        """
        Returns string representation of a particular query
        """
        if not val:
            return selobj
        return selobj.where(text('{} = {}'.format(field,val)))

    @queryval.register(collections.Iterable)
    def _(val,selobj,field):
        if not val:
            return selobj
        query = selobj.where(text(' and '.join(['{} = {}'.format(field,y) for y in year[:-1]])))
        return query.where(text('{} = {}'.format(field,year[-1])))

    @queryval.register(range)
    def _(val,selobj,field):
        if not val:
            return selobj
        return selobj.where(text('{} > {} and {} < {}'.format(field,val.start,field,val.stop)))

    @queryval.register(BaseGeometry)
    def _(val,selobj,field):
        if not val:
            return selobj
        return selobj.where(text('st_contains(st_setsrid(st_makeenvelope({},{},{},{}), 49900), st_setsrid(geom,49900))'.format(*val.bounds)) )

    if shape and isinstance(shape, tuple):
        shape = box(*shape)

    metadata = MetaData(conn)
    metadata.reflect(bind=conn, schema='ti_bins')

    if isinstance(shape, BaseGeometry):  # We Have a Shapely Geometry, get appropriate table
        regex = re.compile(r'/*time')
        tables = [metadata.tables['ti_bins.fullres']]
        tables.extend(filter(lambda x: regex.search(x.key), metadata.sorted_tables))
        tables.append(metadata.tables['ti_bins.global'])
        table = tables[np.digitize(shape.area, np.linspace(0, 64800, len(tables), endpoint=True))-1]
    else:  # Else, get global plot
        table = metadata.tables['ti_bins.global']

    # Apply all the queries
    table = metadata.tables['ti_bins.bin25time']
    query = select([table.columns[key] for key in columns] if columns else [table])
    query = queryval(shape, query, 'geom')
    query = queryval(year,query,'year')
    query = queryval(ls, query, 'lsubs')
    query = queryval(local_time, query, 'local_time')

    if verbose:
        print(str(query))

    # GeoDataframe.from_postgis doesn't behave well, so manual conversion
    # is done instead
    df = pd.DataFrame()
    for chunk in pd.read_sql(str(query), conn, chunksize=100000):
        df = df.append(chunk, ignore_index=True)

    df['geom'] = df['geom'].apply(lambda x:wkb.loads(x.hex(), hex=True))
    return gpd.GeoDataFrame(df, geometry='geom')
