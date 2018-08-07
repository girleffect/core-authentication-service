import re

from raven.processors import SanitizePasswordsProcessor


class SanitizeHeadersProcessor(SanitizePasswordsProcessor):
    """
    Custom Processor inheriting from the
    """
    # List of headers to omit
    KEYS = frozenset([
        "x-api-key",
    ])
    VALUES_RE = re.compile(r"^(?:\d[ -]*?){13,16}$")
