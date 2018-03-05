"""
Do not modify this file. It is generated from the Swagger specification.

Container module for JSONSchema definitions.
This does not include inlined definitions.

The pretty-printing functionality provided by the json module is superior to
what is provided by pformat, hence the use of json.loads().
"""
import json

# When no schema is provided in the definition, we use an empty schema
__UNSPECIFIED__ = {}

client = json.loads("""
{
    "properties": {
        "_post_logout_redirect_uris": {
            "description": "New-line delimited list of post-logout redirect URIs",
            "type": "string"
        },
        "_redirect_uris": {
            "description": "New-line delimited list of redirect URIs",
            "type": "string"
        },
        "client_id": {
            "description": "",
            "type": "string"
        },
        "contact_email": {
            "description": "",
            "type": "string"
        },
        "id": {
            "description": "",
            "type": "integer"
        },
        "logo": {
            "description": "",
            "format": "uri",
            "type": "string"
        },
        "name": {
            "description": "",
            "type": "string"
        },
        "require_consent": {
            "description": "If disabled, the Server will NEVER ask the user for consent.",
            "type": "boolean"
        },
        "response_type": {
            "description": "",
            "type": "string"
        },
        "reuse_consent": {
            "description": "If enabled, the Server will save the user consent given to a specific client, so that user won't be prompted for the same authorization multiple times.",
            "type": "boolean"
        },
        "terms_url": {
            "description": "External reference to the privacy policy of the client.",
            "type": "string"
        },
        "website_url": {
            "description": "",
            "type": "string"
        }
    },
    "required": [
        "client_id",
        "response_type"
    ],
    "type": "object"
}
""")

user = json.loads("""
{
    "properties": {
        "avatar": {
            "format": "uri",
            "type": "string"
        },
        "birth_date": {
            "format": "date",
            "type": "string"
        },
        "country_code": {
            "maxLength": 2,
            "type": "string"
        },
        "date_joined": {
            "description": "",
            "format": "date",
            "readOnly": true,
            "type": "string"
        },
        "email": {
            "description": "",
            "format": "email",
            "type": "string"
        },
        "email_verified": {
            "type": "boolean"
        },
        "first_name": {
            "description": "",
            "type": "string"
        },
        "gender": {
            "type": "string"
        },
        "id": {
            "description": "A UUID identifying the user",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
        },
        "is_active": {
            "description": "Designates whether this user should be treated as active. Deselect this instead of deleting accounts.",
            "type": "boolean"
        },
        "last_login": {
            "description": "",
            "readOnly": true,
            "type": "string"
        },
        "last_name": {
            "description": "",
            "type": "string"
        },
        "msisdn": {
            "maxLength": 15,
            "type": "string"
        },
        "msisdn_verified": {
            "type": "boolean"
        },
        "username": {
            "description": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
            "readOnly": true,
            "type": "string"
        }
    },
    "required": [
        "id",
        "username",
        "is_active",
        "date_joined"
    ],
    "type": "object"
}
""")

user_update = json.loads("""
{
    "minProperties": 1,
    "properties": {
        "avatar": {
            "format": "uri",
            "type": "string"
        },
        "birth_date": {
            "format": "date",
            "type": "string"
        },
        "country_code": {
            "maxLength": 2,
            "type": "string"
        },
        "email": {
            "description": "",
            "format": "email",
            "type": "string"
        },
        "email_verified": {
            "type": "boolean"
        },
        "first_name": {
            "description": "",
            "type": "string"
        },
        "gender": {
            "type": "string"
        },
        "is_active": {
            "description": "Designates whether this user should be treated as active. Deselect this instead of deleting accounts.",
            "type": "boolean"
        },
        "last_name": {
            "description": "",
            "type": "string"
        },
        "msisdn": {
            "maxLength": 15,
            "type": "string"
        },
        "msisdn_verified": {
            "type": "boolean"
        }
    },
    "type": "object"
}
""")

