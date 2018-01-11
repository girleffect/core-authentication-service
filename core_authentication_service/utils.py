def update_form_fields(form, required=[]):
    """Update form fields and widgets.

    form --  Instance of a form.
    required -- list of fields to toggle required for.

    Helper method for setting field and widget atrributes, can
    be used for any form isntance.
    """

    # For the event where required is all that needs to be toggled, a list will
    # suffice.

    import pdb; pdb.set_trace()
    for field in required:
        form.fields[field].required = True
        form.fields[field].widget.is_required = True
