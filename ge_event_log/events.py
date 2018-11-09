import json

import boto3
from environs import Env

from django.utils import timezone

from access_control.rest import ApiException
from authentication_service import api_helpers
from authentication_service.constants import SessionKeys
from authentication_service.utils import get_session_data
from ge_event_log import schemas, utils
from ge_kinesis.producer import GEKinesisProducer

env = Env()

AUTHENTICATION_SERVICE_HARDCODED_SITE_ID = 0

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


def put_event(event_type, data, request=None):
    """
    Used for all Kinesis put record events.
    """

    # TODO: Check if this needs more elegant handling.
    schema = schemas.EventTypes.SCHEMAS[event_type]

    # Basic support for both dict and json strings
    if isinstance(data, str):
        data = json.loads(data)

    # Authentication Service does not have client or site entries
    site_id = AUTHENTICATION_SERVICE_HARDCODED_SITE_ID

    # Lookup the site_id if the request is present.
    if request:
        client_id = get_session_data(request, SessionKeys.CLIENT_ID)
        if client_id:
            # NOTE: This will raise a ImproperlyConfigured if the site does not exist
            site_id = api_helpers.get_site_for_client(client_id)
        else:
            # If no client was present on the request and no site_id was set in
            # data, assume the site is the Authentication Service itself.
            site_id = data.get("site_id", site_id)

    # Append BASE_SCHEMA values to all event data
    data.update(
        {
            "timestamp": timezone.now().isoformat(),
            "site_id": site_id,
            "event_type": event_type
        }
    )
    utils.validate(data, schema)

    # Base producer supports only the singular put event, it does a
    # boto3.client.put_records of all queued events.
    KINESIS_PRODUCER.put(json.dumps(data), partition_key=event_type)
