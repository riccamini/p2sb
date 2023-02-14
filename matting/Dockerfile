# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# System package dependencies
RUN apt-get update \
&& apt-get install -y libgomp1 wget ffmpeg libsm6 libxext6 \
&& rm -rf /var/lib/apt/lists/*

# Copying requirements so we can install dependencies before copying the code and cache the layer in 
# subsequent builds
ENV APP_HOME /app
WORKDIR $APP_HOME/matting-fastdeploy

COPY matting-fastdeploy/requirements.txt $APP_HOME/matting-fastdeploy/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install fastdeploy-python==1.0.3 -f https://www.paddlepaddle.org.cn/whl/fastdeploy.html

# Copy local code to the container image.
COPY matting-fastdeploy $APP_HOME/matting-fastdeploy
COPY utils $APP_HOME/utils

CMD ["python3", "main.py"]
