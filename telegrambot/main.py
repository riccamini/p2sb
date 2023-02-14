import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
print(sys.path)

import logging
import time
import flask
import telebot
import uuid
import json

from google.cloud import pubsub_v1
from utils import fileutils, payloads, cloudstorage

from dotenv import load_dotenv
load_dotenv()

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Logger init
logging.basicConfig(
    level=os.getenv('LOG_LEVEL'),
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger("telethon-client-logger")
logger.info("Started!")
logger.debug("Environment configuration: "+str(os.environ))

# Pub/Sub publisher client configuration
gcp_project_name= os.getenv('GCP_PROJECT_NAME')
topic_name = os.getenv('TOPIC_NAME')
pubsub_client = pubsub_v1.PublisherClient()
topic_path = f"projects/{gcp_project_name}/topics/{topic_name}"

# Set up telegram bot
bot = telebot.TeleBot(os.getenv('APP_TOKEN'))

# Setup scratch-dir, model dirs
workdir = os.getenv('TMP_PATH')
fileutils.setup_dir(os.getenv('TMP_PATH'))

# Cloud storage client
cs_client = cloudstorage.CloudStorageClient()
cs_bucket = os.getenv('BUCKET_NAME')

app = flask.Flask(__name__)


# Process webhook calls
@app.route('/', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        logger.debug(f"Request received: {json_string}")

        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ('', 204)
    else:
        return ('Bad request', 400)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am stickersbot!\n\n"
                  "Please send me a picture of a person and I'll try my best to create a sticker!"))

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, "Please send me a picture!")

@bot.message_handler(func= lambda message: True, content_types=['photo'])
def get_input_photo(message: telebot.types.Message):
    logger.debug("Input photo sent by user")
    
    file_id = message.photo[-1].file_id
    file_path = bot.get_file(file_id).file_path
    logger.debug(f"File id: {file_id}\nFile path: {file_path}")

    downloaded_file = bot.download_file(file_path)
    media_uuid = str(uuid.uuid1())
    output_file_path = f"{workdir}/{media_uuid}.jpg"
    logger.debug(f"Output file path: {output_file_path}")

    with open(output_file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    chat_id = message.chat.id
    user = message.chat.username if not None else 'N.A.'
    
    cs_client.put_object(cs_bucket, media_uuid, output_file_path)
    
    pubsub_message = payloads.P2SMessage(chat_id, media_uuid, user, str(time.time()), "P2SImageReceived")
    future = pubsub_client.publish(topic_path, pubsub_message.get_bytes())
    message_id = future.result()

    logger.debug(f"Message sent to pub/sub with id: {message_id}")
    bot.reply_to(message, "Thank you for the photo! Please be patient while I create your sticker...")


if __name__ == '__main__':
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
