from datetime import datetime
from datahub.core import db

from datahub.model.account import Account

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
                'type': self.discriminator,
                'owner': self.owner.name}

class Resource(Node):
    __mapper_args__ = {'polymorphic_identity': 'resource'}
    url = db.Column(db.Unicode(255))

    def __init__(self, owner, name, url, summary):
        self.owner = owner
        self.name = name
        self.url = url
        self.summary = summary

    def to_dict(self):
        d = super(Resource, self).to_dict()
        d['url'] = self.url
        return d

    def __repr__(self):
        return '<Resource %r>' % self.name

