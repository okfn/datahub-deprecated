
DEBUG = True
SECRET_KEY = 'no'

SITE_NAME = 'DataHub'
SITE_SENDER = 'support@datahub'

BROKER_TRANSPORT = "sqlakombu.transport.Transport"
CELERY_BACKEND = "database" 

SOLR_URL = 'http://127.0.0.1:8983/solr/datahub'

SQLALCHEMY_DATABASE_URI = 'sqlite:///datahub.db'
BROKER_HOST = SQLALCHEMY_DATABASE_URI
CELERY_RESULT_DBURI = SQLALCHEMY_DATABASE_URI
