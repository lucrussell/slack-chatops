# Kafka Slack Bot

A Slack bot for getting graphs and other data from Kafka.

## Set Up
To build and run:

```
$ docker-compose up -d
```

This assumes entries for Kafka and Zookeeper in `/etc/hosts`, i.e.:

```
127.0.0.1 kafka
127.0.0.1 zookeeper
```

## Usage
Request application metrics, e.g.: 
 
```
@little_bot help me!
@little_bot what is the lag like today?
@little_bot graph it for me, please
```


