FROM puckel/docker-airflow:1.10.9
USER root
RUN pip install requests
RUN pip install pyspark==3.0.0
RUN mkdir -p /usr/share/man/man1
RUN apt-get update && apt-get install -y default-jdk && apt-get clean
USER airflow