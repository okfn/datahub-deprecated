from datadeck.core import db

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Resource %r>' % self.name


