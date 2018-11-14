import jsonschema
import uuid

@jsonschema.FormatChecker.cls_checks("uuid")
def check_uuid_format(instance):
    try:
        uuid.UUID(instance)
        return True
    except ValueError:
        return False


# The instance of the format checker must be created after
# the UUID format checker was registered.
_FORMAT_CHECKER = jsonschema.FormatChecker()


def validate(instance, schema):
    jsonschema.validate(
        instance,
        schema=schema,
        format_checker=_FORMAT_CHECKER
    )
