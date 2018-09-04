import asyncio
import functools
import logging
from types import FunctionType, ModuleType
from typing import Type

from prometheus_client import Histogram, Counter

logger = logging.getLogger(__name__)

H = Histogram(f"authentication_service_call_duration_seconds", "API call duration (s)",
              ["call"])


def _prometheus_class_metric_decorator(f: FunctionType):
    """
    A Prometheus decorator adding timing metrics to a function in a class.
    asynchronous ones when used as a decorator.
    :param f: The function for which to capture metrics
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with H.labels(call=f.__name__).time():
            return f(*args, **kwargs)

    return wrapper


def add_prometheus_metrics_for_class(klass: Type):
    """
    Convenience function applying the Prometheus metrics decorator to the
    specified class functions.
    :param klass: The class to which the instrumentation will be applied
    """
    decorate_all_in_class(klass, _prometheus_class_metric_decorator, [])


def decorate_all_in_class(klass: Type, decorator: FunctionType, whitelist: list):
    """
    Decorate all functions in a class with the specified decorator
    :param klass: The class to interrogate
    :param decorator: The decorator to apply
    :param whitelist: Functions not to be decorated.
    """
    for name in dir(klass):
        if name not in whitelist:
            obj = getattr(klass, name)
            if isinstance(obj, FunctionType) or asyncio.iscoroutinefunction(obj):
                logger.debug(f"Adding metrics to {klass.__name__}:{name}")
                setattr(klass, name, decorator(obj))
            else:
                logger.debug(f"No metrics on {klass.__name__}:{name} because it is not a coroutine or "
                             f"function")
