from flask import request, render_template, redirect
from flask import url_for, flash
from formencode import Invalid, htmlfill

from datahub.core import app, login_manager, current_user
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

@app.route('/<owner>/<node>')
def node(owner, node):
    # FIXME: query for node, not resource
    resource = logic.resource.find(owner, node)
    return render_template('resource/view.html',
                resource=resource)

@app.route('/<owner>', methods=['POST'])
def node_create(owner):
    """ Create a new node for the given user. """
    # FIXME: handle different kinds of nodes.
    data = request_content(request)
    try:
        resource = logic.resource.create(owner, data)
        return redirect(url_for('node', owner=owner, 
                                node=resource.name))
    except Invalid, inv:
        page = dashboard()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

def dashboard():
    return render_template('account/dashboard.html',
                account=account)

@app.route('/<account>')
def account(account):
    account = logic.account.find(account)
    return render_template('account/home.html',
                account=account)

@app.route('/register', methods=['GET'])
def register():
    return render_template('account/register.html')

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

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('account/profile.html',
                           user=current_user)

@app.route('/profile', methods=['POST'])
def profile_save():
    data = request_content(request)
    try:
        logic.user.update(current_user, data)
        flash('Your profile has been updated.', 'success')
        return profile()
    except Invalid, inv:
        page = profile()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

@app.route('/login', methods=['GET'])
def login():
    return render_template('account/login.html')
login_manager.login_view = "login"

@app.route('/login', methods=['POST'])
def login_save():
    data = request_content(request)
    try:
        logic.user.login(data)
        flash('Welcome back.', 'success')
        return redirect(url_for('home'))
    except Invalid, inv:
        page = login()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

@app.route("/logout")
def logout():
    logic.user.logout()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    if not current_user.is_anonymous():
        return dashboard()
    # FIXME: Figure out what to put here
    from datahub.model import Account
    accounts = Account.query.all()
    return render_template('home.html', accounts=accounts)
