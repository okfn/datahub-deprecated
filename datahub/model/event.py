from datetime import datetime
from datahub.core import db

from datahub.model.account import Account
from datahub.model.types import JSONType

class Event(db.Model):
    __tablename__ = 'event'
    discriminator = db.Column('type', db.Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.UnicodeText)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship(Account,
                           backref=db.backref('events', lazy='dynamic'))

    data = db.Column(JSONType, default=dict)

    def __init__(self, account, message):
        self.account = account
        self.message = message

    def to_dict(self):
        return {'id': self.id,
                'message': self.message,
                'time': self.time,
                'data': self.data,
                'type': self.discriminator,
                'account': self.account.name}


class EventStreamEntry(db.Model):
    """ An event stream entry connects events back to the objects that 
    they pertain to. """

    __tablename__ = 'event_stream_entry'
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.Unicode)
    entity_id = db.Column(db.Unicode)

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship(Event, backref=db.backref('stream_entries'))

    def __init__(self, entity_type, entity_id, event):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.event = event

    def to_dict(self):
        return {'entity_type': self.entity_type,
                'entity_id': self.entity_id,
                'type': self.discriminator,
                'event': self.event.to_dict()}


##### Event types library

class AccountCreatedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'account_created'}

    def __init__(self, account):
        super(AccountCreatedEvent, self).__init__(account, '')

class AccountUpdatedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'account_updated'}

    def __init__(self, account):
        super(AccountUpdatedEvent, self).__init__(account, '')

class ResourceCreatedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'resource_created'}

    def __init__(self, account, resource):
        super(ResourceCreatedEvent, self).__init__(account, 
            resource.summary)
        self.data = {'resource': resource.name, 
                     'owner': resource.owner.name}

class ResourceUpdatedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'resource_updated'}

    def __init__(self, account, resource):
        super(ResourceUpdatedEvent, self).__init__(account, 
            resource.summary)
        self.data = {'resource': resource.name, 
                     'owner': resource.owner.name}

class ResourceDeletedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'resource_deleted'}

    def __init__(self, account, resource):
        super(ResourceDeletedEvent, self).__init__(account, 
            resource.summary)
        self.data = {'resource': resource.name, 
                     'owner': resource.owner.name}

class DatasetCreatedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'dataset_created'}

    def __init__(self, account, dataset):
        super(DatasetCreatedEvent, self).__init__(account, 
            dataset.summary)
        self.data = {'dataset': dataset.name, 
                     'owner': dataset.owner.name}

class DatasetUpdatedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'dataset_updated'}

    def __init__(self, account, dataset):
        super(DatasetUpdatedEvent, self).__init__(account, 
            dataset.summary)
        self.data = {'dataset': dataset.name, 
                     'owner': dataset.owner.name}

class DatasetAddResourceEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'dataset_add_resource'}

    def __init__(self, account, dataset, resource):
        super(DatasetAddResourceEvent, self).__init__(account, 
            resource.summary)
        self.data = {'dataset_name': dataset.name, 
                     'dataset_owner': dataset.owner.name,
                     'resource_name': resource.name,
                     'resource_owner': resource.owner.name}

class DatasetRemoveResourceEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'dataset_remove_resource'}

    def __init__(self, account, dataset, resource):
        super(DatasetRemoveResourceEvent, self).__init__(account, 
            resource.summary)
        self.data = {'dataset_name': dataset.name, 
                     'dataset_owner': dataset.owner.name,
                     'resource_name': resource.name,
                     'resource_owner': resource.owner.name}

class DatasetDeletedEvent(Event):
    __mapper_args__ = {'polymorphic_identity': 'dataset_deleted'}

    def __init__(self, account, dataset):
        super(DatasetDeletedEvent, self).__init__(account, 
            dataset.summary)
        self.data = {'dataset': dataset.name, 
                     'owner': dataset.owner.name}

