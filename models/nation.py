from .base import Base
from sqlalchemy import Column, Integer, String


class Nation(Base):
    __tablename__ = 'nation'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))

    def __repr__(self):
        return "<Nation(id = {} ,name = {})>".format(self.id, self.name)
