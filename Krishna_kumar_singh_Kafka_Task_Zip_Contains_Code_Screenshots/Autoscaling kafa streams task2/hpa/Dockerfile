FROM openjdk:8

ARG JMX_PORT="5555"

ENV JMX_JAVA_OPTS="-Dcom.sun.management.jmxremote.port=$JMX_PORT -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"

COPY kafka-streams-1.0-SNAPSHOT-jar-with-dependencies.jar /usr/src/myapp/kafka-streams-app.jar

CMD [ "sh", "-c", "java $JMX_JAVA_OPTS -jar /usr/src/myapp/kafka-streams-app.jar" ]