# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME/telegrambot

COPY telegrambot/requirements.txt $APP_HOME/telegrambot/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY telegrambot $APP_HOME/telegrambot
COPY utils $APP_HOME/utils

CMD ["python3", "main.py"]
