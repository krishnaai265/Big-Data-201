from pyspark.sql import SparkSession
from pyspark.sql import functions as F

sparkSession = SparkSession.builder.master("local").appName("GetKafkaTopicData").getOrCreate()

def hotels_data():
    topicName = "hotels_data_topic"

    df = sparkSession.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9098") \
        .option("subscribe", topicName) \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load()

    interval = df.select(F.col("value").cast("string")).alias("csv").select("csv.*")

    return interval \
        .selectExpr("split(value,',')[0] as Id"
                    , "split(value,',')[1] as Name" \
                    , "split(value,',')[2] as Country" \
                    , "split(value,',')[3] as City" \
                    , "split(value,',')[4] as Address" \
                    , "split(value,',')[5] as Latitude" \
                    , "split(value,',')[5] as Longitude" \
                    ).toDF("Id", "Name", "Country", "City", "Address", "Latitude", "Longitude")


def weather_data():
    topicName = "weather_data_topic"

    df = sparkSession.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9098") \
        .option("subscribe", topicName) \
        .option("delimiter", "\t") \
        .load() \
        .limit(10000)

    return df \
        .selectExpr("split(value,'\t')[0] as lng" \
                    , "split(value,'\t')[1] as lat" \
                    , "split(value,'\t')[2] as avg_tmpr_f" \
                    , "split(value,'\t')[3] as avg_tmpr_c" \
                    , "split(value,'\t')[4] as wthr_date" \
                    ).toDF("lng", "lat", "avg_tmpr_f", "avg_tmpr_c", "wthr_date")


def expedia_data(date):
    return sparkSession \
        .read \
        .format("avro") \
        .load("hdfs://localhost:9000/expedia/*") \
        .filter(F.year(F.col("srch_ci")) == date)


def joinData(expedia_data, hotels_data):
    return expedia_data.join(hotels_data.withColumn("id", F.col("Id")), on=['id'], how='inner')


def write_valid_expedia_data_to_hdfs(expedia_data):
    expedia_data\
        .write \
        .partitionBy("year") \
        .format("csv") \
        .save("hdfs://localhost:9000/valid_expedia/*")


def join_hotels_weather(joinData, weather_data):
    return joinData \
        .withColumn("Longitude", F.round(F.col("Longitude"), 1)) \
        .withColumn("Latitude", F.round(F.col("Latitude"), 1)) \
        .join(weather_data
              .withColumn("Longitude", F.round(F.col("lng"), 1))
              .withColumn("Latitude", F.round(F.col("lat"), 1)), on=['Latitude', 'Longitude'], how='inner')


def calculate_idle_day(expedia_data):
    return expedia_data.select(F.col("srch_ci"), F.col("srch_co"),
                               F.datediff(F.col("srch_co"), F.col("srch_ci")).alias("datediff"))


def more_than_zero_degree_weather_data(join_data):
    return join_data.filter(F.col("avg_tmpr_c") > 0)


def add_stay_type(joinData):
    return joinData.select("site_name", "srch_ci", "srch_co",
                           F.datediff(F.col("srch_co"), F.col("srch_ci")).alias("datediff")) \
        .withColumn("stay_type", F.when((F.col("datediff") >= 2) & (F.col("datediff") <= 7), "standard_stay_cnt")
                    .otherwise(
        F.when((F.col("datediff").isNull()) | (F.col("datediff") <= 0) | (F.col("datediff") > 30), "erronemous_stay_cnt")
            .otherwise(F.when(F.col("datediff") == 1, "short_stay_cnt")
                       .otherwise(F.when((F.col("datediff") >= 7) & (F.col("datediff") <= 14), "standard_extended_stay_cnt")
                                  .otherwise(F.when((F.col("datediff") >= 14) & (F.col("datediff") <= 28), "long_stay_cnt"))
                                  )))).drop("srch_ci", "srch_co", "datediff")


def most_popular_stay_type(erronemous_stay, short_stay, standard_stay, standard_extended_stay, long_stay):

    return F.when((erronemous_stay >= short_stay) & (erronemous_stay >= standard_stay) & (erronemous_stay >= standard_extended_stay) & (erronemous_stay >= long_stay), "erronemous_stay")\
        .otherwise(F.when((short_stay >= erronemous_stay) & (short_stay >= standard_stay) & (short_stay >= standard_extended_stay) & (short_stay >= long_stay), "short_stay")\
        .otherwise(F.when((standard_extended_stay >= short_stay) & (standard_extended_stay >= erronemous_stay) & (standard_extended_stay >= standard_stay) & (standard_extended_stay >= long_stay), "standard_extended_stay")\
        .otherwise(F.when((standard_stay >= erronemous_stay) & (standard_stay >= short_stay) & (standard_stay >= standard_extended_stay) & (standard_stay >= long_stay), "standard_stay")\
        .otherwise(F.when((long_stay >= standard_stay) & (long_stay >= erronemous_stay) & (long_stay >= short_stay) & (long_stay >= standard_extended_stay), "long_stay")))))


def pivot_dataframe(stay_duration):
    return stay_duration \
        .groupBy(F.col("site_name")) \
        .pivot("stay_type") \
        .agg(F.count(F.lit(1)))

def write_valid_expedia_data_to_hdfs(pivot_dataframe):
    pivot_dataframe.write\
        .format("csv") \
        .save("hdfs://localhost:9000/spark_streaming/*")


def print_enrich_data(expedia_datas, hotels_datas, weather_datas):
    #joinDatas = joinData(expedia_datas, hotels_datas)
    #join_hotels_weather_expedia = join_hotels_weather(joinDatas, weather_datas)
    #join_hotels_weather_expedia.show()
    #more_than_zero_degree_weather_data = more_than_zero_degree_weather_data(weather_datas)
    #more_than_zero_degree_weather_data.show()
    calculate_idle_days = calculate_idle_day(expedia_datas)
    calculate_idle_days.show()

    add_stay_types = add_stay_type(expedia_datas)

    pivot_dataframes = pivot_dataframe(add_stay_types)

    pivot_dataframes.drop("null").na.fill(0).withColumn("most_popular_stay_type",
                                                        most_popular_stay_type(F.col("erronemous_stay_cnt"),
                                                                               F.col("short_stay_cnt"),
                                                                               F.col("standard_stay_cnt"),
                                                                               F.col("standard_extended_stay_cnt"),
                                                                               F.col("long_stay_cnt"))).show()
    write_valid_expedia_data_to_hdfs(pivot_dataframes)


if __name__ == '__main__':
    expedia_data_2016 = expedia_data("2016")
    expedia_data_2017 = expedia_data("2017")
    #hotels_datas = hotels_data()
    #weather_datas = weather_data()
    #print_enrich_data(expedia_data_2016, hotels_datas, weather_datas)
    print_enrich_data(expedia_data_2017, "hotels_datas", "weather_datas")