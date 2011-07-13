from flask import request, render_template, redirect
from flask import url_for, flash
from werkzeug.contrib.atom import AtomFeed
from formencode import Invalid, htmlfill

from datahub.core import app, login_manager, current_user
from datahub import logic
from datahub.util import request_content

from datahub.views.resource_api import api as resource_api
from datahub.views.account_api import api as account_api
from datahub.views.event_api import event_api, stream_api

app.register_blueprint(resource_api, url_prefix='/api/v1/resource')
app.register_blueprint(account_api, url_prefix='/api/v1/account')
app.register_blueprint(event_api, url_prefix='/api/v1/event')
app.register_blueprint(stream_api, url_prefix='/api/v1/stream')

@app.route('/<owner>/<node>')
def node(owner, node):
    # FIXME: query for node, not resource
    resource = logic.resource.find(owner, node)
    return render_template('resource/view.html',
                resource=resource)

@app.route('/<owner>/<node>.atom')
def node_feed(owner, node):
    resource = logic.resource.find(owner, node)
    events = logic.event.latest_by_entity(resource)
    entries = map(logic.event.event_to_entry, events)
    feed = AtomFeed(title="%s / %s" % (owner, node),
                    id='urn:datahub:%s/%s' % (owner, node),
                    url=url_for('node', owner=owner,
                        node=node),
                    subtitle=resource.summary,
                    entries=entries)
    return feed.get_response()

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

@app.route('/<account>.atom')
def account_feed(account):
    account = logic.account.find(account)
    events = logic.event.latest_by_entity(account)
    entries = map(logic.event.event_to_entry, events)
    feed = AtomFeed(title=account.name,
                    id='urn:datahub:%s' % account.name,
                    url=url_for('account', account=account.name),
                    subtitle=account.full_name,
                    entries=entries)
    return feed.get_response()

@app.route('/<account>')
def account(account):
    account = logic.account.find(account)
    events = logic.event.latest_by_entity(account)
    return render_template('account/home.html',
                account=account, events=events)



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
