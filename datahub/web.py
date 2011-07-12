from flask import Response, request
from flaskext.gravatar import Gravatar
from werkzeug.exceptions import Unauthorized
from formencode import Invalid

from datahub.core import app, current_user
from datahub import logic
from datahub.util import response_format, jsonify
from datahub import views

gravatar = Gravatar(app, size=32, rating='g',
                    default='retro')


@app.context_processor
def set_current_user():
    return dict(current_user=current_user)

@app.before_request
def basic_authentication():
    """ Attempt HTTP basic authentication on a per-request basis. """
    if 'Authorization' in request.headers:
        authorization = request.headers.get('Authorization')
        authorization = authorization.split(' ', 1)[-1]
        login, password = authorization.decode('base64').split(':', 1)
        try:
            logic.user.login({'login': login, 'password': password})
        except Invalid:
            raise Unauthorized('Invalid username or password.')

@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(500)
def handle_exceptions(exc):
    """ Re-format exceptions to JSON if accept requires that. """
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
    return Response(repr(exc.unpack_errors()), status=400, 
                    mimetype='text/plain')


if __name__ == "__main__":
    app.run()

