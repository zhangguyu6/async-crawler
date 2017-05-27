from bs4 import BeautifulSoup
from crawler import Crawler
from urllib.parse import urlparse
from tasks.commontasks import fecthdoubanmovie
from help import headersgen, proxy
from log import logger
from traceback import format_exc


def parsefilter(url):
    return urlparse(url)[2].split('/')[1] == 'tag'


def fetchfilter(url):
    return urlparse(url)[2].split('/')[1] == 'subject'


doubancrawler = Crawler("https://movie.douban.com/", headergen=headersgen,
                        parsefilter=parsefilter, fetchfilter=fetchfilter, proxy=proxy)


@doubancrawler.add_init
async def inithandle(session):
    retry = 3
    while retry > 0:
        try:
            async with session.get("https://movie.douban.com/tag/", proxy=proxy(), headers=headersgen()) as response:
                logger.debug(response.status)
                text = await response.text()
                soup = BeautifulSoup(text, 'lxml')
                a = soup.find('a', class_="tag-title-wrapper").next_siblings
                a = [i for i in a][1]
                urllist = [i["href"] for i in a.find_all('a')]
                return urllist
        except Exception as e:
            logger.error(format_exc())
            retry -= 1
    return []


@doubancrawler.add_parse
def movieurlparse(url, text):
    soup = BeautifulSoup(text, 'lxml')
    urllst = [i.a["href"] for i in soup.find_all("div", class_='pl2')]
    if soup.find("div", class_="paginator"):
        urllst.extend([i["href"] for i in soup.find(
            "div", class_="paginator").find_all("a")])
    return urllst

# doubancrawler.add_fetch_handler(fecthdoubanmovie)


def main():
    doubancrawler.supervisor()


if __name__ == '__main__':
    main()
