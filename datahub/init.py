from datahub.core import app
from datahub.model import db

if __name__ == '__main__':
    app.test_request_context().push()
    db.create_all()


