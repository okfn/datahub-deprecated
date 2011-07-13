from flask import Blueprint, request

from datahub import logic
from datahub.util import jsonify

event_api = Blueprint('event_api', __name__)

@event_api.route('/<event>', methods=['GET'])
def get(event):
    """ Get a JSON representation of the event. """
    event = logic.event.find(event)
    return jsonify(event)


