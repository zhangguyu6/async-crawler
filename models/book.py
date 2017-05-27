from sqlalchemy import Table, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base
from .tag import BookTag
from .person import Author, Publisher
# from .person import


ass_book_tag = Table('book_tag', Base.metadata,
                     Column('book_id', Integer, ForeignKey('book.id'),
                            Column('booktag_id', Integer, ForeignKey('booktag.id'))))


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(30))
    author = Column(Integer, ForeignKey('author.id'))
    publisher = Column(Integer, ForeignKey('publisher.id'))
    subtitle = Column(String(30))
    pagenames = Column(Integer)
    price = Column(Integer)
    belongto = Column(String(30))
    isbn = Column(Integer)
    content_intr = Column(Text)
    author_intr = Column(Text)
    tag = relationship('MovieTag', secondary=ass_book_tag,
                       backref='books')

    def __repr__(self):
        return "<Book (id = {}, title = {})> ".format(self.id, self.name)
