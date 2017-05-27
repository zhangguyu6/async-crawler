from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'person',
        'polymorphic_on': name
    }

    def __repr__(self):
        return "<Person(id={},name={})>".format(self.id, self.name)


class Dirctor(Person):
    __tablename__ = 'dirctor'
    id = Column(Integer, ForeignKey('person.id'), primary_key=True)
    dirctor_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'dirctor',
    }

class Scriptwriter(Person):
    __tablename__ = 'scriptwriter'
    id = Column(Integer, ForeignKey('person.id'), primary_key=True)
    scriptwriter_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'scriptwriter',
    }

class Actor(Person):
    __tablename__ = 'actor'
    id = Column(Integer, ForeignKey('person.id'), primary_key=True)
    actor_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'actor',
    }

class Author(Person):
    __tablename__ = 'author'
    id = Column(Integer, ForeignKey('person.id'), primary_key=True)
    author_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'author',
    }

class Publisher(Person):
    __tablename__ = 'publisher'
    id = Column(Integer, ForeignKey('person.id'), primary_key=True)
    publisher_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'publisher',
    }

