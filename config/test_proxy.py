import aiohttp
import asyncio
import random
import string
from useragents import user_agents
pl = []
rl = []
with open("proxy.txt", "r") as f:
    for i in f.readlines():
        pl.append("http://{}".format(i.strip()))




async def fetch(proxy):
    try:
        with aiohttp.Timeout(4):
            connector = aiohttp.TCPConnector(verify_ssl=False, limit=30)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get('https://www.douban.com/', proxy=proxy,
                                       headers=headersgen()) as resp:
                    print(len(rl))
                    if resp.status == 200:
                        rl.append(proxy)
    except Exception as e:
        print(e)


def main():

    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*[fetch(i) for i in pl])
    loop.run_until_complete(tasks)
    with open('proxy.txt', 'w') as f:
        for i in rl:
            f.write(i + '\n')
    print(rl)
if __name__ == '__main__':
    import sys
    from os.path import dirname, abspath
    sys.path.append(dirname(dirname(abspath(__file__))))
    from help import cookiegen, headersgen
    main()
