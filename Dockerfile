FROM python:3.11.0a6-alpine3.14

#RUN apt-get update && apt-get -y install pip 

RUN pip install --upgrade pip
RUN pip install requests 

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install psycopg2

RUN pip install python-dotenv

RUN mkdir -p /app
WORKDIR /app

COPY . /app
RUN chmod +x /app/retornaPontosDB.py 

COPY crontab /var/spool/cron/crontabs/root


# start crond with log level 8 in foreground, output to stderr
CMD crond -l 2 -f 