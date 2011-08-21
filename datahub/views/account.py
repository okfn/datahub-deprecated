from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect
from flask import get_template_attribute
from werkzeug.contrib.atom import AtomFeed
from formencode import Invalid, htmlfill

from datahub.core import login_manager, current_user
from datahub.auth import require
from datahub.pager import Pager
from datahub import logic
from datahub.util import request_content

blueprint = Blueprint('account', __name__)

@blueprint.route('/<account>.atom')
def feed(account):
    account = logic.account.find(account)
    events = logic.event.latest_by_entity(account)
    events.limit(40)
    entries = map(logic.event.event_to_entry, events)
    feed = AtomFeed(title=account.name,
                    id='urn:datahub:%s' % account.name,
                    url=url_for('account.get', account=account.name),
                    subtitle=account.full_name,
                    entries=entries)
    return feed.get_response()

@blueprint.route('/<account>')
def get(account):
    account = logic.account.find(account)
    events = logic.event.latest_by_entity(account)
    events = Pager(events, 'account.get', request.args, limit=10,
                   account=account.name)
    resources = logic.account.resources(account)
    datasets = logic.account.datasets(account)
    return render_template('account/home.html',
                resources=resources, datasets=datasets,
                account=account, events=events)

@blueprint.route('/activate/<account>')
def activate(account):
    logic.user.activate(account, request.args)
    flash('Your account has been activated.', 'success')
    return redirect(url_for('home'))

@blueprint.route('/register', methods=['GET'])
def register():
    require.account.create()
    return render_template('account/register.html')

@blueprint.route('/register', methods=['POST'])
def register_save():
    data = request_content(request)
    try:
        logic.user.register(data)
        return redirect(url_for('home'))
    except Invalid, inv:
        page = register()
        return htmlfill.render(page, defaults=data, 
                errors=inv.unpack_errors())

@blueprint.route('/profile', methods=['GET'])
def profile():
    require.account.update(current_user)
    return render_template('account/profile.html',
                           user=current_user)

@blueprint.route('/profile', methods=['POST'])
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

@blueprint.route('/login.modal', methods=['GET'])
def login_modal():
    modal = get_template_attribute('account/parts.html', 
                'login_modal')
    return modal()

@blueprint.route('/login', methods=['GET'])
def login():
    return render_template('account/login.html')
login_manager.login_view = "login"

@blueprint.route('/login', methods=['POST'])
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

@blueprint.route("/logout")
def logout():
    require.logged_in()
    logic.user.logout()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))
