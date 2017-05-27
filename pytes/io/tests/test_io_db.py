import unittest
from .. import io_db

class TestUtils(unittest.TestCase):
    # TODO: Make better tests

    def test_init(self):
        try:
            io_db.spark_from_mongodb()
        except Exception as e:
            self.fail("PySpark failed to initialize: {}".format(e))
