from flask import request

from datadeck.core import app, db
from datadeck import logic
from datadeck.util import request_content, jsonify

@app.route('/api/v1/resource/<owner>', methods=['GET'])
def resource_index(owner):
    result = logic.resource.list_by_owner(owner)
    return jsonify(list(result))

@app.route('/api/v1/resource/<owner>', methods=['POST'])
def resource_create(owner):
    data = request_content(request)
    resource = logic.resource.create(owner, data)
    db.session.commit()
    return jsonify({'status': 'ok', 'name': resource.name})

@app.route('/api/v1/resource/<owner>/<resource>', methods=['GET'])
def resource_get(owner, resource):
    resource = logic.resource.find(owner, resource)
    return jsonify(resource)

@app.route('/api/v1/resource/<owner>/<resource>', methods=['PUT'])
def resource_update(owner, resource):
    pass

@app.route('/api/v1/resource/<owner>/<resource>', methods=['DELETE'])
def resource_delete(owner, resource):
    pass

