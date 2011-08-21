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
from datahub.views.account import blueprint as account
from datahub.views.event_api import event_api, stream_api

app.register_blueprint(resource_api, url_prefix='/api/v1/resource')
app.register_blueprint(dataset_api, url_prefix='/api/v1/dataset')
app.register_blueprint(account_api, url_prefix='/api/v1/account')
app.register_blueprint(event_api, url_prefix='/api/v1/event')
app.register_blueprint(stream_api, url_prefix='/api/v1/stream')
app.register_blueprint(account)

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

@app.route('/add_resources.modal')
def add_resources_modal():
    dataset = logic.dataset.find(request.args['owner'],
                                 request.args['name'])
    require.dataset.add_resource(dataset)
    resources = logic.resource.list_by_owner(current_user.name)
    modal = get_template_attribute('resource/parts.html', 
                                   'add_resources_modal')
    return modal(dataset, resources)

@app.route('/add_datasets.modal')
def add_datasets_modal():
    resource = logic.resource.find(request.args['owner'],
                                   request.args['name'])
    require.dataset.create(current_user)
    datasets = logic.dataset.list_by_owner(current_user.name)
    modal = get_template_attribute('dataset/parts.html', 
                                   'add_datasets_modal')
    return modal(resource, datasets)

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
                resources=resources,
                datasets=datasets)

@app.route('/search')
def search():

    return render_template('search.html')

@app.route('/')
def home():
    if not current_user.is_anonymous():
        return dashboard()
    # FIXME: Figure out what to put here
    from datahub.model import Account
    accounts = Account.query.all()
    return render_template('home.html', accounts=accounts)
