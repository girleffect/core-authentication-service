import json

from django.utils import timezone

import boto3

from ge_kinesis.producer import GEKinesisProducer
from ge_event_log import schemas, utils


# TODO: Make env driven
KINESIS_SESSION = boto3.Session(
    aws_access_key_id="foobar",
    aws_secret_access_key="foobar",
    region_name="us-east-1",
)

# TODO: Make env driven
KINESIS_PRODUCER = GEKinesisProducer(
    stream_name="test-stream",
    boto3_session=KINESIS_SESSION,
    boto3_client_settings={"endpoint_url": "http://localstack:4568"},
    buffer_time=5
)

EVENT_PARTITIONS = {
    "user_login": "user_login",
    "user_logout": "user_logout",
}

def get_timestamp():
    # Timestamp in microseconds since epoch time, use timezone as created_at is
    # not available till after the first creation.
    now = timezone.now()
    microseconds = int(
        now.strftime("%s")
    ) * 1000000 + now.microsecond
    return microseconds


def put_event(event_type, data):
    """
    Used for all Kinesis put record events.
    """
    schema = getattr(schemas, event_type)

    # Basic support for both dict and json strings
    if isinstance(data, str):
        data = json.loads(data)

    # Append timestamp to all data
    # TODO: Site lookup needs to be done, session client_id for lookup, auth
    # service id=0
    #site_id = api_helpers.get_site_for_client(self.client.id)
    data.update(
        {
            "timestamp": get_timestamp(),
            "site_id": 0,
        }
    )
    utils.validate(data, schema)

    # Base producer supports only the singular put event, it does a
    # boto3.client.put_records of all queued events.
    KINESIS_PRODUCER.put(json.dumps(data), partition_key=EVENT_PARTITIONS[event_type])
