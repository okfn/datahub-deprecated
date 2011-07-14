from flask import Blueprint, request, redirect, url_for

from datahub import logic
from datahub.util import request_content, jsonify
from datahub.exc import Gone

api = Blueprint('dataset_api', __name__)

@api.route('/<owner>', methods=['GET'])
def index(owner):
    """ List all the datasets of a particular user. """
    result = logic.dataset.list_by_owner(owner)
    return jsonify(list(result))

@api.route('/<owner>', methods=['POST'])
def create(owner):
    """ Create a new dataset for the given user. """
    data = request_content(request)
    dataset = logic.dataset.create(owner, data)
    return redirect(url_for('.get', owner=owner, 
                            dataset=dataset.name))

@api.route('/<owner>/<dataset>', methods=['GET'])
def get(owner, dataset):
    """ Get a JSON representation of the dataset. """
    dataset = logic.dataset.find(owner, dataset)
    return jsonify(dataset)

@api.route('/<owner>/<dataset>/resources', methods=['GET'])
def resources_get(owner, dataset):
    """ Get a JSON representation of the resources in this dataset. """
    resources = logic.dataset.list_resources(owner, dataset)
    return jsonify(resources)

@api.route('/<owner>/<dataset>/resources', methods=['POST'])
def resources_add(owner, dataset):
    """ Add a resource to this dataset. """
    data = request_content(request)
    logic.dataset.add_resource(owner, dataset, data)
    return redirect(url_for('.resources_get', owner=owner, 
                            dataset=dataset))

@api.route('/<owner>/<dataset>/resources/<resource_owner>/<resource_name>', methods=['DELETE'])
def resources_remove(owner, dataset, resource_owner, resource_name):
    """ Add a resource to this dataset. """
    logic.dataset.remove_resource(owner, dataset, resource_owner, resource_name)
    return redirect(url_for('.resources_get', owner=owner, 
                            dataset=dataset))

@api.route('/<owner>/<dataset>', methods=['PUT'])
def update(owner, dataset):
    """ Update the data of the dataset. """
    data = request_content(request)
    dataset = logic.dataset.update(owner, dataset, data)
    return jsonify(dataset)

@api.route('/<owner>/<dataset>', methods=['DELETE'])
def delete(owner, dataset):
    """ Delete the dataset. """
    logic.dataset.delete(owner, dataset)
    raise Gone('Successfully deleted: %s / %s' % (owner, dataset))

