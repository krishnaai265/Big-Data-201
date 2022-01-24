FROM ubuntu:16.04

ENV container docker
ENV ambari_repo http://public-repo-1.hortonworks.com/ambari/ubuntu16/2.x/updates/2.7.3.0/ambari.list

RUN apt-get update -y
RUN apt-get install -y wget ntp
RUN wget -O /etc/apt/sources.list.d/ambari.list $ambari_repo
RUN apt-get install -y gnupg
RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B9733A7A07513CAD
RUN apt-get update -y
RUN apt-get install -y ambari-server ambari-agent

RUN apt-get install -y ssh
RUN ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa
RUN cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
RUN chmod 0600 ~/.ssh/authorized_keys

RUN mkdir -p /usr/share/java/ && \
 wget https://jdbc.postgresql.org/download/postgresql-42.2.9.jar -O /usr/share/java/postgresql-42.2.9.jar && \
 chmod 644 /usr/share/java/postgresql-42.2.9.jar && \
 ambari-server setup --jdbc-db=postgres --jdbc-driver=/usr/share/java/postgresql-42.2.9.jar && \
 echo "n\n1\ny\nn\n" | ambari-server setup && \
 sed -i "s/ambari,mapred/all/g" /etc/postgresql/9.5/main/pg_hba.conf && \
 service postgresql start && \
 ambari-server start &&  \
 su - postgres -c "psql -c \"create database hive\"" && \
 su - postgres -c "psql -c \"create user hive with password 'admin';"\" && \
 su - postgres -c "psql -c \"grant all privileges on database hive to hive;"\" && \
 su - postgres -c "psql -c \"create database oozie\"" && \
 su - postgres -c "psql -c \"create user oozie with password 'admin';"\" && \
 su - postgres -c "psql -c \"grant all privileges on database oozie to oozie;"\" && \
 sed -i "s/localhost/ambari.hadoop/" /etc/ambari-agent/conf/ambari-agent.ini && \
 ambari-server stop && \
 service postgresql stop

EXPOSE 5432 8440 8441 8440 8080

CMD service ssh start && service postgresql start && service ntp start && ambari-agent start && (ambari-server start || ambari-server start) && tail -f /dev/null