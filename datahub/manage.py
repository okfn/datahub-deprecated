from flaskext.script import Manager
from flaskext.celery import install_commands as install_celery_commands

from datahub.core import app, db
from datahub.model import * 

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
    from datahub.logic.search import reset_index
    reset_index()

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

