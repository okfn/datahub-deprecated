from hashlib import sha1
import os

from formencode import Schema, Invalid, validators

from datahub.core import db
from datahub.model import User
from datahub.logic.account import AccountSchema, AccountSchemaState, get


class RegistrationSchema(AccountSchema):
    """ Extend the account schema for user registration. """
    password = validators.String(min=4)
    password_confirm = validators.String()
    chained_validators = [validators.FieldsMatch(
            'password', 'password_confirm')]

class LoginSchema(Schema):
    """ Simple schema to check login fields are present. """
    login = validators.String()
    password = validators.String()

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


def register(data):
    # tell availablename about our current name:
    state = AccountSchemaState(None)
    data = RegistrationSchema().to_python(data, state=state)

    user = User(data['name'], data['full_name'], data['email'],
                hash_password(data['password']))
    db.session.add(user)
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
    return user

