#!/bin/bash

PUBSUB_GCP_PROJECT=p2s-test-prj

PUBSUB_INCOMING_TOPIC=p2s-incoming
PUBSUB_INCOMING_SUBSCRIPTION=p2s-incoming-subscr
PUBSUB_INCOMING_ENDPOINT=http://127.0.0.1:8080

PUBSUB_MATTED_TOPIC=p2s-matted
PUBSUB_MATTED_SUBSCRIPTION=p2s-matted-subscr
PUBSUB_MATTED_ENDPOINT=http://127.0.0.1:8081

PUBSUB_PROCESSED_TOPIC=p2s-processed
PUBSUB_PROCESSED_SUBSCRIPTION=p2s-processed-subscr
PUBSUB_PROCESSED_ENDPOINT=http://127.0.0.1:8082

PUBSUB_VENV_PATH=/home/riccamini/workspace/python-venvs/pubsub-client
PUBSUB_SNIPPETS_PATH=/home/riccamini/workspace/pubsub-samples/python-pubsub/samples/snippets

export PUBSUB_PROJECT_ID=p2s-test-prj
export PUBSUB_EMULATOR_HOST=localhost:8085

# Subscribe endpoint to topic
${PUBSUB_VENV_PATH}/bin/python ${PUBSUB_SNIPPETS_PATH}/subscriber.py ${PUBSUB_PROJECT_ID} create-push ${PUBSUB_INCOMING_TOPIC} ${PUBSUB_INCOMING_SUBSCRIPTION} ${PUBSUB_INCOMING_ENDPOINT}

# Subscribe endpoint to topic
${PUBSUB_VENV_PATH}/bin/python ${PUBSUB_SNIPPETS_PATH}/subscriber.py ${PUBSUB_PROJECT_ID} create-push ${PUBSUB_MATTED_TOPIC} ${PUBSUB_MATTED_SUBSCRIPTION} ${PUBSUB_MATTED_ENDPOINT}

# Subscribe endpoint to topic
${PUBSUB_VENV_PATH}/bin/python ${PUBSUB_SNIPPETS_PATH}/subscriber.py ${PUBSUB_PROJECT_ID} create-push ${PUBSUB_PROCESSED_TOPIC} ${PUBSUB_PROCESSED_SUBSCRIPTION} ${PUBSUB_PROCESSED_ENDPOINT}
