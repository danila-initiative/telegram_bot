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
RUN pip install -r requirements.txt	

# RUN pytest tests/