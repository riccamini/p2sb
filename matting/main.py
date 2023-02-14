import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from utils import payloads, fileutils
from mattingservice import MattingService
from utils.cloudstorage import CloudStorageClient 
from google.cloud import pubsub_v1
from flask import Flask, request

from dotenv import load_dotenv
load_dotenv()

import base64
import json
import time
import logging

app = Flask(__name__)

matting_service = MattingService(os.getenv("MODEL_PATH"), os.getenv("PARAMS_PATH"), os.getenv("CONFIG_PATH"), os.getenv("SAVE_DIR"))

cs_client = CloudStorageClient()
cs_bucket = os.getenv('BUCKET_NAME')
workdir = os.getenv('WORK_DIR') # Tmp dir for holding media downloaded before matting

# Setup scratch-dir, output dir
fileutils.setup_dir(os.getenv('WORK_DIR'))
fileutils.setup_dir(os.getenv("SAVE_DIR"))

gcp_project_name= os.getenv('GCP_PROJECT_NAME')
topic_name = os.getenv('TOPIC_NAME')
topic_path = f"projects/{gcp_project_name}/topics/{topic_name}"

pubsub_client = pubsub_v1.PublisherClient()

# Logger init
logging.basicConfig(
    level=os.getenv('LOG_LEVEL'),
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Started!")
logger.debug("Environment configuration: "+str(os.environ))


@app.route("/", methods=["POST"])
def index():
    logger.debug("Request received")
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        logger.error(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:

        # Decode message
        p2s_image_received_raw = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
        p2s_image_received = json.loads(p2s_image_received_raw, object_hook=payloads.p2s_image_received_decoder)
        logger.info(f"Received message: {p2s_image_received}")
        
        # Download / get image into workdir from bucket
        logger.info("Downloading media from bucket...")
        cs_client.get_object(cs_bucket, p2s_image_received.media_filename, f"{workdir}/{p2s_image_received.media_filename}")

        # Matt image
        logger.info(f"Matting image {p2s_image_received.media_filename} ...")
        output_image_complete_path = matting_service.matt_image(f"{workdir}/{p2s_image_received.media_filename}")
        
        # Upload result to bucket
        logger.info(f"Uploading results to bucket {cs_bucket} ...")
        cs_client.put_object(cs_bucket, p2s_image_received.media_filename+"_matted", output_image_complete_path)

        p2s_image_processed = payloads.P2SMessage(p2s_image_received.chat_id, p2s_image_received.media_filename+"_matted", \
            p2s_image_received.user, str(time.time()), "P2SImageMatted")

        # Send message through pub/sub topic
        logger.info(f"Sending message to output topic {topic_path}")
        future = pubsub_client.publish(topic_path, p2s_image_processed.get_bytes())
        message_id = future.result()

        logger.debug(f"Message sent with id: {message_id}")

    return ("", 204)


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)