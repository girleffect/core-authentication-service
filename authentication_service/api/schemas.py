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

Address = json.loads("""
{
    "description": "OIDC Address structure", 
    "properties": {
        "country": {
            "type": "string"
        }, 
        "locality": {
            "type": "string"
        }, 
        "postal_code": {
            "type": "string"
        }, 
        "region": {
            "type": "string"
        }, 
        "street_address": {
            "type": "string"
        }
    }
}
""")

Client = json.loads("""
{
    "description": "Client object", 
    "properties": {
        "application_type": {
            "type": "string"
        }, 
        "client_id": {
            "type": "string"
        }, 
        "client_name": {
            "type": "string"
        }, 
        "client_uri": {
            "type": "string"
        }, 
        "contacts": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "default_max_age": {
            "format": "int64", 
            "type": "integer"
        }, 
        "default_scopes": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "grant_types": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "logo_uri": {
            "type": "string"
        }, 
        "policy_uri": {
            "type": "string"
        }, 
        "redirect_uris": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "response_types": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "tos_uri": {
            "type": "string"
        }
    }, 
    "required": [
        "client_name", 
        "client_uri"
    ]
}
""")

OAuth2Error = json.loads("""
{
    "description": "Error Response defined as in Section 5.2 of OAuth 2.0 [RFC6749].\n", 
    "properties": {
        "error": {
            "type": "string"
        }, 
        "error_description": {
            "type": "string"
        }
    }, 
    "required": [
        "error"
    ]
}
""")

ProblemDetail = json.loads("""
{
    "description": "HTTP Problem Detail\n", 
    "properties": {
        "detail": {
            "description": "Human-readable explanation specific to this occurrence of the problem.\n", 
            "type": "string"
        }, 
        "status": {
            "description": "The HTTP status code for this occurrence of the problem.\n", 
            "type": "integer"
        }, 
        "title": {
            "description": "Human-readable summary of the problem type.\n", 
            "type": "string"
        }, 
        "type": {
            "default": "about:blank", 
            "type": "string"
        }
    }, 
    "required": [
        "type", 
        "status"
    ]
}
""")

Session = json.loads("""
{
    "description": "Session object", 
    "properties": {
        "authenticated_at": {
            "format": "date-time", 
            "type": "string"
        }, 
        "client_id": {
            "type": "string"
        }, 
        "client_name": {
            "type": "string"
        }, 
        "client_uri": {
            "type": "string"
        }, 
        "concluded_at": {
            "format": "date-time", 
            "type": "string"
        }, 
        "connected_at": {
            "format": "date-time", 
            "type": "string"
        }, 
        "contacts": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "created_at": {
            "type": "string"
        }, 
        "deleted_at": {
            "format": "date-time", 
            "type": "string"
        }, 
        "logo_uri": {
            "type": "string"
        }, 
        "nonce": {
            "type": "string"
        }, 
        "policy_uri": {
            "type": "string"
        }, 
        "redirect_uri": {
            "type": "string"
        }, 
        "response_mode": {
            "type": "string"
        }, 
        "response_type": {
            "type": "string"
        }, 
        "scopes": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "scopes_optional": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "scopes_required": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "scopes_seen": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "scopes_signed": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "session_id": {
            "type": "string"
        }, 
        "session_state": {
            "type": "string"
        }, 
        "session_uri": {
            "type": "string"
        }, 
        "sub": {
            "type": "string"
        }, 
        "tokens_seen": {
            "items": {
                "type": "string"
            }, 
            "type": "array"
        }, 
        "tos_uri": {
            "type": "string"
        }, 
        "version": {
            "type": "integer"
        }
    }
}
""")

Token = json.loads("""
{
    "description": "Successful token response\n", 
    "properties": {
        "access_token": {
            "description": "The access token issued by the authorization server.", 
            "type": "string"
        }, 
        "expires_at": {
            "description": "The time the access token will expire in seconds since epoch.", 
            "format": "int64", 
            "type": "integer"
        }, 
        "expires_in": {
            "description": "The lifetime in seconds of the access token.", 
            "format": "int32", 
            "type": "integer"
        }, 
        "id_token": {
            "description": "ID Token value associated with the authenticated session.", 
            "type": "string"
        }, 
        "refresh_token": {
            "description": "The refresh token issued to the client, if any.", 
            "type": "string"
        }, 
        "scope": {
            "description": "The scope of the granted tokens.", 
            "type": "string"
        }, 
        "token_type": {
            "type": "string"
        }
    }, 
    "required": [
        "token_type"
    ]
}
""")

UserInfo = json.loads("""
{
    "description": "OIDC UserInfo structure", 
    "properties": {
        "address": {
            "description": "OIDC Address structure", 
            "properties": {
                "country": {
                    "type": "string"
                }, 
                "locality": {
                    "type": "string"
                }, 
                "postal_code": {
                    "type": "string"
                }, 
                "region": {
                    "type": "string"
                }, 
                "street_address": {
                    "type": "string"
                }
            }, 
            "x-scope": [
                "", 
                "#/responses/UserInfo", 
                "#/definitions/UserInfo"
            ]
        }, 
        "email": {
            "type": "string"
        }, 
        "email_verified": {
            "type": "boolean"
        }, 
        "family_name": {
            "type": "string"
        }, 
        "given_name": {
            "type": "string"
        }, 
        "name": {
            "type": "string"
        }, 
        "phone_number": {
            "type": "string"
        }, 
        "phone_number_verified": {
            "type": "boolean"
        }, 
        "sub": {
            "type": "string"
        }
    }, 
    "required": [
        "sub"
    ]
}
""")

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
        "client_type": {
            "description": "<b>Confidential</b> clients are capable of maintaining the confidentiality of their credentials. <b>Public</b> clients are incapable.", 
            "type": "string"
        }, 
        "contact_email": {
            "description": "", 
            "type": "string"
        }, 
        "jwt_alg": {
            "description": "Algorithm used to encode ID Tokens.", 
            "type": "string"
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

