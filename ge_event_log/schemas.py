from ge_event_log import utils

BASE_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "event_type": {
            "type": "object",
        },
        "timestamp": {
            "type": "object",
        },
        "site_id": {
            "type": "object"
        }
    },
    "required": [
        "event_type",
        "timestamp",
        "site_id"
    ],
}


class EventTypes:
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"

    SCHEMAS = {
        USER_LOGIN: {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "event_type": {
                    "type": "string",
                    "pattern": USER_LOGIN
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time"
                },
                "site_id": {
                    "type": "integer"
                },
                "user_id": {
                    "format": "uuid",
                    "type": "string"
                },
            },
            "required": [
                "event_type",
                "timestamp",
                "site_id",
                "user_id"
            ],
        },
        USER_LOGOUT: {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "event_type": {
                    "type": "string",
                    "pattern": USER_LOGOUT
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time"
                },
                "site_id": {
                    "type": "integer"
                },
                "user_id": {
                    "format": "uuid",
                    "type": "string"
                },
            },
            "required": [
                "event_type",
                "timestamp",
                "site_id",
                "user_id"
            ],
        }
    }

# Check all schema definitions
for event_type, schema in EventTypes.SCHEMAS.items():
    utils.validate(schema["properties"], BASE_SCHEMA)
    assert event_type == schema["properties"]["event_type"]["pattern"]
