from datahub.core import db, current_user
from datahub.exc import NotFound
from datahub.auth import require
from datahub.model import Dataset, Account
from datahub.model.event import DatasetCreatedEvent
from datahub.model.event import DatasetUpdatedEvent
from datahub.model.event import DatasetAddResourceEvent
from datahub.model.event import DatasetRemoveResourceEvent
from datahub.model.event import DatasetDeletedEvent

from datahub.logic import account, resource
from datahub.logic import event
from datahub.logic.search import index_add, index_delete
from datahub.logic.node import NodeSchema, NodeSchemaState, NodeReference
from datahub.logic.node import get as get_node, find as find_node

class DatasetSchema(NodeSchema):
    allow_extra_fields = True

def list_by_owner(owner_name):
    """ Query for all datasets owned by a particular account. """
    # TODO: move to search
    owner = account.find(owner_name)
    return Dataset.query.join(Dataset.owner).filter(Account.name==owner.name)

def get(owner_name, dataset_name):
    """ Get will try to find a dataset and return None if no dataset is
    found. Use `find` for an exception-generating variant. """
    dataset = get_node(owner_name, dataset_name)
    return dataset if isinstance(dataset, Dataset) else None

def find(owner_name, dataset_name):
    """ Find a dataset or yield a `NotFound` exception. """
    dataset = find_node(owner_name, dataset_name)
    if not isinstance(dataset, Dataset):
        raise NotFound('Not a dataset: %s / %s' % (owner_name, 
                       dataset_name))
    require.dataset.read(dataset)
    return dataset

def create(owner_name, data):
    owner = account.find(owner_name)
    require.dataset.create(owner)

    state = NodeSchemaState(owner_name, None)
    data = DatasetSchema().to_python(data, state=state)

    dataset = Dataset(owner, data['name'], data['summary'],
                      data['meta'])
    db.session.add(dataset)
    db.session.flush()
    index_add(dataset)

    event_ = DatasetCreatedEvent(current_user, dataset)
    event.emit(event_, [dataset])

    db.session.commit()
    return dataset

def update(owner_name, dataset_name, data):
    dataset = find(owner_name, dataset_name)
    require.dataset.update(dataset)

    # tell availablename about our current name:
    state = NodeSchemaState(owner_name, dataset_name)
    data = DatasetSchema().to_python(data, state=state)

    dataset.name = data['name']
    dataset.summary = data['summary']
    dataset.meta = data['meta']
    index_add(dataset)

    event_ = DatasetUpdatedEvent(current_user, dataset)
    event.emit(event_, [dataset])

    db.session.commit()
    return dataset

def list_resources(owner_name, dataset_name):
    dataset = find(owner_name, dataset_name)
    require.dataset.read(dataset)
    return dataset.resources

def add_resource(owner_name, dataset_name, data):
    dataset = find(owner_name, dataset_name)
    require.dataset.add_resource(dataset)

    data = NodeReference().to_python(data)

    res = resource.find(data['owner'], data['name'])
    if not res in dataset.resources:
        dataset.resources.append(res)

        event_ = DatasetAddResourceEvent(current_user, 
                        dataset, res)
        event.emit(event_, [dataset, res])
    db.session.commit()

def remove_resource(owner_name, dataset_name, resource_owner,
                    resource_name):
    dataset = find(owner_name, dataset_name)
    require.dataset.remove_resource(dataset)
    res = resource.find(resource_owner, resource_name)
    if res in dataset.resources:
        dataset.resources.remove(res)

        event_ = DatasetRemoveResourceEvent(dataset.owner, 
                        dataset, res)
        event.emit(event_, [dataset, res])
    db.session.commit()

def delete(owner_name, dataset_name):
    dataset = find(owner_name, dataset_name)
    require.dataset.delete(dataset)

    event_ = DatasetDeletedEvent(current_user, dataset)
    event.emit(event_, [dataset])

    db.session.delete(dataset)
    index_delete(dataset)
    db.session.commit()


