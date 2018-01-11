def update_form_fields(form, required=[], validators={}, fields_data={}):
    """Update form fields and widgets.

    form --  Instance of a form.
    required -- list of fields to toggle required for.
    validators -- a dictionary
        {
            "<fieldname>": [<list of validators>]
        }
    fields_data -- a dictionary
        {
            "<fieldname>": {
                "attributes": {
                    <attribute>: <value>
                },
            }
        }

    Helper method for setting field and widget atrributes, can
    be used for any form instance. Sets attributes on both fields and widgets.
    """

    # For the event where required is all that needs to be toggled, a list will
    # suffice.
    for field in required:
        form.fields[field].required = True
        form.fields[field].widget.is_required = True

    # Set validators on fields.
    for field, data in validators.items():
        form.fields[field].validators = data

    # Update field and widget attributes.
    for field, data in fields_data.items():

        if data.get("attributes", None):
            widget = form.fields[field].widget
            field = form.fields[field]

            # Special case, allow for the assignment of a different input type.
            if data["attributes"].get("type"):
                widget.input_type = data["attributes"].pop(
                    "type", widget.input_type
                )

            # Widgets for the most part make use of a dictionary structure, so
            # just update the dictionary blindly.
            widget.attrs.update(data["attributes"])

            # Fields make use of instance attributes, so it requires a
            # different approach.
            for attr, val in data["attributes"].items():
                setattr(field, attr, val)
