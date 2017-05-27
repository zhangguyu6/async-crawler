import configparser
config = configparser.ConfigParser()
config.read('./alembic.ini')
sqlurl = config['alembic']['sqlalchemy.url']
