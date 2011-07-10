from flask import jsonify, request

from datadeck.core import app, db
from datadeck.logic import resource
from datadeck.util import request_content

@app.route('/api/v1/resource/<owner>', methods=['GET'])
def resource_index(owner):
    result = resource.list_by_owner(owner)
    return jsonify(list(result))

@app.route('/api/v1/resource/<owner>', methods=['POST'])
def resource_create(owner):
    data = request_content(request)
    res = resource.create(owner, data)
    db.session.commit()
    return jsonify({'status': 'ok', 'name': res.name})

@app.route('/api/v1/resource/<owner>/<resource>', methods=['GET'])
def resource_get(owner, resource):
    pass

@app.route('/api/v1/resource/<owner>/<resource>', methods=['PUT'])
def resource_update(owner, resource):
    pass

@app.route('/api/v1/resource/<owner>/<resource>', methods=['DELETE'])
def resource_delete(owner, resource):
    pass

