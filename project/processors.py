import re

from raven.processors import SanitizePasswordsProcessor


class SanitizeHeadersProcessor(SanitizePasswordsProcessor):
    """
    Custom Processor which adds any headers to be additionally omitted.
    """
    # List of headers to omit
    KEYS = SanitizePasswordsProcessor.KEYS.union(["x-api-key"])
