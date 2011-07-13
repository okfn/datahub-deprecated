from datahub.core import db
from datahub.exc import NotFound, InternalError
from datahub.model import Event, EventStreamEntry

from datahub.logic.renderers import RENDERERS

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

def latest_by_stream(entity_type, entity_id, limit=50):
    """ Fetch the `limit` latest events that occured on the given
    event stream. """
    events = Event.query.join(EventStreamEntry)
    events = events.filter(EventStreamEntry.entity_type==entity_type)
    events = events.filter(EventStreamEntry.entity_id==entity_id)
    events = events.order_by(Event.time.desc())
    events = events.limit(limit)
    return events.all()

def latest_by_entity(entity, limit=50):
    """ Get events for a specific entity. """
    return latest_by_stream(entity.__tablename__, entity.id, 
                            limit=limit)

def emit(event, streams=[]):
    """ Unlike the other logic.*.create methods, this function 
    expects an instantiated Event object to be passed in. As there
    are many different event types, this seemed the right thing to
    do. """
    streams = set(streams)
    if not event.account in streams:
        streams.add(event.account)
    db.session.add(event)
    for stream in streams:
        entry = EventStreamEntry(stream.__tablename__, stream.id, 
                                 event)
        db.session.add(entry)
    db.session.flush()

def renderer(event):
    """ Retrieve and instantiate an appropriate renderer for this 
    event. """
    try:
        return RENDERERS[type(event)](event)
    except KeyError:
        raise InternalError('No renderer for %s' % type(event))

