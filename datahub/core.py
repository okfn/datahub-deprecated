# shut up useless SA warning:
import warnings; warnings.filterwarnings('ignore', 'Unicode type received non-unicode bind param value.')


from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

from datahub import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('DATAHUB_SETTINGS', silent=True)

db = SQLAlchemy(app)



