import unittest

from .. import utils

class TestUtils(unittest.TestCase):

    def test_angle_normalization(self):
        assert utils.mgs84_norm_lat(91) == -89
        assert utils.mgs84_norm_lat(45) == 45
        assert utils.mgs84_norm_lat(-91) == 89

        assert utils.mgs84_norm_long(181) == -179
        assert utils.mgs84_norm_long(180) == -180
        assert utils.mgs84_norm_long(-180) == -180
        assert utils.mgs84_norm_long(-91) == -91
