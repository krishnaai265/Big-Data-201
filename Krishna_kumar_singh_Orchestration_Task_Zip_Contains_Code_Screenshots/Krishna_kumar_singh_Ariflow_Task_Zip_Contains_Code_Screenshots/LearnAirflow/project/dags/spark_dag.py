

try:

    from datetime import timedelta
    from airflow import DAG
    from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
    from datetime import datetime

    print("All Dag modules are ok ......")
except Exception as e:
    print("Error  {} ".format(e))

spark_master = "spark://spark:7077"
spark_avro_jar = "/usr/local/bin/spark/spark-avro_2.12-3.0.1.jar"

with DAG(
        dag_id="spark_dag",
        schedule_interval="@daily",
        default_args={
            "owner": "airflow",
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
            "start_date": datetime(2021, 1, 1),
        },
        catchup=False) as f:

    create_dataframe_and_write_avro = SparkSubmitOperator(
        task_id="create_dataframe_and_write_avro",
        application="./script/spark_script.py",
        conf={"spark.master": spark_master},
        jars=spark_avro_jar,
        driver_class_path=spark_avro_jar
    )

create_dataframe_and_write_avro
