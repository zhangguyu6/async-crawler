from .base import Base
from sqlalchemy import Column, Integer, String, Float


class Evaluation(Base):
    __tablename__ = 'evaluation'
    id = Column(Integer, primary_key=True)
    score = Column(Float)
    evalnums = Column(Integer)
    fivestar = Column(Float)
    fourstar = Column(Float)
    threestar = Column(Float)
    twostar = Column(Float)
    onestar = Column(Float)
