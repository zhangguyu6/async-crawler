from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, backref
import pymysql
# pymysql.install_as_MySQLdb()

from .base import Base, engine
from .tag import MovieTag
from .person import Actor, Dirctor, Scriptwriter
from .nation import Nation
from .language import Language
from .evaluation import Evaluation

Session = sessionmaker(bind=engine)

ass_movie_dirctor = Table('movie_dirctor', Base.metadata,
                          Column('movie_id', Integer, ForeignKey('movie.id')),
                          Column('dirctor_id', Integer,ForeignKey('dirctor.id')))

ass_movie_scriptwriter = Table('movie_scriptwriter', Base.metadata,
                               Column('movie_id', Integer,ForeignKey('movie.id')),
                               Column('scriptwriter_id', Integer,ForeignKey('scriptwriter.id')))

ass_movie_actor = Table('movie_actor', Base.metadata,
                        Column('movie_id', Integer, ForeignKey('movie.id')),
                        Column('actor_id', Integer, ForeignKey('actor.id')))

ass_movie_tag = Table('movie_tag', Base.metadata,
                      Column('movie_id', Integer, ForeignKey('movie.id')),
                      Column('movietag_id', Integer, ForeignKey('movietag.id')))

ass_movie_nation = Table('movie_nation', Base.metadata,
                         Column('movie_id', Integer, ForeignKey('movie.id')),
                         Column('nation_id', Integer, ForeignKey('nation.id')))

ass_movie_language = Table('movie_language', Base.metadata,
                           Column('movie_id', Integer, ForeignKey('movie.id')),
                           Column('language_id', Integer,
                                  ForeignKey('language.id')))


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    title = Column(String(50))

    dirctor = relationship('Dirctor', secondary=ass_movie_dirctor,
                           backref='movies')

    scriptwriter = relationship('Scriptwriter', secondary=ass_movie_scriptwriter,
                                backref='movies')

    actor = relationship('Actor', secondary=ass_movie_actor,
                         backref='movies')

    catagory = Column(String(20))

    nation = relationship('Nation', secondary=ass_movie_nation,
                          backref='movies')

    language = relationship('Language', secondary=ass_movie_language,
                            backref='movies')

    pub_data = Column(String(20))

    length = Column(String(20))

    subname = Column(String(20))

    evaluate = Column(Integer, ForeignKey('evaluation.id'))

    tag = relationship('MovieTag', secondary=ass_movie_tag,
                       backref='movies')

    subintro = Column(Text(300))

    def __repr__(self):
        return "<User(id= {}, name= {})>".format(self.id, self.name)
