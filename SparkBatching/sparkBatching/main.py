from pyspark.sql import SparkSession
import pyspark
from pyspark.sql import functions as F


def hotels_data():
    topicName = "hotels_topic"
    sparkSession = SparkSession.builder.master("local").appName("GetKafkaTopicData").getOrCreate()

    df = sparkSession.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", topicName) \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load()

    interval = df.select(F.col("value").cast("string")).alias("csv").select("csv.*")

    return interval \
        .selectExpr("split(value,',')[0] as Id" \
                    , "split(value,',')[1] as Name" \
                    , "split(value,',')[2] as Country" \
                    , "split(value,',')[3] as City" \
                    , "split(value,',')[4] as Address" \
                    , "split(value,',')[5] as Latitude" \
                    , "split(value,',')[5] as Longitude" \
                    ).toDF("Id", "Name", "Country", "City", "Address", "Latitude", "Longitude")



def weather_data():
    topicName = "weather_topic"
    sparkSession = SparkSession.builder.master("local").appName("GetKafkaTopicData").getOrCreate()

    df = sparkSession.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", topicName) \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load()

    interval = df.select(F.col("value").cast("string")).alias("csv").select("csv.*")

    return interval \
        .selectExpr("split(value,',')[0] as lng" \
                    , "split(value,',')[1] as lat" \
                    , "split(value,',')[2] as avg_tmpr_f" \
                    , "split(value,',')[3] as avg_tmpr_c" \
                    , "split(value,',')[4] as wthr_date" \
                    ).toDF("lng", "lat", "avg_tmpr_f", "avg_tmpr_c", "wthr_date")


def expedia_data():
    sparkSession = pyspark.sql.SparkSession \
        .builder \
        .appName("root") \
        .getOrCreate()
    return sparkSession.read.format("avro").load("hdfs://localhost:9000/expedia/*")


def calculate_idle_days(expedia_data):
    return expedia_data.select(F.col("srch_ci"), F.col("srch_co"),
                               F.datediff(F.col("srch_co"), F.col("srch_ci")).alias("datediff"))


def remove_booking_data(expedia_data):
    return expedia_data.select(F.col("srch_ci"), F.col("srch_co"),
                               F.datediff(F.col("srch_co"), F.col("srch_ci")).alias("datediff")) \
        .filter((F.col("datediff") >= 2) & (F.col("datediff") <= 30))


def joinData(expedia_data, hotels_data):
    return expedia_data.join(hotels_data.withColumn("id", F.col("Id")), on=['id'], how='inner')


def invalid_hotels(joinData):
    return joinData.select(F.col("Name"), F.col("Country"), F.col("City"), F.col("srch_ci"), F.col("srch_co"),
                           F.datediff(F.col("srch_co"), F.col("srch_ci")).alias("datediff")) \
        .filter(~(F.col("datediff") >= 2) & (F.col("datediff") <= 30))


def group_hotels(joinData):
    return joinData.groupBy(F.col("Country"), F.col("City")).count()


def write_valid_expedia_data_to_hdfs(expedia_data):
    expedia_data.select("id", "date_time", "site_name", "posa_continent", "user_location_country",
                        "user_location_region", "user_location_city", "orig_destination_distance", "user_id",
                        "is_mobile", "is_package", "channel", "srch_ci", "srch_co", "srch_adults_cnt",
                        F.datediff(F.col("srch_co"), F.col("srch_ci")).alias("datediff")) \
        .filter((F.col("datediff") >= 2) & (F.col("datediff") <= 30)) \
        .withColumn("year", F.year(F.col("srch_ci"))) \
        .write \
        .partitionBy("year") \
        .format("csv") \
        .save("hdfs://localhost:9000/valid_expedia/*")


if __name__ == '__main__':
    expedia_data = expedia_data()
    # hotels_data = hotels_data()
    #   weather_data = weather_data()
    # print("expedia_data :", expedia_data.show(), "\n")
    #   print("hotel_data :", hotels_data.count(), "\n")
    #   print("weather_data", weather_data.count(), "\n")
    # print(calculate_idle_days(expedia_data))
    expedia_data.repartition(1).write.option("header", "true").csv("expedia_data")
# print(remove_booking_data(expedia_data).show())
# joinData = joinData(expedia_data, hotels_data)
# print("Joined Data: ", joinData.count())
# invalid_hotels(joinData).show()
# group_hotels(joinData).show()
# write_valid_expedia_data_to_hdfs(expedia_data)
