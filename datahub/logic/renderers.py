#import cgi
from flask import url_for

from datahub.model.event import ResourceCreatedEvent

class EventRenderer(object): 
    html_template = ''
    plain_template = ''

    def __init__(self, event):
        self.event = event

    def params(self):
        return self.event.data

    def __html__(self):
        return self.html_template % self.params()

    def __unicode__(self):
        return self.plain_template % self.params()

class ResourceCreatedEventRenderer(EventRenderer):
    html_template = '''has <verb>created</verb> 
        <a href='%(url)s'>%(owner)s/%(resource)s</a>'''

    def params(self):
        data = self.event.data.copy()
        data['url'] = url_for('node', owner=data['owner'], 
                              node=data['resource'])
        return data

RENDERERS = {
    ResourceCreatedEvent: ResourceCreatedEventRenderer
    }

