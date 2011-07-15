from datahub.core import current_user

from datahub.auth.util import logged_in

def create(account):
    return logged_in() and account == current_user

def read(node):
    return True

def update(node):
    return logged_in() and node.owner == current_user

def delete(node):
    return update(node)
