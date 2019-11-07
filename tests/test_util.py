import unittest
from src import util

class TestUtils(unittest.TestCase):

    def test_get_time(self):
        self.assertEqual(util._get_time(10), '10 secs')
        self.assertEqual(util._get_time(1000), '16 mins')
        self.assertEqual(util._get_time(10000), '2 hrs')
        self.assertEqual(util._get_time(1000000), '11 days')
        self.assertIsNone(util._get_time(-1))