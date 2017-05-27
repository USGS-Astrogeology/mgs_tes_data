from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext

# TODO: Added more drivers & data sources, mostly hardcoaded to mongodb for now
# Cassandra is not tested
db_driver = {
    'mongodb' : 'org.mongodb.spark:mongo-spark-connector_2.11:2.0.0',
    'cassandra' : 'com.datastax.spark:spark-cassandra-connector_2.11:2.0.1-s_2.11'
}

db_datasource = {
    'mongodb' : 'com.mongodb.spark.sql.DefaultSource',
    'cassandra' : 'org.apache.spark.sql.cassandra'
}

def create_spark_session(flavor, config=SparkConf()):
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

def spark_from_mongodb(host='localhost', port=27017, db='test', collection='collection'):
    """
    Create a SparkClient instance for a mongodb database.
    """

    # TODO: Better way of conveniently creating DB specific PySpark sessions? Code smell is icky
    mongo_config = SparkConf()
    mongo_config.set('spark.mongodb.input.uri', 'mongodb://{}:{}/{}.{}'.format(host, port,db, collection))
    mongo_config.set('spark.mongodb.output.uri', 'mongodb://{}:{}/{}.{}'.format(host, port, db, collection))

    return create_spark_session(flavor='mongodb', config=mongo_config)


def get_dataframe(context, columns='*', where='', **options):
    """
    Simple function to get a dataframe from a Spark session
    """
    df = self.reader.options(**options).load().select(columns)
    return df if not query else df.where(where)
