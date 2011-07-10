from flask import request

from datahub.core import app, db
from datahub import logic
from datahub.exc import Gone
from datahub.util import request_content, jsonify

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
    data = request_content(request)
    resource = logic.resource.update(owner, resource, data)
    db.session.commit()
    return jsonify(resource)

@app.route('/api/v1/resource/<owner>/<resource>', methods=['DELETE'])
def resource_delete(owner, resource):
    logic.resource.delete(owner, resource)
    db.session.commit()
    raise Gone('Successfully deleted: %s / %s' % (owner, resource))
