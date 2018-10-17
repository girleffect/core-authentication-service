import warnings
from functools import wraps


class generic_deprecation(object):
    def __init__(self, message, warning_class=DeprecationWarning, stack_level=2):
        self.message = message
        self.warning_class = warning_class
        self.stack_level = stack_level

    def __call__(self, method):
        def wrapped(*args, **kwargs):
            warnings.warn(self.message, self.warning_class, self.stack_level)
            return method(*args, **kwargs)
        return wrapped


def required_form_fields_label_alter(init_func, required_character=None):
    """
    Decorator for Django form's __init__ method.

    Appends an asterisk or provided character to labels of fields that are
    required.
    """
    @wraps(init_func)
    def _wrapped(*args, **kwargs):
        # Form needs to be initialised before labels are changed
        init = init_func(*args, **kwargs)

        # Append required character to the existing label
        for name, field in args[0].fields.items():
            # NOTE: If the label was not specified on the field, there is
            # nothing to append to.
            if field.required and field.label:
                field.label += f" {required_character or '*'}"
        return init
    return _wrapped
