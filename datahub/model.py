from datetime import datetime
from datadeck.core import db

class Account(db.Model):
    """ Account is generic base class for normal users and 
    organizational accounts. """
    __tablename__ = 'account'
    discriminator = db.Column('type', db.String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'name': self.name}

class User(Account):
    __mapper_args__ = {'polymorphic_identity': 'user'}

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name


class Entity(db.Model):
    __tablename__ = 'entity'
    discriminator = db.Column('type', db.String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}
    __table_args__ = (
        db.Index('user_namespace', 'owner_id', 'name', unique=True),
        )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    owner = db.relationship(Account,
                            backref=db.backref('entities', lazy='dynamic'))

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'owner': self.owner.name}

class Resource(Entity):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    def __init__(self, owner, name):
        self.owner = owner
        self.name = name

    def __repr__(self):
        return '<Resource %r>' % self.name


