from datahub.core import app
from pyes import ES
from pyes.exceptions import NotFoundException

def index_name():
    return app.config.get('ELASTIC_SEARCH_INDEX', 'datahub')

def connection():
    return ES(app.config['ELASTIC_SEARCH_URL'])

def index_add(entity):
    """ Add an SQLAlchemy-controlled entity to the elastic search index
    """
    if not hasattr(entity, '__tablename__'):
        raise TypeError('Can only index entities with a __tablename__')
    if not hasattr(entity, 'to_dict'):
        raise TypeError('Can only index entities with a to_dict')
    #conn = connection()
    #conn.index(entity.to_dict(), index_name(), 
    #           entity.__tablename__, entity.id)

def index_delete(entity):
    """ Deleta an SQLAlchemy-controlled entity from the elastic search 
    index, catching any NotFoundExceptions. """
    if not hasattr(entity, '__tablename__'):
        raise TypeError('Can only index entities with a __tablename__')
    #conn = connection()
    #try:
    #    conn.delete(index_name(), entity.__tablename__, entity.id)
    #except NotFoundException:
    #    pass


