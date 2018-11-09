import multiprocessing

from kinesis.producer import AsyncProducer

import logging
LOGGER = logging.getLogger(__name__)
class GEAsyncProducer(AsyncProducer):
    """
    Overriden AsyncProducer from kinesis-python package.
    Provides the ability to change the client setup as well, specifically the
    endpoint_url.
    """

    # https://github.com/NerdWalletOSS/kinesis-python/blob/master/src/kinesis/producer.py#L64
    def __init__(self, stream_name, buffer_time, queue, max_count=None,
            max_size=None, boto3_session=None, boto3_client_settings=None):
        self.stream_name = stream_name
        self.buffer_time = buffer_time
        self.queue = queue
        self.records = []
        self.next_records = []
        self.alive = True
        self.max_count = max_count or self.MAX_COUNT
        self.max_size = max_size or self.MAX_SIZE
        boto3_client_settings = {} or boto3_client_settings

        if boto3_session is None:
            boto3_session = boto3.Session()
        client_settings = {"service_name": "kinesis"}
        client_settings.update(boto3_client_settings)
        self.client = boto3_session.client(**client_settings)

        self.start()


# Based on https://github.com/NerdWalletOSS/kinesis-python/blob/master/src/kinesis/producer.py:class KinesisProducer
class GEKinesisProducer:
    def __init__(self, stream_name, buffer_time=0.5, max_count=None,
            max_size=None, boto3_session=None, boto3_client_settings=None, producer_class=None, queue=None):
        self.queue = queue or multiprocessing.Queue()
        kwargs = {
            "stream_name": stream_name,
            "buffer_time": buffer_time,
            "queue": self.queue,
            "max_count": max_count,
            "max_size": max_size,
            "boto3_session": boto3_session,
            "boto3_client_settings": boto3_client_settings
        }
        self.async_producer = GEAsyncProducer(**kwargs)

    def put(self, data, explicit_hash_key=None, partition_key=None):
        self.queue.put((data, explicit_hash_key, partition_key))
