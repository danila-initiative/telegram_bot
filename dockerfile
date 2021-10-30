FROM python:3.9.6-slim-buster

RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
    cron \
    vim \
    make

RUN mkdir app

WORKDIR /app

COPY ./runtests.sh ./runtests.sh

COPY ./requirements.txt	./requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
