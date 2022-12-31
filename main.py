import undetected_chromedriver as uc

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import logging

from lib.scraper import Scraper
from lib.entities import Info, ChaptersList, InfoWithList, Chapter

app = FastAPI()

logger = logging.getLogger(__name__)

@app.on_event("startup")
def onStart():
    global scraper
    global chromeWebDriver
    chromeWebDriver = uc.Chrome(headless=False)
    scraper = Scraper(chromeWebDriver)

# Not working with --reload option of uvicorn, but here related issues:
# 1. https://github.com/tiangolo/fastapi/issues/1937
# 2. https://github.com/tiangolo/fastapi/issues/5383
# 3. https://github.com/tiangolo/fastapi/issues/5072
@app.on_event("shutdown")
def onDown():
    chromeWebDriver.quit()

class UrlPayload(BaseModel):
    url: HttpUrl

@app.post('/ranobe/scrape')
def scrapeInfoWithList(payload: UrlPayload) -> InfoWithList:
    url = payload.url
    logger.info(f'Scraping info with chapters list: {url}')

    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')
    if not scraper.isPageInfo(url):
        raise HTTPException(400, 'Page is not starting point for scraping ranobe. Accesible will be ranobe info page')

    infoWithList = scraper.scrapeInfoWithList(url)

    return infoWithList

@app.post('/info/scrape')
def scrapeInfo(payload: UrlPayload) -> Info:
    url = payload.url
    logger.info(f'Scraping info page: {url}')
    
    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')

    if not scraper.isPageInfo(url):
        raise HTTPException(400, 'Page is not info')
    
    info = scraper.scrapeInfo(url)
    
    return info

@app.post('/chapters-list/scrape')
def scrapeChapter(payload: UrlPayload) -> ChaptersList:
    url = payload.url
    logger.info(f'Scraping chapters list page: {url}')
    
    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')

    if not scraper.isPageChaptersList(url):
        raise HTTPException(400, 'Page is not chapters list')
    
    chaptersList = scraper.scrapeChaptersList(url)
    
    return chaptersList

@app.post('/chapter/scrape')
def scrapeChapter(payload: UrlPayload) -> Chapter:
    url = payload.url
    logger.info(f'Scraping chapter page: {url}')
    
    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')

    if not scraper.isPageChapter(url):
        raise HTTPException(400, 'Page is not chapter')
    
    chapter = scraper.scrapeChapter(url)
    
    return chapter
