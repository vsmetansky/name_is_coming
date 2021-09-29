FROM python:3.9-slim-buster

WORKDIR /app
COPY requirements.txt /app

RUN \
  pip install -U pip --no-cache-dir && \
  pip install -r requirements.txt --no-cache-dir

COPY . /app

RUN pip install -e . --no-cache-dir

CMD poller --clear-cache --run-forever
