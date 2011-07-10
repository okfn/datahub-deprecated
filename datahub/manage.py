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



if __name__ == '__main__':
    manager.run()

