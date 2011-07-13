from datetime import datetime
from datahub.core import db

class Account(db.Model):
    """ Account is generic base class for normal users and 
    organizational accounts. """
    __tablename__ = 'account'
    discriminator = db.Column('type', db.Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255), unique=True)
    full_name = db.Column(db.Unicode(2000))
    email = db.Column(db.Unicode(2000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'name': self.name,
                'type': self.discriminator,
                'full_name': self.full_name}

class User(Account):
    __mapper_args__ = {'polymorphic_identity': 'user'}
    password = db.Column(db.Unicode(2000))

    def __init__(self, name, full_name, email, password):
        self.name = name
        self.full_name = full_name
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return self.name

    def __repr__(self):
        return '<User %r>' % self.name

