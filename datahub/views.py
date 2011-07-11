from flask import request, render_template, redirect, url_for
from formencode import Invalid, htmlfill

from datahub.core import app, login_manager
from datahub import logic
from datahub.exc import Gone
from datahub.util import request_content, jsonify

@app.route('/api/v1/resource/<owner>', methods=['GET'])
def resource_index(owner):
    """ List all the resources of a particular user. """
    result = logic.resource.list_by_owner(owner)
    return jsonify(list(result))

@app.route('/api/v1/resource/<owner>', methods=['POST'])
def resource_create(owner):
    """ Create a new resource for the given user. """
    data = request_content(request)
    resource = logic.resource.create(owner, data)
    return redirect(url_for('resource_get', owner=owner, 
                            resource=resource.name))

@app.route('/api/v1/resource/<owner>/<resource>', methods=['GET'])
def resource_get(owner, resource):
    """ Get a JSON representation of the resource. """
    resource = logic.resource.find(owner, resource)
    return jsonify(resource)

@app.route('/api/v1/resource/<owner>/<resource>', methods=['PUT'])
def resource_update(owner, resource):
    """ Update the data of the resource. """
    data = request_content(request)
    resource = logic.resource.update(owner, resource, data)
    return jsonify(resource)

@app.route('/api/v1/resource/<owner>/<resource>', methods=['DELETE'])
def resource_delete(owner, resource):
    """ Delete the resource. """
    logic.resource.delete(owner, resource)
    raise Gone('Successfully deleted: %s / %s' % (owner, resource))

@app.route('/api/v1/profile/<account>', methods=['GET'])
def profile_get(account):
    """ Get a JSON representation of the account. """
    account = logic.account.find(account)
    return jsonify(account)

@app.route('/api/v1/profile/<account>', methods=['PUT'])
def profile_update(account):
    """ Update the data of the account profile. """
    data = request_content(request)
    account = logic.account.update(account, data)
    return jsonify(account)

@app.route('/register', methods=['GET'])
def register():
    return render_template('account/register.tmpl')

@app.route('/register', methods=['POST'])
def register_save():
    data = request_content(request)
    try:
        logic.user.register(data)
        return redirect(url_for('home'))
    except Invalid, inv:
        page = register()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())


@app.route('/login', methods=['GET'])
def login():
    return render_template('account/login.tmpl')
login_manager.login_view = "login"

@app.route('/login', methods=['POST'])
def login_save():
    data = request_content(request)
    try:
        logic.user.login(data)
        return redirect(url_for('home'))
    except Invalid, inv:
        page = login()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

@app.route("/logout")
def logout():
    logic.user.logout()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.tmpl')
