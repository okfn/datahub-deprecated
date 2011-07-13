from flaskext.script import Manager
from flaskext.celery import install_commands as install_celery_commands

from datahub.core import app
from datahub.model import db

manager = Manager(app)
install_celery_commands(manager)


@manager.command
def createdb():
    """ Create the SQLAlchemy database. """
    db.create_all()
    resetsearch()


@manager.command
def resetsearch():
    """ Reset the elatic search index (without rebuilding). """
    from datahub.logic.search import index_name, connection
    conn = connection()
    try:
        conn.delete_index(index_name())
    except: pass
    conn.create_index(index_name())

@manager.command
def rebuildsearch():
    """ Re-build the search index for common entities. """
    resetsearch()
    from datahub.logic.account import rebuild
    rebuild()
    from datahub.logic.node import rebuild
    rebuild()



if __name__ == '__main__':
    manager.run()

