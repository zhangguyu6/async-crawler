# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import uvloop
import config
from sqlalchemy.orm import sessionmaker
from billiard import current_process
from celery.signals import worker_process_init, worker_process_shutdown
from functools import wraps
from concurrent.futures import CancelledError
import traceback
from celery.utils.log import get_task_logger
from models import engine
logger = get_task_logger(__name__)


# 为每个celery进程;建立一个loop,一个session


@worker_process_init.connect
def init_handle(**kwargs):
    # 保存一个全局session实例,自带DNS缓存,可以很方便的改写head,cookie
    global client, celerysession
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    p = current_process()
    logger.info("eventloop has been  set up on worker {}".format(p.index + 1))
    client = aiohttp.ClientSession(loop=loop)
    engine.dispose()
    celerysession = sessionmaker(bind=engine)
    config.db_session["dbsession"] = celerysession
    config.db_session["client"] = client
    logger.info("session has been  set up on worker {}".format(p.index + 1))


@worker_process_shutdown.connect
def finally_handle(**kwargs):
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(client.close())
    p = current_process()
    logger = get_task_logger(__name__)
    logger.info("session has been  closed on worker {}".format(p.index + 1))
    try:
        for task in asyncio.Task.all_tasks():
            task.cancel()
    except CancelledError:
        logger.info("loop has been  closed on worker {}".format(p.index + 1))
        loop.close()


# 可重入的协程装饰器,将协程放入loop中,并安排运行
def async_decorator(core):
    @wraps(core)
    def wrap(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(core(*args, **kwargs))

        except Exception as exc:
            logger.debug(traceback.format_exc())
            raise args[0].retry(exc=exc, countdown=1)
    return wrap
