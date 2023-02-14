#!/bin/bash

PUBSUB_TEST_PROJECT=p2s-test-prj
PUBSUB_INCOMING_TOPIC=p2s-incoming
PUBSUB_MATTED_TOPIC=p2s-matted
PUBSUB_PROCESSED_TOPIC=p2s-processed

PUBSUB_VENV_PATH=/home/riccamini/workspace/python-venvs/pubsub-client
PUBSUB_SNIPPETS_PATH=/home/riccamini/workspace/pubsub-samples/python-pubsub/samples/snippets

export PUBSUB_PROJECT_ID=${PUBSUB_TEST_PROJECT}
export PUBSUB_EMULATOR_HOST=localhost:8085

nohup gcloud beta emulators pubsub start --project=${PUBSUB_TEST_PROJECT} > pubsub-emu.log 2>&1 & echo $! > run.pid

sleep 5

echo "Creating ${PUBSUB_INCOMING_TOPIC} ..."
${PUBSUB_VENV_PATH}/bin/python ${PUBSUB_SNIPPETS_PATH}/publisher.py ${PUBSUB_TEST_PROJECT} create ${PUBSUB_INCOMING_TOPIC}

echo "Creating ${PUBSUB_MATTED_TOPIC} ..."
${PUBSUB_VENV_PATH}/bin/python ${PUBSUB_SNIPPETS_PATH}/publisher.py ${PUBSUB_TEST_PROJECT} create ${PUBSUB_MATTED_TOPIC}

echo "Creating ${PUBSUB_PROCESSED_TOPIC} ..."
${PUBSUB_VENV_PATH}/bin/python ${PUBSUB_SNIPPETS_PATH}/publisher.py ${PUBSUB_TEST_PROJECT} create ${PUBSUB_PROCESSED_TOPIC}




