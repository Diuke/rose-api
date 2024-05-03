FROM python:3.10.14-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y binutils libproj-dev gdal-bin

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

COPY /roseapi .
COPY ./requirements.txt .
COPY ./server_start.sh .
RUN mkdir -p /results

RUN python -m pip install --upgrade pip && \
    pip3 install -r requirements.txt 

RUN chmod +x server_start.sh
ENTRYPOINT "/server_start.sh"