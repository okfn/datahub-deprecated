from datahub.core import db
from datahub.exc import NotFound
from datahub.model import Dataset, Account
from datahub.model.event import DatasetCreatedEvent
from datahub.model.event import DatasetUpdatedEvent
from datahub.model.event import DatasetDeletedEvent

from datahub.logic import account
from datahub.logic import event
from datahub.logic.search import index_add, index_delete
from datahub.logic.node import NodeSchema, NodeSchemaState
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
    return dataset

def create(owner_name, data):
    owner = account.find(owner_name)

    state = NodeSchemaState(owner_name, None)
    data = DatasetSchema().to_python(data, state=state)

    dataset = Dataset(owner, data['name'], data['summary'])
    db.session.add(dataset)
    db.session.flush()
    index_add(dataset)

    # FIXME: use current_user, not owner.
    event_ = DatasetCreatedEvent(owner, dataset)
    event.emit(event_, [dataset])

    db.session.commit()
    return dataset

def update(owner_name, dataset_name, data):
    dataset = find(owner_name, dataset_name)

    # tell availablename about our current name:
    state = NodeSchemaState(owner_name, dataset_name)
    data = DatasetSchema().to_python(data, state=state)

    dataset.name = data['name']
    dataset.summary = data['summary']
    index_add(dataset)

    # FIXME: use current_user, not owner.
    event_ = DatasetUpdatedEvent(dataset.owner, dataset)
    event.emit(event_, [dataset])

    db.session.commit()

    return dataset

def delete(owner_name, dataset_name):
    dataset = find(owner_name, dataset_name)

    # FIXME: use current_user, not owner.
    event_ = DatasetDeletedEvent(dataset.owner, dataset)
    event.emit(event_, [dataset])

    db.session.delete(dataset)
    index_delete(dataset)
    db.session.commit()


