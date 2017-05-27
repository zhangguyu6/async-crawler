# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from config import sqlurl

engine = create_engine(
    sqlurl+"?charset=utf8", echo=True)
Base = declarative_base()


def main():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
if __name__ == '__main__':
    # main()
    print(sqlurl)