# async-crawler
一个可定制的基于eventloop的分布式爬虫,可以从豆瓣等网站上爬取信息
## 结构
* uvloop实现eventloop
* aiohttp实现客户端http异步请求
* celery,redis实现任务队列
* alembic,sqlalchemy建立,操作数据库模型
![crawler.png](https://ooo.0o0.ooo/2017/05/27/592941b305436.png)
## 基本使用
### 定义url过滤器
```
def parsefilter(url):
    """
    return a bool  e.g. return urlparse(url)[2].split('/')[1] == 'tag'
    """
    pass

def fetchfilter(url):
    """
    return a bool e.g. return urlparse(url)[2].split('/')[1] == 'subject'
    """
    pass
```
### 定义代理规则
```
def proxy():
    """
    return a string  e.g.'http://218.201.98.196:3128'
    """
    pass
```
### 定义header规则
```
def headersgen():
    """
    return a dict e.g.{'User-Agent': ..,
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Connection': 'keep-alive',
                       'Cookie': ..}
    """
    pass
```
### 实例爬虫app
```
def 
doubancrawler = Crawler(rooturl,parsefilter=parsefilter, fetchfilter=fetchfilter)
```
### 添加init_parsehandler
```
@doubancrawler.add_init
async def inithandle(session):
    """
    return a urllist e.g. ["https://movie.douban.com/"]
    """
    pass
```
### 添加parsehandler
```
@doubancrawler.add_parse
def movieurlparse(url, text):
    """
    return a urllist e.g. ["https://movie.douban.com/"]
    """
    pass
```
### 添加celery task
```
doubancrawler.add_fetch_handler(fecthdoubanmovie)
```
### 运行爬虫
```
def main():
    doubancrawler.supervisor()


if __name__ == '__main__':
    main()
```
### 经验教训总结
* aiohttp居然不支持https代理
* sqlalchemy在multiprocessing必须使用[`Engine.dispose()`](http://docs.sqlalchemy.org/en/latest/core/connections.html)
* eventloop的终止问题 对所用task,调用`task.cancel()`,会对每一个task引发`CancelledError`,包括loop.
* 在实际应用中发现,sql的存取为性能瓶颈,在存取中错误地使用了大量查询操作,后续准备在爬取时将数据直接存储到
redis中,再进行关系数据库操作.