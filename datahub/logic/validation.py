import re

from formencode import FancyValidator, Invalid

VALID_NAME = re.compile(r"^[a-zA-Z0-9_\-]{2,1999}$")

class Name(FancyValidator):
    """ Check if a given name is valid for resources, datasets or 
    users. """

    def _to_python(self, value, state):
        if VALID_NAME.match(value):
            return value
        raise Invalid('Invalid name.', value, None)


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


class AvailableNodeName(FancyValidator):
    """ Checks if a node with the given name exists for the 
    specified owner. """

    def _to_python(self, value, state):
        from datahub.logic.node import get
        existing = get(state.owner_name, value)
        if existing and (state.current_name is None or \
            state.current_name == value):
            raise Invalid('Name is taken.', value, None)
        return value

class Metadata(FancyValidator):
    """ Checks for arbitrary metadata in a dictionary submitted via 
    the JSON API. """

    def _dict_keys(self, dictionary, value):
        for k, v in dictionary.items():
            if not VALID_NAME.match(k):
                raise Invalid('Invalid metadata key: %s.' % k, value, None)
            if isinstance(v, dict):
                self._dict_keys(v, value)

    def _to_python(self, value, state):
        if not isinstance(value, dict):
            raise Invalid('Metadata must be a dictionary.', value, None)
        self._dict_keys(value, value)
        return value

class AvailableAccountName(FancyValidator):
    """ Checks if a resource with the given name exists for the 
    specified owner. """

    def _to_python(self, value, state):
        from datahub.logic.account import get
        existing = get(value)
        if existing and (state.current_name is None or \
            not state.current_name == value):
            raise Invalid('Name is taken.', value, None)
        return value
