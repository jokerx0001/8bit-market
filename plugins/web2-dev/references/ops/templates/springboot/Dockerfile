FROM eclipse-temurin:{{JAVA_VERSION}}

RUN mkdir /opt/app
COPY target/{{PROJECT_NAME}}-*.jar /opt/app/{{PROJECT_NAME}}.jar

CMD ["java", "-jar", "/opt/app/{{PROJECT_NAME}}.jar", "--spring.profiles.active={{SPRING_PROFILE}}"]
