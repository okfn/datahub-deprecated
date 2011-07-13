from flask import request, render_template, redirect
from flask import url_for, flash
from formencode import Invalid, htmlfill

from datahub.core import app, login_manager, current_user
from datahub import logic
from datahub.util import request_content, jsonify

from datahub.views.resource_api import api as resource_api
from datahub.views.account_api import api as account_api

app.register_blueprint(resource_api, url_prefix='/api/v1/resource')
app.register_blueprint(account_api, url_prefix='/api/v1/account')

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
