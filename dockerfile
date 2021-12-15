FROM python:3.9.6-slim-buster


# Утилитки
RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
    cron \
    vim \
    make


# Рабочая папка
RUN mkdir app
WORKDIR /app


# Cron
COPY cron_file_testing /etc/cron.d/cron_file
RUN chmod 0644 /etc/cron.d/cron_file
RUN crontab /etc/cron.d/cron_file


# Запускалка тестов
COPY ./runtests.sh ./runtests.sh
COPY ./entrypoint.sh ./entrypoint.sh

COPY ./Makefile ./Makefile

# Окружение
COPY ./requirements.txt	./requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
