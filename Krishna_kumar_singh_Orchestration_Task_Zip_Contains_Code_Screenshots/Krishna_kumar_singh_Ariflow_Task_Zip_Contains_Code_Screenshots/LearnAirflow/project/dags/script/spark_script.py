from pyspark.sql import SparkSession
print("Start Executing Spark Script.......  ")

columns = ["language", "users_count"]
data = [("Java", "20000"), ("Python", "100000"), ("Scala", "3000")]

spark = SparkSession.builder.appName('SparkByExamples.com').getOrCreate()
rdd = spark.sparkContext.parallelize(data)

dfFromRDD2 = spark.createDataFrame(rdd).toDF(*columns)
dfFromRDD2.show()
dfFromRDD2.write.format("com.databricks.spark.avro").mode("overwrite").save("/usr/local/bin/spark")