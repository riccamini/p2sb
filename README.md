# p2s
Get chat app stickers of persons from pictures via telegram!

This project is intended to be a playground for GCP services. The application is designed on GCP and will use services that I am interested in trying and that can fit the bill.

## Repository structure
- telegrambot: read messages from telegram / write messages back with stickers
- matting: module to isolate persons from pictures received via telegram
- telegrambot_resp: answer back with the sticker!

## How to build and run locally

### telegrambot

From repo home, lunch 
docker build --tag p2s-telegram-client --file telegrambot/Dockerfile ./

to build the docker image

Launch 
sudo docker run --network="host" -v /tmp:/tmp p2s-telegram-client

to run the container. The --netwrok="host" is needed if you intent to run the pubsub emulator and bind it to localhost.



