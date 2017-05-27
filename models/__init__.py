from .base import Base,engine
from .move import Movie
from .tag import Tag, MovieTag, BookTag
from .person import Person, Actor, Dirctor, Scriptwriter
from .language import Language
from .nation import Nation
from .evaluation import Evaluation


def main():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
if __name__ == '__main__':
    main()