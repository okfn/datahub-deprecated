from datahub.core import db
from datahub.exc import NotFound
from datahub.model import Account

def get(name):
    """ Get will try to find an account and return None if no account
    found. Use `find` for an exception-generating variant. """
    return Account.query.filter(Account.name==name).first()

def find(name):
    """ Find an account or yield a `NotFound` exception. """
    account = get(name)
    if account is None:
        raise NotFound('No such account: %s' % name)
    return account

def update(account_name, data):
    """ Update an account's data. """
    account = find(account_name)
    
    account.name = data['name']
    db.session.commit()
    return account

