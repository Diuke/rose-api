# Dockerfile
FROM python:3.10.14-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update
RUN apt-get install -y binutils libproj-dev gdal-bin

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project
COPY ./roseapi /code/