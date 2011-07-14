from datahub.core import db
from datahub.exc import NotFound
from datahub.model import Resource, Account
from datahub.model.event import ResourceCreatedEvent
from datahub.model.event import ResourceUpdatedEvent
from datahub.model.event import ResourceDeletedEvent

from datahub.logic import account
from datahub.logic import event
from datahub.logic.search import index_add, index_delete
from datahub.logic.validation import URL
from datahub.logic.node import NodeSchema, NodeSchemaState
from datahub.logic.node import get as get_node, find as find_node

class ResourceSchema(NodeSchema):
    allow_extra_fields = True
    url = URL(not_empty=True)

def list_by_owner(owner_name):
    """ Query for all resources owned by a particular account. """
    # TODO: move to search
    owner = account.find(owner_name)
    return Resource.query.join(Resource.owner).filter(Account.name==owner.name)

def get(owner_name, resource_name):
    """ Get will try to find a resource and return None if no resource is
    found. Use `find` for an exception-generating variant. """
    resource = get_node(owner_name, resource_name)
    return resource if isinstance(resource, Resource) else None

def find(owner_name, resource_name):
    """ Find a resource or yield a `NotFound` exception. """
    resource = find_node(owner_name, resource_name)
    if not isinstance(resource, Resource):
        raise NotFound('Not a resource: %s / %s' % (owner_name, 
                       resource_name))
    return resource

def create(owner_name, data):
    owner = account.find(owner_name)

    state = NodeSchemaState(owner_name, None)
    data = ResourceSchema().to_python(data, state=state)

    resource = Resource(owner, data['name'], data['url'],
                        data['summary'])
    db.session.add(resource)
    db.session.flush()
    index_add(resource)

    # FIXME: use current_user, not owner.
    event_ = ResourceCreatedEvent(owner, resource)
    event.emit(event_, [resource])

    db.session.commit()
    return resource

def update(owner_name, resource_name, data):
    resource = find(owner_name, resource_name)

    # tell availablename about our current name:
    state = NodeSchemaState(owner_name, resource_name)
    data = ResourceSchema().to_python(data, state=state)

    resource.name = data['name']
    resource.url = data['url']
    resource.summary = data['summary']
    index_add(resource)

    # FIXME: use current_user, not owner.
    event_ = ResourceUpdatedEvent(resource.owner, resource)
    event.emit(event_, [resource])

    db.session.commit()

    return resource

def delete(owner_name, resource_name):
    resource = find(owner_name, resource_name)

    # FIXME: use current_user, not owner.
    event_ = ResourceDeletedEvent(resource.owner, resource)
    event.emit(event_, [resource])

    db.session.delete(resource)
    index_delete(resource)
    db.session.commit()


