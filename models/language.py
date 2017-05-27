from .base import Base
from sqlalchemy import Column, Integer, String

class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))

    def __repr__(self):
        return "<Language(id = {} ,name = {})>".format(self.id, self.name)