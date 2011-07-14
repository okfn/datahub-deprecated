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

