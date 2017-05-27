from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class Tag(Base):
    __tablename__='tag'
    id = Column(Integer, primary_key=True)
    name= Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'tag',
        'polymorphic_on': name
    }

    def __repr__(self):
        return "<Tag (id= {} name = {})>".format(self.id,self.name)


class MovieTag(Tag):
    __tablename__='movietag'
    id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    movietag_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'movietag',
    }

class BookTag(Tag):
    __tablename__='booktag'
    id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    booktag_name=Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'booktag',
    }
