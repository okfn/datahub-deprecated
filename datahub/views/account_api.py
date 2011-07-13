from flask import Blueprint, request

from datahub import logic
from datahub.util import request_content, jsonify

api = Blueprint('account_api', __name__)

@api.route('/<account>', methods=['GET'])
def get(account):
    """ Get a JSON representation of the account. """
    account = logic.account.find(account)
    return jsonify(account)

@api.route('/<account>', methods=['PUT'])
def update(account):
    """ Update the data of the account profile. """
    data = request_content(request)
    account = logic.account.update(account, data)
    return jsonify(account)
