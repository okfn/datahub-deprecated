from datetime import datetime

from solr import SolrConnection

from datahub.core import app
from datahub.util import datetime_add_tz

def connection():
    return SolrConnection(app.config['SOLR_URL'])

def to_key(entity):
    return '%s:%s' % (entity.__tablename__, entity.id)

def flatten_dict(d, prefix='meta', sep='_'):
    """ Flatten a dict to a list of values with each key 
    joined to `prefix` by `sep`. """
    flat = {}
    for k, v in d.items():
        key = "".join([prefix, sep, k])
        if isinstance(v, dict):
            flat.update(flatten_dict(v, prefix=key, sep=sep))
        else:
            flat[key] = v
    return flat

def index_add(entity):
    """ Add an SQLAlchemy-controlled entity to the elastic search index
    """
    if not hasattr(entity, '__tablename__'):
        raise TypeError('Can only index entities with a __tablename__')
    if not hasattr(entity, 'to_dict'):
        raise TypeError('Can only index entities with a to_dict')
    conn = connection()
    data = entity.to_dict()
    data['_key'] = to_key(entity)
    data['doc_type'] = entity.__tablename__
    flat_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            flat_data.update(flatten_dict(v, prefix=k))
        else:
            flat_data[k] = v
    data = flat_data
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = datetime_add_tz(v)
    try:
        conn.add_many([data])
        conn.commit()
    finally: 
        conn.close()

def index_delete(entity):
    """ Deleta an SQLAlchemy-controlled entity from the elastic search 
    index, catching any NotFoundExceptions. """
    if not hasattr(entity, '__tablename__'):
        raise TypeError('Can only index entities with a __tablename__')
    conn = connection()
    try:
        conn.delete_query('+_key:%s' % to_key(entity))
        conn.commit()
    finally: 
        conn.close()

def reset_index():
    """ Delete all entries from the index. """
    conn = connection()
    try:
        conn.delete_query('*:*')
        conn.commit()
    finally: 
        conn.close()

