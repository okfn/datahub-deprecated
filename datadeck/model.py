from datadeck.core import db

class Account(db.Model):
    """ Account is generic base class for normal users and 
    organizational accounts. """
    __tablename__ = 'account'
    discriminator = db.Column('type', db.String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)


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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))

    owner_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    owner = db.relationship('Account',
        backref=db.backref('entities', lazy='dynamic'))



class Resource(Entity):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Resource %r>' % self.name


