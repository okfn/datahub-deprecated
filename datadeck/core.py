from flask import Flask
from pymongo import Connection

from datadeck import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('DATADECK_SETTINGS', silent=True)

conn = Connection(app.config['MONGO_HOST'])
db = conn[app.config['MONGO_DB']]

