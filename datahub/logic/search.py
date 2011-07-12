from datahub.core import app
from pyes import ES

def index_name():
    return app.config.get('ELASTIC_SEARCH_INDEX', 'datahub')

def connection():
    return ES(app.config['ELASTIC_SEARCH_URL'])

