import re

from formencode import FancyValidator, Invalid

VALID_NAME = re.compile(r"^[a-zA-Z0-9_\-]{1,1999}$")

class Name(FancyValidator):
    """ Check if a given name is valid for resources, datasets or 
    users. """

    def _to_python(self, value, state):
        if not VALID_NAME.match(value):
            raise Invalid('Invalid name.', value, None)
        return value


class URL(FancyValidator):
    """ Check if the given reference is a valid URL. """

    def _to_python(self, value, state):
        if not ':' in value:
            raise Invalid('No schema in URL', value, None)
        schema, url = value.split(':', 1)
        if not schema.lower().strip() in ['http', 'https', 'ftp']:
            raise Invalid('Invalid schema: %s' % schema, value, None)
        # TODO: Introduce normalization and possibly collision detection
        return value


class AvailableResourceName(FancyValidator):
    """ Checks if a resource with the given name exists for the 
    specified owner. """

    def _to_python(self, value, state):
        from datahub.logic.resource import get
        existing = get(state.owner_name, value)
        if existing and (state.current_name is None or \
            state.current_name == value):
            raise Invalid('Name is taken.', value, None)
        return value
