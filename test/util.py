from datahub import core
from datahub import web

def make_test_app():
    web.app.config['TESTING'] = True
    web.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    web.app.config['ELASTIC_SEARCH_INDEX'] = 'datahub_test'
    core.db.create_all()
    return web.app.test_client()

def tear_down_test_app():
    core.db.drop_all()

