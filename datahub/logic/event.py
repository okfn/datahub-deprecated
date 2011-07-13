from datahub.exc import NotFound
from datahub.model import Event

def get(id):
    """ Get will try to find an event and return None if no event
    found. Use `find` for an exception-generating variant. """
    return Event.query.filter(Event.id==id).first()

def find(id):
    """ Find an event or yield a `NotFound` exception. """
    event = get(id)
    if event is None:
        raise NotFound('No such event: %s' % id)
    return event
