import csv
import unittest

from main import read_csv, check_geocoordinate, generate_geohash


class TestMainMethods(unittest.TestCase):

    def test_read_csv(self):
        self.assertRaises(FileNotFoundError, read_csv, 'dummy_file')

    def test_check_geocoordinate(self):
        hotelsfile = 'resource/hotels.csv'
        with open(hotelsfile, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            i = 0
            for row in reader:
                self.assertRaises(IndexError, check_geocoordinate, row)

    def test_generate_geohash(self):
        geohash = generate_geohash(100.00, 100.00)
        self.assertEqual('ypzp', geohash)


if __name__ == '__main__':
    unittest.main()