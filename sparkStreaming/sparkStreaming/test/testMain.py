import unittest

from pyspark.sql import SparkSession

from main import more_than_zero_degree_weather_data, joinData, calculate_idle_day, join_hotels_weather, add_stay_type


class TestMainMethods(unittest.TestCase):

    def setUp(self):
        sparkSession = SparkSession.builder.master("local").appName("GetKafkaTopicData").getOrCreate()

        self.expedia_data = sparkSession.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv("test/resource/expedia.csv")

        self.hotels_data = sparkSession.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv("test/resource/hotels.csv")

        self.weather_data = sparkSession.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv("test/resource/weather.csv")

        self.joinData = joinData(self.expedia_data, self.hotels_data)

    def test_calculate_idle_days(self):
        self.assertEqual(2528242, calculate_idle_day(self.expedia_data).count())

    def test_more_than_zero_degree_weather_data(self):
        self.assertEqual(10, more_than_zero_degree_weather_data(self.weather_data).count())

    def test_join_data(self):
        self.assertEqual(7, self.joinData.count())

    def test_join_hotels_weather(self):
        self.assertEqual(1, join_hotels_weather(self.joinData, self.weather_data).count())

    def test_add_stay_type(self):
        self.assertEqual(2528242, add_stay_type(self.expedia_data).count())


if __name__ == '__main__':
    unittest.main()
