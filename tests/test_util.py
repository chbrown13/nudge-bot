import unittest
from src import util

class TestUtils(unittest.TestCase):

    def test_get_time(self):
        self.assertEqual(util.get_time(10), '10 secs')
        self.assertEqual(util.get_time(1000), '17 mins')
        self.assertEqual(util.get_time(10000), '3 hrs')
        self.assertEqual(util.get_time(1000000), '11 days')
        self.assertIsNone(util.get_time(-1))