from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext

class SparkClient(object):
    """
    Simple class providing some syntactic sugar for the PySpark interface

    """
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

    def __init__(self, flavor, config=SparkConf(), **kwargs):
        """

        """
        flavor = flavor.lower()

        # Create configuration and start connection
        config.set('spark.jars.packages', SparkClient.db_driver[flavor])
        sc = SparkContext(conf=config)
        self.sqlcontext = SQLContext(sc)
        self.reader = self.sqlcontext.read.format(SparkClient.db_datasource[flavor])


    def from_mongodb(host='localhost', port=27017, db='test', collection='collection'):
        mongo_config = SparkConf()
        mongo_config.set('spark.mongodb.input.uri', 'mongodb://{}:{}/{}.{}'.format(host, port,db, collection))
        mongo_config.set('spark.mongodb.output.uri', 'mongodb://{}:{}/{}.{}'.format(host, port, db, collection))

        return SparkClient(config=mongo_config, flavor='mongodb')

    def get_dataframe(self, columns=[], filter='', **options):
        df = self.reader.options(**options).load()
        return df if not query else df.filter(query)
