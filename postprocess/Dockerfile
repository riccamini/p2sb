# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copying requirements so we can install dependencies before copying the code and cache the layer in 
# subsequent builds
ENV APP_HOME /app
WORKDIR $APP_HOME/postprocess

COPY postprocess/requirements.txt $APP_HOME/postprocess/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY postprocess $APP_HOME/postprocess
COPY utils $APP_HOME/utils

CMD ["python3", "main.py"]
