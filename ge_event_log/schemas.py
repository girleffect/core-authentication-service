BASE_SCHEMA = {
    "required": [
        "event_type",
        "timestamp",
        "site_id"
    ],
    "type": "object",
    "properties": {
        "event_type": {
            "type": "string",
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "site_id": {
            "type": "integer"
        }
    },
}

user_login = {
    "required": [
        "user_id",
    ],
    "type": "object",
    "properties": {
        "user_id": {
            "format": "uuid",
            "type": "string"
        },
    }
}
