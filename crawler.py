import asyncio
import aiohttp
import traceback
from inspect import isawaitable
from urllib.parse import urlparse, urljoin
from log import logger
from signal import SIGTERM, SIGINT
from functools import wraps
from asyncio import CancelledError
from concurrent.futures._base import TimeoutError
from aiohttp.client_exceptions import ClientConnectorError, ClientHttpProxyError, ServerDisconnectedError
# import uvloop

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Crawler:
    """
        async crawler class
    """

    def __init__(self, rooturl, max_redirct=10, max_tasks=25, max_retry=3,
                 timeout=4, headergen=None, proxy=None, loop=None,
                 parsefilter=None, fetchfilter=None):

        self.rooturl = rooturl
        self.dominname = urlparse(rooturl)[1]
        self.loop = loop or asyncio.get_event_loop()
        self.max_redirct = max_redirct
        self.max_tasks = max_tasks
        self.max_retry = max_retry
        self.queue = asyncio.Queue(loop=self.loop)

        self.seen_pages = set()
        self.fail_pages = set()
        self.timeout = timeout

        # headergen should be a function which return headerdict
        self.headergen = headergen or (lambda: None)
        self.proxy = proxy or (lambda: None)
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False, limit=30),
                                             loop=self.loop, headers=self.headergen())

        # can be coroutine
        self.parse_inits = []

        # can be coroutineg
        # para: url, response
        # return : state, url, text
        self.parse_handlers = []

        # can be coroutine
        self.fetch_handlers = []

        # according to url determine whether to parse
        self.parsefilter = parsefilter or (lambda url: True)

        # according to url determine whether to fetch
        self.fetchfilter = fetchfilter or (lambda url: True)

        self.count_dict = {
            "url_parse": 0,
            "parse_fail": 0,
            "url_fetch": 0,
            "remain_task": 0,
            "all_task": 0
        }

    def add_url(self, url, max_redirct=None):
        """
            add url to queue if url not be added before
        """
        urldominname = urlparse(url)[1]
        if urldominname == self.dominname and url not in self.seen_pages:
            self.queue.put_nowait((url, max_redirct or self.max_redirct))
            self.seen_pages.add(url)
            self.count_dict["remain_task"] += 1
            self.count_dict["all_task"] += 1
            logger.info("add url {} to queue".format(url))
            logger.info("has parsed urls{} / fetch urls {} / remain urls {} / all urls {}".format(
                self.count_dict["url_parse"], self.count_dict["url_fetch"],
                self.count_dict["remain_task"], self.count_dict["all_task"]))

    def add_urllst(self, urllst):

        [self.add_url(link) for link in urllst]
        return

    def add_parse_init(self, parsehandler):
        """
            add handler that parse at first
        """
        self.parse_inits.append(parsehandler)

    def add_init(self, handler):
        self.parse_inits.append(handler)

        @wraps(handler)
        def wrap(*args, **kwargs):
            return handler(*args, **kwargs)
        return wrap

    def add_parse_handler(self, parsehandler):
        """
            add handler that parse response and find next link , 
            function and coroutine are accepted
        """
        self.parse_handlers.append(parsehandler)

    def add_parse(self, handler):
        self.parse_handlers.append(handler)

        @wraps(handler)
        def wrap(*args, **kwargs):
            return handler(*args, **kwargs)
        return wrap

    def add_fetch_handler(self, fetchhandler):
        """
            add handler that fetch content from response , f
            unction and coroutine are accepted
        """
        self.fetch_handlers.append(fetchhandler)

    def add_fetch(self, handler):
        self.fetch_handlers.append(handler)

        @wraps(handler)
        def wrap(*args, **kwargs):
            return handler(*args, **kwargs)
        return wrap

    def is_rediect(self, response):
        return response.status in (300, 301, 302, 303, 307)

    async def parse(self, url, max_redirct, session=None):
        logger.info("parse url from {}".format(url))

        if not self.parsefilter(url):
            return url

        self.count_dict["url_parse"] += 1
        retry = self.max_retry

        while retry > 0:
            try:
                session = session or self.session
                request = {"headers": self.headergen(), "url": url,
                           "proxy": self.proxy()}
                if not request.get("method"):
                    request["method"] = "GET"
                with aiohttp.Timeout(self.timeout):
                    async with session.request(**request) as response:
                        logger.info("has parsed urls{} / fetch urls {} / remain urls {} / fail urls {} /all urls {}".format(
                            self.count_dict["url_parse"], self.count_dict["url_fetch"],
                            self.count_dict["remain_task"], self.count_dict['parse_fail'],
                            self.count_dict["all_task"]))
                        # redirct
                        if self.is_rediect(response):
                            logger.info(
                                "parse redirct url from {}".format(url))
                            location = response.headers["location"]
                            nexturl = urljoin(url, location)
                            if nexturl in self.seen_urls:
                                return
                            if max_redirct > 0:
                                self.add_url(nexturl, max_redirct - 1)
                            return None
                        # normal
                        else:
                            if not self.parse_handlers:
                                logger.warning("can't  find parse handlers")

                                try:
                                    self.close()
                                    raise NotImplementedError
                                except:
                                    pass

                            else:
                                logger.info(
                                    "parse normal url from {}".format(url))
                                text = await response.text()
                                for parse_handler in self.parse_handlers:
                                    resp = parse_handler(url, text)
                                    if isawaitable(resp):
                                        urllst = await resp
                                    else:
                                        urllst = resp

                                    # parse func don't need join
                                    urllst = [urljoin(url, i) if not urlparse(
                                        i)[0] else i for i in urllst] if urllst else []
                                    self.add_urllst(urllst)
                                await response.release()
                                del resp, urllst, response
                            return url
            except (TimeoutError, ClientConnectorError, ClientHttpProxyError, ServerDisconnectedError) as e:
                logger.error(traceback.format_exc())
                retry -= 1
                request['proxy'] = self.proxy()
                self.count_dict["parse_fail"] += 1
                self.fail_pages.add(url)
            # except CancelledError as e: 这里使用取消异常会导致task无法正常取消
            #     return None,None
            else:
                retry -= 1
        # when fail parse , add to queue again
        self.queue.put_nowait((url, max_redirct or self.max_redirct))
        self.count_dict["remain_task"] += 1
        logger.info("add url {} to queue".format(url))
        logger.info("has parsed urls {} / fetch urls {} / remain urls {} / fail urls {} / all urls {}".format(
            self.count_dict["url_parse"], self.count_dict["url_fetch"],
            self.count_dict["remain_task"], self.count_dict['parse_fail'],
            self.count_dict["all_task"]))

        return None

    async def fetch(self, url):
        """
            only fetch target url 
        """
        logger.info("fetch page from {}".format(url))

        if not self.fetchfilter(url):
            return

        self.count_dict["url_fetch"] += 1
        logger.info("has parsed urls {} / fetch urls {} / remain urls {} / fail urls {} /all urls {}".format(
            self.count_dict["url_parse"], self.count_dict["url_fetch"],
            self.count_dict["remain_task"], self.count_dict['parse_fail'],
            self.count_dict["all_task"]))

        [fetch_handler.delay(url) for fetch_handler in self.fetch_handlers]
        return

    async def work(self):
        """
            work until queue is empty
        """
        try:
            while True:
                url, max_redirect = await self.queue.get()
                self.count_dict["remain_task"] -= 1
                logger.info("get url {} from queue".format(url))
                logger.info("has parsed urls{} / fetch urls {} / remain urls {} / fail urls {} /all urls {}".format(
                    self.count_dict["url_parse"], self.count_dict["url_fetch"],
                    self.count_dict["remain_task"], self.count_dict['parse_fail'],
                    self.count_dict["all_task"]))
                url = await self.parse(url, max_redirect)
                if url and self.fetchfilter(url):
                    await self.fetch(url)
                logger.debug("queue length {}".format(self.queue.qsize()))
                self.queue.task_done()
        except CancelledError:
            pass

    async def run(self):
        """
            run until all tasks complete
        """
        logger.info("crawler  starting")

        # add first parse url into queue
        for parse_handler in self.parse_inits:
            urllst = parse_handler(self.session)
            if isawaitable(urllst):
                urllst = await urllst
            urllst = [urljoin(self.rooturl, i)
                      for i in urllst] if urllst else []
            self.add_urllst(urllst)

        [self.loop.create_task(self.work()) for _ in range(self.max_tasks)]
        await self.queue.join()
        logger.info("tasks all done")
        self.close()

    def close(self):

        for task in asyncio.Task.all_tasks():
            task.cancel()
        logger.info("complete {} tasks ".format(len(self.seen_pages)))
        logger.info("crawler is stoped ")

    def supervisor(self):
        for _signal in (SIGINT, SIGTERM):
            try:
                self.loop.add_signal_handler(_signal, self.close)
            except NotImplementedError:
                logger.warn(
                    'loop.add_signal_handlerr is not implemented on this platform.')
        try:
            self.loop.run_until_complete(self.run())
        except CancelledError:
            logger.info("loop is stoped ")
        finally:
            self.session.close()
            self.loop.close()


def main():

    mycrawler = Crawler("https://www.nju.edu.cn/")
    mycrawler.supervisor()


if __name__ == '__main__':
    main()
