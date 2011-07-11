from flask import request

from formencode import Invalid

from datahub.core import app
from datahub import logic
from datahub.util import response_format, jsonify
from datahub import views

@app.before_request
def basic_authentication():
    if 'Authorization' in request.headers:
        authorization = request.headers.get('Authorization')
        authorization = authorization.split(' ', 1)[-1]
        login, password = authorization.decode('base64').split(':', 1)
        logic.user.login({'login': login, 'password': password})

@app.errorhandler(404)
def handle_exceptions(exc):
    format = response_format(app, request)
    if format == 'json':
        body = {'status': exc.code,
                'name': exc.name,
                'description': exc.get_description(request.environ)}
        return jsonify(body, status=exc.code,
                       headers=exc.get_headers(request.environ))
    return exc

@app.errorhandler(Invalid)
def handle_invalid(exc):
    format = response_format(app, request)
    if format == 'json':
        body = {'status': 400,
                'name': 'Invalid Data',
                'description': unicode(exc),
                'errors': exc.unpack_errors()}
        return jsonify(body, status=400)
    return exc


if __name__ == "__main__":
    app.run()

