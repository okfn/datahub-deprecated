from hashlib import sha1
from uuid import uuid4
import os

from flask import url_for
from flaskext.login import login_user, logout_user
from formencode import Schema, Invalid, validators

from datahub.core import db, login_manager, current_user
from datahub.exc import BadRequest
from datahub.auth import require
from datahub.model import User
from datahub.model.event import AccountCreatedEvent
from datahub.model.event import AccountUpdatedEvent

from datahub.logic import event
from datahub.logic.search import index_add
from datahub.logic.account import AccountSchema, AccountSchemaState
from datahub.logic.account import get as get_account, find, send_mail

ACTIVATION_TEMPLATE = '''Dear %(full_name)s,

Please click the activation link to finalize your registration:

    %(url)s

'''


class RegistrationSchema(AccountSchema):
    """ Extend the account schema for user registration. """
    email = validators.Email(not_empty=True)
    password = validators.String(min=4)
    password_confirm = validators.String()
    chained_validators = [validators.FieldsMatch(
            'password', 'password_confirm')]

class ProfileSchema(AccountSchema):
    """ Extend the account schema for user profile editing. """
    email = validators.Email(not_empty=True)
    password = validators.String(not_empty=False)
    password_confirm = validators.String(not_empty=False)
    chained_validators = [validators.FieldsMatch(
            'password', 'password_confirm')]

class LoginSchema(Schema):
    """ Simple schema to check login fields are present. """
    login = validators.String()
    password = validators.String()

def make_token():
    """ Generate a unique token. """
    return sha1(str(uuid4())).hexdigest()[:10]

def hash_password(password):
    """ Hash password on the fly. """
    if isinstance(password, unicode):
        password_8bit = password.encode('ascii', 'ignore')
    else:
        password_8bit = password

    salt = sha1(os.urandom(60))
    hash = sha1(password_8bit + salt.hexdigest())
    hashed_password = salt.hexdigest() + hash.hexdigest()

    if not isinstance(hashed_password, unicode):
        hashed_password = hashed_password.decode('utf-8')
    return hashed_password


def validate_password(user_password, password):
    """ Check the password against existing credentials. """
    if isinstance(password, unicode):
        password_8bit = password.encode('ascii', 'ignore')
    else:
        password_8bit = password
    hashed_pass = sha1(password_8bit + user_password[:40])
    return user_password[40:] == hashed_pass.hexdigest()

def get(user_name):
    user = get_account(user_name)
    if isinstance(user, User):
        return user

@login_manager.user_loader
def null_get(user_name):
    return get(user_name)

def register(data):
    require.account.create()
    state = AccountSchemaState(None)
    data = RegistrationSchema().to_python(data, state=state)

    user = User(data['name'], data['full_name'], data['email'],
                hash_password(data['password']))
    db.session.add(user)
    db.session.flush()
    index_add(user)

    event_ = AccountCreatedEvent(user)
    event.emit(event_)

    send_activation(user)

    db.session.commit()

    return user

def update(user, data):
    require.account.update(user)

    # TODO combine with account.update
    state = AccountSchemaState(user.name)
    data = ProfileSchema().to_python(data, state=state)

    user.name = data['name']
    user.full_name = data['full_name']
    user.email = data['email']
    if data['password']:
        user.password = hash_password(data['password'])

    db.session.add(user)
    index_add(user)

    event_ = AccountUpdatedEvent(current_user)
    event.emit(event_)

    db.session.commit()

    return user

def login(data):
    data = LoginSchema().to_python(data)
    user = get(data['login'])
    # TODO: get rid of raising these exceptions in here.
    if user is None:
        raise Invalid('Invalid user name', data['login'], None,
                      error_dict={'login': 'Invalid user name'})
    if not validate_password(user.password, data['password']):
        raise Invalid('Password is incorrect', data['password'], None,
                      error_dict={'password': 'Password is incorrect'})
    if not login_user(user):
        raise BadRequest('This account is not activated.')
    return user

def logout():
    logout_user()

def activate(account, args):
    account = find(account)
    if account.activation_code != args['token']:
        raise BadRequest('Invalid activation code!')
    account.activated = True
    db.session.commit()
    login_user(account)

def send_activation(account):
    account.activation_code = make_token()
    account.activated = False
    subject = 'Activate your account'
    body = ACTIVATION_TEMPLATE % {
            'full_name': account.full_name, 
            'url': url_for('activate', 
                account=account.name,
                token=account.activation_code,
                _external=True)
            }
    send_mail(account, subject, body)
