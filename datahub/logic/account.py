from formencode import Schema, All, validators
from flaskext.mail import Message

from datahub.core import db, mail, app
from datahub.exc import NotFound
from datahub.auth import require
from datahub.model import Account, Resource, Dataset
from datahub.model.event import AccountUpdatedEvent

from datahub.logic import event
from datahub.logic.search import index_add
from datahub.logic.validation import Name, AvailableAccountName

class AccountSchemaState():
    """ Used to let the AvailableAccountName validator know that the 
    current name is taken by the account itself. """

    def __init__(self, current_name):
        self.current_name = current_name

class AccountSchema(Schema):
    allow_extra_fields = True
    name = All(Name(not_empty=True), AvailableAccountName())
    full_name = validators.String(min=1, max=2000)
    email = validators.Email(if_empty=None, if_missing=None)

def get(name):
    """ Get will try to find an account and return None if no account
    found. Use `find` for an exception-generating variant. """
    return Account.query.filter(Account.name==name).first()

def find(name):
    """ Find an account or yield a `NotFound` exception. """
    account = get(name)
    if account is None:
        raise NotFound('No such account: %s' % name)
    require.account.read(account)
    return account

def update(account_name, data):
    """ Update an account's data. """
    account = find(account_name)
    require.account.update(account)

    # tell availablename about our current name:
    state = AccountSchemaState(account_name)
    data = AccountSchema().to_python(data, state=state)

    account.name = data['name']
    account.full_name = data['full_name']
    if 'email' in data and data['email'] is not None:
        account.email = data['email']
    index_add(account)

    # FIXME: use current_user, not owner.
    event_ = AccountUpdatedEvent(account)
    event.emit(event_)

    db.session.commit()
    return account

def resources(account):
    return db.session.query(Resource).filter_by(owner=account)

def datasets(account):
    return db.session.query(Dataset).filter_by(owner=account)

def rebuild():
    """ Rebuild the search index for all accounts. """
    for account in Account.query:
        index_add(account)

def send_mail(account, subject, body):
    message = Message(subject, 
            recipients=[account.email],
            body=body,
            sender = (app.config['SITE_NAME'], 
                      app.config['SITE_SENDER']))
    mail.send(message)
