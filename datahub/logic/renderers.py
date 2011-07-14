#import cgi
from flask import url_for

from datahub.model.event import ResourceCreatedEvent
from datahub.model.event import ResourceUpdatedEvent
from datahub.model.event import ResourceDeletedEvent

from datahub.model.event import DatasetCreatedEvent
from datahub.model.event import DatasetUpdatedEvent
from datahub.model.event import DatasetAddResourceEvent
from datahub.model.event import DatasetRemoveResourceEvent
from datahub.model.event import DatasetDeletedEvent

from datahub.model.event import AccountCreatedEvent
from datahub.model.event import AccountUpdatedEvent

class EventRenderer(object): 
    html_template = ''
    plain_template = ''

    def __init__(self, event):
        self.event = event

    def params(self):
        return self.event.data

    def url(self):
        return url_for('home', _external=True)

    def __html__(self):
        return self.html_template % self.params()

    def __unicode__(self):
        return self.plain_template % self.params()

class AccountCreatedEventRenderer(EventRenderer):
    html_template = '''<verb>signed up</verb>'''

    def params(self):
        return self.event.data

    def url(self):
        return url_for('account', self.event.account.name, 
                _external=True)

class AccountUpdatedEventRenderer(EventRenderer):
    html_template = '''<verb>updated</verb> their
        <a href='%(url)s'>profile</a>'''

    def params(self):
        data = self.event.data.copy()
        data['url'] = url_for('account', account=self.event.account.name)
        return data

    def url(self):
        return url_for('account', self.event.account.name, 
                _external=True)

class ResourceCreatedEventRenderer(EventRenderer):
    html_template = '''<verb>created</verb> the resource
        <a href='%(url)s'>%(owner)s/%(resource)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['url'] = url_for('node', owner=data['owner'], 
                              node=data['resource'])
        return data

    def url(self):
        return url_for('node', account=self.event.data['owner'], 
                node=self.event.data['resource'], _external=True)

class ResourceUpdatedEventRenderer(EventRenderer):
    html_template = '''<verb>updated</verb> the resource
        <a href='%(url)s'>%(owner)s/%(resource)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['url'] = url_for('node', owner=data['owner'], 
                              node=data['resource'])
        return data

    def url(self):
        return url_for('node', account=self.event.data['owner'], 
                node=self.event.data['resource'], _external=True)

class ResourceDeletedEventRenderer(EventRenderer):
    html_template = '''<verb>deleted</verb> the resource
        %(owner)s/%(resource)s'''

    def params(self):
        return self.event.data

class DatasetCreatedEventRenderer(EventRenderer):
    html_template = '''<verb>created</verb> the dataset
        <a href='%(url)s'>%(owner)s/%(dataset)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['url'] = url_for('node', owner=data['owner'], 
                              node=data['dataset'])
        return data

    def url(self):
        return url_for('node', account=self.event.data['owner'], 
                node=self.event.data['dataset'], _external=True)

class DatasetUpdatedEventRenderer(EventRenderer):
    html_template = '''<verb>updated</verb> the dataset
        <a href='%(url)s'>%(owner)s/%(dataset)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['url'] = url_for('node', owner=data['owner'], 
                              node=data['dataset'])
        return data

    def url(self):
        return url_for('node', account=self.event.data['owner'], 
                node=self.event.data['dataset'], _external=True)

class DatasetAddResourceEventRenderer(EventRenderer):
    html_template = '''<verb>added</verb> the resource 
        <a href='%(resource_url)s'>%(resource_owner)s/%(resource_name)s</a>
        to the dataset
        <a href='%(dataset_url)s'>%(dataset_owner)s/%(dataset_name)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['resource_url'] = url_for('node', 
                              owner=data['resource_owner'], 
                              node=data['resource_name'])
        data['dataset_url'] = url_for('node', 
                              owner=data['dataset_owner'], 
                              node=data['dataset_name'])
        return data

    def url(self):
        return url_for('node', account=self.event.data['dataset_owner'], 
                node=self.event.data['dataset_name'], _external=True)

class DatasetRemoveResourceEventRenderer(EventRenderer):
    html_template = '''<verb>removed</verb> the resource 
        <a href='%(resource_url)s'>%(resource_owner)s/%(resource_name)s</a>
        from the dataset
        <a href='%(dataset_url)s'>%(dataset_owner)s/%(dataset_name)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['resource_url'] = url_for('node', 
                              owner=data['resource_owner'], 
                              node=data['resource_name'])
        data['dataset_url'] = url_for('node', 
                              owner=data['dataset_owner'], 
                              node=data['dataset_name'])
        return data

    def url(self):
        return url_for('node', account=self.event.data['dataset_owner'], 
                node=self.event.data['dataset_name'], _external=True)

class DatasetDeletedEventRenderer(EventRenderer):
    html_template = '''<verb>deleted</verb> the dataset
        %(owner)s/%(dataset)s'''

    def params(self):
        return self.event.data

RENDERERS = {
    ResourceCreatedEvent: ResourceCreatedEventRenderer,
    ResourceUpdatedEvent: ResourceUpdatedEventRenderer,
    ResourceDeletedEvent: ResourceDeletedEventRenderer,

    DatasetCreatedEvent: DatasetCreatedEventRenderer,
    DatasetUpdatedEvent: DatasetUpdatedEventRenderer,
    DatasetAddResourceEvent: DatasetAddResourceEventRenderer,
    DatasetRemoveResourceEvent: DatasetRemoveResourceEventRenderer,
    DatasetDeletedEvent: DatasetDeletedEventRenderer,

    AccountCreatedEvent: AccountCreatedEventRenderer,
    AccountUpdatedEvent: AccountUpdatedEventRenderer
    }

