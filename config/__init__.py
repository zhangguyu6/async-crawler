from .useragents import user_agents
from .url import sqlurl
global pl
with open("config/proxy.txt") as f:
    pl = [i for i in f.readlines()]

db_session = {}
