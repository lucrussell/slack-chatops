from pykafka import KafkaClient


class KafkaLag(object):

    def __init__(self, config=None):
        self.broker_groups = config.get('broker_groups')

    def report(self):
        lag_report = {}
        for broker_group, value in self.broker_groups.items():
            kafka_client = KafkaClient(hosts=','.join(value['brokers']))
            consumers = self.broker_groups[broker_group].get('consumer_groups')
            group_items = consumers.items()
            lag_report[broker_group] = []
            for topic_name, details in group_items:

                group_name = details['group_name']
                topic_offsets = TopicOffsets(broker_group,
                                             topic_name, group_name)
                topic = kafka_client.topics[topic_name.encode('utf-8')]
                latest_offsets = topic.latest_available_offsets()

                try:
                    consumer = topic.get_simple_consumer(
                        consumer_group=group_name.encode('utf-8'),
                        auto_start=False)
                    consumed_offsets = consumer.fetch_offsets()
                finally:
                    consumer.stop()

                for partition, res in consumed_offsets:
                    lag = latest_offsets[partition].offset[0] - res.offset
                    topic_offsets.add(partition, lag)

                lag_report[broker_group].append(topic_offsets)
        return lag_report


def format_response(offset_data):
    res = '```'
    for broker, broker_offsets in offset_data.items():
        res += '{}:\n'.format(broker)
        for offset in broker_offsets:
            res += '\n'
            res += '\t {}:'.format(offset.topic_name)
            for item in offset.partition_lag.items():
                res += '\n'
                res += '\t \t partition {}: \t {}'.format(item[0], item[1])
                res += '\n'
    res += '```'
    return res


class TopicOffsets(object):
    def __init__(self, broker_group, topic_name, group_name):
        self.broker_group = broker_group
        self.topic_name = topic_name
        self.group_name = group_name
        self.partition_lag = {}

    def add(self, partition_id, lag):
        self.partition_lag[partition_id] = lag

    def __repr__(self):
        rep = {
            'broker_group': self.broker_group,
            'topic_name': self.topic_name,
            'group_name': self.group_name,
            'lag': self.partition_lag,
        }
        return str(rep)
