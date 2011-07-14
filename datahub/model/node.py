from datetime import datetime
from datahub.core import db

from datahub.model.account import Account

datasets_resources_table = db.Table('datasets_resources', db.metadata,
    db.Column('dataset_id', db.Integer, db.ForeignKey("node.id"), primary_key=True),
    db.Column('resource_id', db.Integer, db.ForeignKey("node.id"), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
)

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


class Dataset(Node):
    __mapper_args__ = {'polymorphic_identity': 'dataset'}

    def __init__(self, owner, name, summary):
        self.owner = owner
        self.name = name
        self.summary = summary

    def to_dict(self):
        d = super(Dataset, self).to_dict()
        return d

    def __repr__(self):
        return '<Dataset %r>' % self.name


Dataset.resources = db.relationship(Resource,
                    secondary=datasets_resources_table,
                    primaryjoin=Dataset.id==datasets_resources_table.c.dataset_id,
                    secondaryjoin=Resource.id==datasets_resources_table.c.resource_id,
                    backref=db.backref('datasets', lazy='dynamic'))

