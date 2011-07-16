from flask import request, render_template, redirect
from flask import url_for, flash, get_template_attribute
from werkzeug.contrib.atom import AtomFeed
from formencode import Invalid, htmlfill

from datahub.core import app, login_manager, current_user
from datahub.model import Resource, Dataset
from datahub.auth import require
from datahub import logic
from datahub.pager import Pager
from datahub.util import request_content

from datahub.views.resource_api import api as resource_api
from datahub.views.dataset_api import api as dataset_api
from datahub.views.account_api import api as account_api
from datahub.views.event_api import event_api, stream_api

app.register_blueprint(resource_api, url_prefix='/api/v1/resource')
app.register_blueprint(dataset_api, url_prefix='/api/v1/dataset')
app.register_blueprint(account_api, url_prefix='/api/v1/account')
app.register_blueprint(event_api, url_prefix='/api/v1/event')
app.register_blueprint(stream_api, url_prefix='/api/v1/stream')

@app.route('/<owner>/<node>')
def node(owner, node):
    node = logic.node.find(owner, node)
    if isinstance(node, Dataset):
        return render_template('dataset/view.html',
                    dataset=node)
    elif isinstance(node, Resource):
        return render_template('resource/view.html',
                    resource=node)

@app.route('/<owner>/<node>.atom')
def node_feed(owner, node):
    resource = logic.resource.find(owner, node)
    events = logic.event.latest_by_entity(resource)
    events.limit(40)
    entries = map(logic.event.event_to_entry, events)
    feed = AtomFeed(title="%s / %s" % (owner, node),
                    id='urn:datahub:%s/%s' % (owner, node),
                    url=url_for('node', owner=owner,
                        node=node),
                    subtitle=resource.summary,
                    entries=entries)
    return feed.get_response()

@app.route('/resource', methods=['POST'])
def resource_create():
    """ Create a new resource for the given user. """
    require.logged_in()
    owner = current_user.name
    data = request_content(request)
    try:
        resource = logic.resource.create(owner, data)
        if 'dataset' in data:
            # if we were simultaneously attaching a 
            # dataset, return there instead.
            flash('Created %s / %s' % (resource.owner.name, resource.name), 
                  'success')
            return redirect(url_for('node', 
                owner=data['dataset']['owner'], 
                node=data['dataset']['name']))
        return redirect(url_for('node', owner=owner, 
                                node=resource.name))
    except Invalid, inv:
        page = resource_create_form()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

def resource_create_form():
    return render_template('resource/create.html')

@app.route('/dataset', methods=['POST'])
def dataset_create():
    """ Create a new dataset for the given user. """
    require.logged_in()
    owner = current_user.name
    data = request_content(request)
    try:
        dataset = logic.dataset.create(owner, data)
        if 'resource' in data:
            # if we were simultaneously attaching a 
            # resource, return there instead.
            flash('Created %s / %s' % (dataset.owner.name, dataset.name), 
                  'success')
            return redirect(url_for('node', 
                owner=data['resource']['owner'], 
                node=data['resource']['name']))
        return redirect(url_for('node', owner=owner, 
                                node=dataset.name))
    except Invalid, inv:
        page = dataset_create_form()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

def dataset_create_form():
    return render_template('dataset/create.html')

@app.route('/create.modal')
def create_modal():
    require.logged_in()
    modal = get_template_attribute('parts.html', 'create_modal')
    return modal()

def dashboard():
    require.logged_in()
    resources = logic.resource.list_by_owner(current_user.name)
    datasets = logic.dataset.list_by_owner(current_user.name)
    return render_template('account/dashboard.html',
                account=account, resources=resources,
                datasets=datasets)

@app.route('/<account>.atom')
def account_feed(account):
    account = logic.account.find(account)
    events = logic.event.latest_by_entity(account)
    events.limit(40)
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
    events = Pager(events, 'account', request.args, limit=50,
                   account=account.name)
    return render_template('account/home.html',
                account=account, events=events)

@app.route('/register', methods=['GET'])
def register():
    require.account.create()
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
    require.account.update(current_user)
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

@app.route('/login.modal', methods=['GET'])
def login_modal():
    modal = get_template_attribute('account/parts.html', 'login_modal')
    return modal()

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
    require.logged_in()
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
