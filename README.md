# Kafka Slack Bot

A simple Slack chatops bot, further writeup [here](TODO).

## Prerequisites
- Python 3.6+
- [Docker](https://www.docker.com/)
- [Kafkacat](https://github.com/edenhill/kafkacat)

## Environment Setup
There are several ways to set up a Python virtual environment, one is with pyenv and pip:

    pyenv install 3.6.3
    pyenv shell 3.6.3
    mkvirtualenv --python=`pyenv which python` mynewenv
    pip install -r requirements.txt

Set up local networking to Kafka/Zookeeper with the following lines in `/etc/hosts`:

    127.0.0.1 kafka
    127.0.0.1 zookeeper

## Usage
Start the supporting services:

    docker-compose up -d

Send some messages:

    for i in `seq 1 3`;
    do
            echo "{\"from\": \"alice\", \"to\":\"bob\", \"amount\": 3}"  | kafkacat -b kafka:9092 -t transactions -p 0
    done

Request application metrics, e.g.:
 

    @little_bot help me!
    @little_bot please show me the Kafka graphs
    @little_bot restart 1

(where `little_bot` is the name you chose when setting up the Slack bot).

