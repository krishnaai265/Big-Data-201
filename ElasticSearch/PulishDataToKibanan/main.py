# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pyspark.shell import spark
from pyspark.sql.types import StructType, StructField, IntegerType, StringType


def write_valid_expedia_data_to_elasticsearch(read_file):
    read_file.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("checkpointLocation", "path-to-checkpointing/") \
        .start("index-name/doc-type")\
        .awaitTermination()

#
# Press the green button in the gutter to run the script.
def read_file():
    jsonSchema = StructType([
        StructField("id", IntegerType(), True),
        StructField("date_time", StringType(), True),
        StructField("site_time", StringType(), True),
        StructField("posa_continent", StringType(), True),
        StructField("user_location_country", StringType(), True),
        StructField("user_location_region", StringType(), True),
        StructField("user_location_city", StringType(), True),
        StructField("orig_destination_distance", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("is_mobile", StringType(), True),
        StructField("is_package", StringType(), True),
        StructField("channel", StringType(), True),
        StructField("srch_ci", StringType(), True),
        StructField("srch_co", StringType(), True),
        StructField("srch_adults_cnt", StringType(), True),
        StructField("srch_children_cnt", StringType(), True),
        StructField("srch_rm_cnt", StringType(), True),
        StructField("srch_destination_id", StringType(), True),
        StructField("srch_destination_type_id", StringType(), True),
        StructField("hotel_id", StringType(), True)
    ])

    return spark.readStream.schema(jsonSchema).csv("resource/")


if __name__ == '__main__':
    read_file = read_file()
    write_valid_expedia_data_to_elasticsearch(read_file)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
