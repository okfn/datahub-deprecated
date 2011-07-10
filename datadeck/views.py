from flask import jsonify

from datadeck.core import app
from datadeck.logic import resource

@app.route('/api/v1/resource/<user>', methods=['GET'])
def resource_index(user):
    result = resource.list_by_user(user)
    return jsonify(list(result))

@app.route('/api/v1/resource/<user>', methods=['POST'])
def resource_create(user):
    pass

