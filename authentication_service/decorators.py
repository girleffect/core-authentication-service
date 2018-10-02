import warnings


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


class required_form_fields_label_alter(object):
    """
    Decorator for Django form's __init__ method.

    Appends an asterisk or provided character to labels of fields that are
    required.
    """
    def __init__(self, required_character=None):
        self.required_character = required_character or "*"

    def __call__(self, method):
        def wrapped(*args, **kwargs):
            # Form needs to be initialised before labels are changed
            init = method(*args, **kwargs)

            # Append required character to the existing label
            for name, field in args[0].fields.items():
                if field.required:
                    field.label += f" {self.required_character}"
            return init
        return wrapped
