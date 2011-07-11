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
                'full_name': self.full_name}

class User(Account):
    __mapper_args__ = {'polymorphic_identity': 'user'}

    def __init__(self, name, full_name, email):
        self.name = name
        self.full_name = full_name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.name


class Node(db.Model):
    __tablename__ = 'node'
    discriminator = db.Column('type', db.Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}
    __table_args__ = (
        db.Index('user_namespace', 'owner_id', 'name', unique=True),
        )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(1000))
    summary = db.Column(db.UnicodeText)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    owner = db.relationship(Account,
                            backref=db.backref('nodes', lazy='dynamic'))

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'owner': self.owner.name}

class Resource(Node):
    __mapper_args__ = {'polymorphic_identity': 'resource'}
    url = db.Column(db.Unicode(255))

    def __init__(self, owner, name, url, summary):
        self.owner = owner
        self.name = name
        self.url = url
        self.summary = summary

    def __repr__(self):
        return '<Resource %r>' % self.name


