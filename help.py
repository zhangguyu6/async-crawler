import random
import string
from config import pl
from config.useragents import user_agents


def cookiegen():

    return "bid={}".format("".join(random.sample(string.ascii_letters + string.digits, 11)))


def proxy():
    return random.choice(pl)


def headersgen():
    return {
        'User-Agent': random.choice(user_agents),
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': cookiegen()
    }
