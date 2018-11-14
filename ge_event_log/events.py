import json

import boto3
from environs import Env

from django.utils import timezone

from access_control.rest import ApiException
from authentication_service import api_helpers
from ge_event_log import schemas, utils
from ge_kinesis.producer import GEKinesisProducer

env = Env()


# To ensure there are no Django startup issues, this module does not rely
# on settings.py for setup variables.
# It can also not be instantiated under all circumstances. The extra process
# the producer creates halts some of Django's management commands, as the
# process does not terminate automatically.
if not env.bool("BUILDER", False):
    # Boto3 session that will be used for authentication

    KINESIS_SESSION = boto3.Session(**env.dict("KINESIS_SESSION"))

    # The AsyncProducer that will be used to perform put_records
    PRODUCER_SETTINGS = env.dict("KINESIS_PRODUCER")
    PRODUCER_SETTINGS["boto3_session"] = KINESIS_SESSION

    # Override the boto3 client settings, if needed
    CLIENT_SETTINGS = env.dict("KINESIS_BOTO3_CLIENT_SETTINGS")
    if CLIENT_SETTINGS.get("endpoint_url"):
        PRODUCER_SETTINGS["boto3_client_settings"] = CLIENT_SETTINGS
    KINESIS_PRODUCER = GEKinesisProducer(**PRODUCER_SETTINGS)


def put_event(event_type, site_id, **kwargs):
    """
    Used for all Kinesis put record events.
    """

    # TODO: Check if this needs more elegant handling.
    schema = schemas.EventTypes.SCHEMAS[event_type]

    # Append BASE_SCHEMA values to all event data
    kwargs.update(
        {
            "timestamp": timezone.now().isoformat(),
            "site_id": site_id,
            "event_type": event_type
        }
    )
    utils.validate(kwargs, schema)

    # Base producer supports only the singular put event, it does a
    # boto3.client.put_records of all queued events.
    KINESIS_PRODUCER.put(json.dumps(kwargs), partition_key=event_type)
