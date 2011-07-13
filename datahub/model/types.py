from json import dumps, loads
from sqlalchemy.types import Text, MutableType, TypeDecorator

class JSONType(MutableType, TypeDecorator):
    impl = Text

    def __init__(self):
        super(JSONType, self).__init__()

    def process_bind_param(self, value, dialect):
        return dumps(value)

    def process_result_value(self, value, dialiect):
        return loads(value)

    def copy_value(self, value):
        return loads(dumps(value))

