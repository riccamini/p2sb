import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
print(sys.path)

import logging
import time
import flask
import json
import base64
import telebot

from PIL import Image
from PIL.ImageOps import contain
from utils import fileutils, payloads, cloudstorage

from dotenv import load_dotenv
load_dotenv()

# Logger init
logging.basicConfig(
    level=os.getenv('LOG_LEVEL'),
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger("telethon-client-logger")
logger.info("Started!")
logger.debug("Environment configuration: "+str(os.environ))

# Set up telegram bot
telebot.logger.setLevel(logging.DEBUG)
bot = telebot.TeleBot(os.getenv('APP_TOKEN'))

# Setup scratch-dir, model dirs
workdir = os.getenv('TMP_PATH')
fileutils.setup_dir(os.getenv('TMP_PATH'))

# Cloud storage client
cs_client = cloudstorage.CloudStorageClient()
cs_bucket = os.getenv('BUCKET_NAME')

app = flask.Flask(__name__)

def process_image(image_path):
    image = Image.open(image_path)
    image_resized = contain(image, (512, 512))

    output_path = f"{image_path}_processed.png"
    image_resized.save(output_path)

    return output_path

# Process webhook calls
@app.route('/', methods=['POST'])
def webhook():
    envelope = flask.request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        # Decode message
        p2s_image_received_raw = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
        p2s_image_received = json.loads(p2s_image_received_raw, object_hook=payloads.p2s_image_received_decoder)
        logger.debug(f"Received message: {p2s_image_received}")

        # Download / get image into workdir from bucket
        logger.debug("Downloading media from bucket...")
        matted_image_path = f"{workdir}/{p2s_image_received.media_filename}"
        cs_client.get_object(cs_bucket, p2s_image_received.media_filename, matted_image_path)

        # process the image to get it to stickers (max 512px)
        processed_image_path = process_image(matted_image_path)

        # Store the picture to CS
        cs_client.put_object(cs_bucket, p2s_image_received.media_filename + "_processed", processed_image_path)

        # Sends back sticers to user
        bot.send_document(p2s_image_received.chat_id, document=open(processed_image_path, 'rb'))

        return ('', 204)
    
    return "Bad Request", 400


if __name__ == '__main__':
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
