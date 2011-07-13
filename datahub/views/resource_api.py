from flask import Blueprint, request, redirect, url_for

from datahub import logic
from datahub.util import request_content, jsonify
from datahub.exc import Gone

api = Blueprint('resource_api', __name__)

@api.route('/<owner>', methods=['GET'])
def index(owner):
    """ List all the resources of a particular user. """
    result = logic.resource.list_by_owner(owner)
    return jsonify(list(result))

@api.route('/<owner>', methods=['POST'])
def create(owner):
    """ Create a new resource for the given user. """
    data = request_content(request)
    resource = logic.resource.create(owner, data)
    return redirect(url_for('.get', owner=owner, 
                            resource=resource.name))

@api.route('/<owner>/<resource>', methods=['GET'])
def get(owner, resource):
    """ Get a JSON representation of the resource. """
    resource = logic.resource.find(owner, resource)
    return jsonify(resource)

@api.route('/<owner>/<resource>', methods=['PUT'])
def update(owner, resource):
    """ Update the data of the resource. """
    data = request_content(request)
    resource = logic.resource.update(owner, resource, data)
    return jsonify(resource)

@api.route('/<owner>/<resource>', methods=['DELETE'])
def delete(owner, resource):
    """ Delete the resource. """
    logic.resource.delete(owner, resource)
    raise Gone('Successfully deleted: %s / %s' % (owner, resource))

