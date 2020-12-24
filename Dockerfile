# Setting up base packages.
FROM python:3.7-alpine
MAINTAINER magnetix

# Setting up unbuffered python enviornment.
ENV PYTHONUNBUFFERED 1

# Installing dependencies
# COPY SRC DST
COPY ./requirements.txt /requirements.txt
# RUN COMMAND
RUN pip3 install -r /requirements.txt

# Setting Up directory Structure.
RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user