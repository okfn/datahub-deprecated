from flask import jsonify

from datadeck.core import app
from datadeck.logic import resource

@app.route('/api/v1/resource/<owner>', methods=['GET'])
def resource_index(owner):
    result = resource.list_by_owner(owner)
    return jsonify(list(result))

@app.route('/api/v1/resource/<owner>', methods=['POST'])
def resource_create(owner):
    pass

