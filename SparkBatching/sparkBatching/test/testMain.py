
import unittest

from pyspark.shell import spark

from main import calculate_idle_days, remove_booking_data, joinData, invalid_hotels, group_hotels


class TestMainMethods(unittest.TestCase):

    def setUp(self):
        self.expedia_data = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true")\
            .csv("resource/expedia.csv")

        self.hotels_data = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true")\
            .csv("resource/hotels.csv")

        self.joinData = joinData(self.expedia_data, self.hotels_data)

    def test_calculate_idle_days(self):
        self.assertEqual(2528242, calculate_idle_days(self.expedia_data).count())

    def test_remove_booking_data(self):
        self.assertEqual(1437391, remove_booking_data(self.expedia_data).count())

    def test_join_data(self):
        self.assertEqual(7, self.joinData.count())

    def test_invalid_hotels(self):
        self.assertEqual(3, invalid_hotels(self.joinData).count())

    def test_group_hotels(self):
        self.assertEqual(7, group_hotels(self.joinData).count())

if __name__ == '__main__':
    unittest.main()