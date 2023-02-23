
# p2sb - Picture to stickers bot
Get chat app stickers of persons from pictures via telegram!

This project is intended to be a playground for GCP services. The bot task is simple: get pictures from users, matt them, postporcess to Telegram's requirements for stickers. You can then forward them to stickersbot to add them to your sets!

Try it out: https://t.me/pic_to_stickers_bot

For additional information check-out my [medium article](https://medium.com/@iacomini.riccardo/build-a-serverless-telegram-bot-on-gcp-with-cloud-run-8d4ec9080b0f)

## General architecture
This project is meant to be a playground for GCP services. The app is designed as a streaming application made of individual specialized components. Cloud Pub/Sub, google's serverless messaging service, connects the individual components, all python applications packaged into containers and running on Cloud Run.

## Repository structure
- **telegrambot**: read messages from telegram, feed the data pipelines with events and images
- **matting**: solate persons from pictures received via telegram
- **postprocess**: postprocess the matted images and send back stickers

The matting component uses a pre-trained matting model on [FastDeploy](https://github.com/PaddlePaddle/FastDeploy). Check out the repository for more info on how to download and run pre-trained matting models.

## How to configire, build and run locally
The app uses client libraries for Pub/Sub and Cloud Storage, but you can still run it locally by running docker, a local emulator of Cloud Pub/Sub, and configuring the app to use local storage instead of Cloud Storage.

There are help scripts to run the emulator and set up topics and subscriptions. Configure variables properly into  **start-pubsub-emu.sh** and run it to run the emulator locally and create the required topics. 

You will need python cloud/pub sub samples, and a virtual enviromnent with its requirements. Check the [GitHub repo](https://github.com/googleapis/python-pubsub/tree/main/samples/snippets) for additional details.

### Configuration
Here are .env files for each component you can place inside each component's directory to run it locally, or to use with docker run to configure the containers:

**telegrambot**

    # General
    LOG_LEVEL="DEBUG"
    APP_TOKEN="INSERT-YOUR-APP-TOKEN"
    TMP_PATH="/tmp/telegrambot-workspace"
    
    # Pub/Sub
    GCP_PROJECT_NAME="YOUR-GCP-PROJECT (as configured in ./start-pub-sub-emu.sh)"
    TOPIC_NAME="YOUR-TOPIC-NAME (as configured in ./start-pub-sub-emu.sh)"
    
    # Cloud Storage
    CS_IMPL="LOCAL_STORAGE"
    MOCK_BUCKET_DIR="/tmp/mock-bucket"
    BUCKET_NAME="YOUR-BUCKET-NAME"
    
    # Local config for pubsub emulator
    PUBSUB_EMULATOR_HOST="localhost:8085"
    PUBSUB_PROJECT_ID="YOUR-GCP-PROJECT (as configured in ./start-pub-sub-emu.sh)"
    

**matting**

    # General config
    WORK_DIR="/tmp/image-matting-workspace"
    SAVE_DIR=${WORK_DIR}/processed
    LOG_LEVEL="DEBUG"
    PORT=8081
    
    # Matting model config - check fastdeploy repo to get the files
    MODEL_PATH="./model.pdmodel"
    PARAMS_PATH="./model.pdiparams"
    CONFIG_PATH="./deploy.yaml"
    
    # Cloud storage config
    CS_IMPL="LOCAL_STORAGE"
    MOCK_BUCKET_DIR="/tmp/mock-bucket"
    BUCKET_NAME="YOUR-BUCKET-NAME"
    
    # Pub/Sub config
    TOPIC_NAME="YOUR-MATTED-TOPIC-NAME"
    GCP_PROJECT_NAME="YOUR-GCP-PROJECT (as configured in ./start-pub-sub-emu.sh)"
    
    # Local config for pubsub emulator
    PUBSUB_EMULATOR_HOST="localhost:8085"
    PUBSUB_PROJECT_ID="YOUR-GCP-PROJECT (as configured in ./start-pub-sub-emu.sh)"

**postprocess**

    # General settings
    LOG_LEVEL="DEBUG"
    TMP_PATH="/tmp/telegrambot-resp"
    APP_TOKEN="YOUR-APP-TOKEN"
    BUCKET_NAME="YOUR-BUCKET-NAME"

### Build and run locally on Docker

Here you have examples for the telegrambot components, but the same commands apply also for the others after replacing tags and doocker file properly.

To build the docker image, from repo home:

    sudo docker build --tag p2sb-telegrambot --file telegrambot/Dockerfile ./

To run the component:

    sudo docker run --network="host" -v /tmp:/tmp p2sb-telegrambot

The --netwrok="host" is needed if you have installed the Cloud pub/sub emulator locally (not as a docker container) and is listening on localhost. 
 
 
