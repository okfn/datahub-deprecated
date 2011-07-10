from datadeck.core import db
from datadeck.exc import NotFound
from datadeck.model import Account

def get(name):
    """ Get will try to find an account and return None if no account
    found. Use `find` for an exception-generating variant. """
    return Account.query.filter(Account.name==name).first()

def find(name):
    """ Find an account or yield a `NotFound` exception. """
    account = get(name)
    if account is None:
        raise NotFound('No such account: %s / %s' % name)
    return account

