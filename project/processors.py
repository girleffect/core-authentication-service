import re

from raven.processors import SanitizePasswordsProcessor


class SanitizeHeadersProcessor(SanitizePasswordsProcessor):
    """
    Custom Processor inheriting from the
    """
    # List of headers to omit
    KEYS = SanitizePasswordsProcessor.KEYS.union(["x-api-key"])
