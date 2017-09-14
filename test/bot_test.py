from slackbot import bot

import unittest
from slackbot import lag
from slackbot.lag import format_response, TopicOffsets


class TestLag(unittest.TestCase):
    # Assumes Kafka is available at kafka:9092 (mocking would be better)
    def test_on_message_returns_response(self):
        mybot = lag.KafkaLag(get_mock_config())
        response = mybot.report()
        self.assertEquals(2, len(response))

        offsets = response.get('broker1')
        self.assertEquals(2, len(offsets))

        offsets = response.get('broker2')
        self.assertEquals(2, len(offsets))

    def test_format_response(self):
        formatted_response = format_response(get_mock_offset_data())
        self.assertIsNotNone(formatted_response)
        print(formatted_response)


class TestBot(unittest.TestCase):

    def test_on_message_returns_response(self):
        mybot = bot.SlackBot(get_mock_config())
        msg = {
              "subtype": "message",
              "text": "<@little_bot> what is the lag?"
            }
        response = mybot.on_message(msg)
        self.assertTrue('broker2' in response)

    def test_on_message_returns_none_without_atuser(self):
        mybot = bot.SlackBot(get_mock_config())
        msg = {
            "subtype": "message",
            "text": "<@U71T7LTC2> what is the lag?"
        }
        response = mybot.on_message(msg)
        self.assertIsNone(response)

    def test_on_message_returns_help_for_invalid_question(self):
        mybot = bot.SlackBot(get_mock_config())
        msg = {
            "subtype": "message",
            "text": "<@little_bot> what is your name?"
        }
        response = mybot.on_message(msg)
        self.assertTrue('graphs' in response)
        self.assertTrue('help' in response)
        self.assertTrue('lag' in response)

    def test_on_message_returns_none_for_edit(self):
        mybot = bot.SlackBot(get_mock_config())
        msg = {
            "subtype": "message_changed",
            "text": "<@little_bot> what is your name?"
        }
        response = mybot.on_message(msg)
        self.assertIsNone(response)

    def test_get_graph_urls(self):
        mybot = bot.SlackBot(get_mock_config())
        self.assertEquals(4, len(mybot.graph_urls))


def get_mock_config():
    return {
          "broker_groups": {
            "broker2": {
              "consumer_groups": {
                "topic1": {
                  "group_name": "group_id_1"
                },
                "topic2": {
                  "group_name": "group_id_2"
                }
              },
              "brokers": [
                "kafka:9092",
                "kafka:9092"
              ],
              "graphs": {
                  "graph1:": "http://mygraph.com",
                  "graph2:": "http://mygraph.com"
              }
            },
            "broker1": {
              "consumer_groups": {
                "topic1": {
                  "group_name": "group_id_1"
                },
                "topic2": {
                  "group_name": "group_id_2"
                }
              },
              "brokers": [
                "kafka:9092",
                "kafka:9092"
              ],
              "graphs": {
                  "graph3:": "http://mygraph.com",
                  "graph4:": "http://mygraph.com"
              }
            }
          },
          "slack_token": "xoxb",
          "bot_name": "little_bot"
        }


def get_mock_offset_data():
    topic_offsets = {
        "broker1": [
            TopicOffsets('broker1', 'topic1', "group_id_1"),
            TopicOffsets('broker1', 'topic2', "group_id_2"),
        ],
        "broker2": [
            TopicOffsets('broker2', 'topic1', "group_id_1"),
        ]
    }
    for key, topic_offset in topic_offsets.items():
        if key == "broker1":
            for item in topic_offset:
                item.add(0, 50)
                item.add(1, 100)
        else:
            for item in topic_offset:
                item.add(0, 25)
                item.add(1, 75)
    return topic_offsets
