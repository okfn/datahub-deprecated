from flask import Blueprint, request

from datahub import logic
from datahub.util import jsonify

event_api = Blueprint('event_api', __name__)

@event_api.route('/<event>', methods=['GET'])
def get(event):
    """ Get a JSON representation of the event. """
    event = logic.event.find(event)
    return jsonify(event)


stream_api = Blueprint('stream_api', __name__)

@stream_api.route('/<type>/<id>', methods=['GET'])
def stream(type, id):
    """ Get the latest events on the given event stream. """
    events = logic.event.latest_by_stream(type, id)
    return jsonify(events)


