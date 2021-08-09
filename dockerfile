FROM python:3.9.6-slim-buster

RUN apt-get update && apt-get -y install cron && apt-get -y install vim
RUN mkdir code
RUN mkdir code/logs
RUN mkdir code/results

COPY requirements.txt /code
COPY src /code/src
COPY .env /code/src

# Cron
COPY cron_file /etc/cron.d/cron_file
RUN chmod 0644 /etc/cron.d/cron_file
RUN crontab /etc/cron.d/cron_file
RUN touch /var/log/cron.log

WORKDIR /code

RUN pip install -r requirements.txt	