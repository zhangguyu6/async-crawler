# -*- coding: utf-8 -*-
from .worker import app
from .setting import async_decorator
from bs4 import BeautifulSoup
from bs4.element import Tag
from contextlib import contextmanager
from aiohttp.client_exceptions import ClientConnectorError, ClientHttpProxyError, ServerDisconnectedError
from help import headersgen, proxy
from models import Movie, Evaluation, Actor, Dirctor, Scriptwriter, Nation, Language, MovieTag
import config
import traceback
import tasks.setting as setting


logger = setting.logger


@contextmanager
def scoped_session():
    session = config.db_session["dbsession"]()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@app.task(bind=True, max_retries=3, default_retry_delay=10)
@async_decorator
async def fecthdoubanmovie(self, url):
    session = config.db_session["client"]
    async with session.get(url, headers=headersgen(), proxy=proxy()) as resp:
        try:
            text = await resp.text()
            soup = BeautifulSoup(text, "lxml")
            title = soup.find("title").text.strip()
            dirctorlist = [i.text for i in soup.find_all(
                "a", rel="v:directedBy")]
            scriptwriterlist = [i.strip() for i in [i for i in soup.find(
                "span", text="编剧").next_siblings][1].text.split('/')]
            actorlist = [i.strip(' .') for i in [i for i in soup.find(
                "span", text="主演").next_siblings][1].text.split('/')]
            catagorylist = " ".join([i.text for i in soup.find_all(
                "span", property="v:genre")])
            nation = soup.find("span", text="制片国家/地区:").next_sibling.strip()
            language = soup.find("span", text="语言:").next_sibling.strip()
            pub_data = soup.find("span", property="v:initialReleaseDate").text
            length = soup.find("span", property="v:runtime").text
            subname = soup.find("span", text="又名:").next_sibling.split('/')[0].strip()
            aver = soup.find("strong", property="v:average").text
            evalnum = soup.find("span", property="v:votes").text
            starts = [i.text for i in soup.find_all(
                "span", class_="rating_per")]
            taglist = [i.text.strip() for i in soup.find(
                "div", class_="tags-body").children if isinstance(i, Tag)]
            subintro = soup.find("span", property="v:summary").text.strip()
        except (ClientConnectorError, ClientHttpProxyError, ServerDisconnectedError, AttributeError) as exc:
            raise self.retry(countdown=5, exc=exc)
        except Exception as exc:
            logger.error(traceback.format_exc())
            logger.error(exc)
        else:
            with scoped_session() as dbsession:
                if not dbsession.query(Movie).filter(Movie.title == title).all():
                    evaluate = Evaluation(score=float(aver),
                                          evalnums=int(evalnum),
                                          fivestar=float(starts[0][:-1]) / 100,
                                          fourstar=float(starts[1][:-1]) / 100,
                                          threestar=float(
                                              starts[2][:-1]) / 100,
                                          twostar=float(starts[3][:-1]) / 100,
                                          onestar=float(starts[4][:-1]) / 100)
 

                    dirctorlist = [dbsession.query(Dirctor).filter(Dirctor.dirctor_name == dirctorname).all()[0] if
                                   dbsession.query(Dirctor).filter(Dirctor.dirctor_name == dirctorname).all() else
                                   Dirctor(dirctor_name=dirctorname) for dirctorname in dirctorlist]

                    actorlist = [dbsession.query(Actor).filter(Actor.actor_name == actorname).all()[0] if
                                 dbsession.query(Actor).filter(Actor.actor_name == actorname).all() else
                                 Actor(actor_name=actorname) for actorname in actorlist]

                    scriptwriterlist = [dbsession.query(Scriptwriter).filter(Scriptwriter.scriptwriter_name == scriptwriter).all()[0] if
                                        dbsession.query(Scriptwriter).filter(Scriptwriter.scriptwriter_name == scriptwriter).all() else
                                        Scriptwriter(scriptwriter_name=scriptwriter) for scriptwriter in scriptwriterlist]

                    nation = dbsession.query(Nation).filter(Nation.name == nation).all()[0] if \
                        dbsession.query(Nation).filter(Nation.name == nation).all() else \
                        Nation(name=nation)

                    language = dbsession.query(Language).filter(Language.name == language).all()[0] if \
                        dbsession.query(Language).filter(Language.name == language).all() else \
                        Language(name=language)

                    taglistlist = [dbsession.query(MovieTag).filter(MovieTag.movietag_name == movietagname).all()[0] if
                                   dbsession.query(MovieTag).filter(MovieTag.movietag_name == movietagname).all() else
                                   MovieTag(movietag_name=movietagname) for movietagname in taglist]

                    
                    dbsession.add(evaluate)
                    dbsession.commit()
                    movie = Movie(title=title,
                                  catagory=catagorylist,
                                  pub_data=pub_data,
                                  length=length,
                                  subname=subname,
                                  subintro=subintro,
                                  evaluate=evaluate.id)

                    movie.dirctor.extend(dirctorlist)
                    movie.scriptwriter.extend(scriptwriterlist)
                    movie.actor.extend(actorlist)
                    movie.nation.append(nation)
                    movie.language.append(language)
                    movie.tag.extend(taglistlist)

                    
                    dbsession.add(movie)
                    dbsession.add(nation)
                    dbsession.add(language)
                    dbsession.add_all(dirctorlist)
                    dbsession.add_all(actorlist)
                    dbsession.add_all(scriptwriterlist)
                    dbsession.add_all(taglistlist)
