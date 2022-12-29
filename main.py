import undetected_chromedriver as uc
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import logging
from urllib.parse import urlparse
import re

class WebDriverScrollingUtils:
    def getDocumentScrollHeight(driver: WebDriver) -> int:
        return driver.execute_script('return document.documentElement.scrollHeight')

    def getDocumentClientHeight(driver: WebDriver) -> int:
        return driver.execute_script('return document.documentElement.clientHeight')

    def getDocumentScrollTop(driver: WebDriver) -> int:
        return driver.execute_script('return document.documentElement.scrollTop')

    def documentScrollBy(driver: WebDriver, x: int, y: int) -> None:
        return driver.execute_script(f"window.scrollBy({x}, {y})")

class DomainScraper:
    def __init__(self) -> None:
        (self)

    def getDomain() -> str:
        return ''

    def _isSupported(url: str) -> bool:
        return False

    def isPageInfo(url: str) -> bool:
        return False

    def scrapeInfo(webDriver: WebDriver, url: str) -> any:
        return None

    def isPageChaptersList(url: str) -> bool:
        return False

    def scrapeChaptersList(webDriver: WebDriver, url: str) -> any:
        return None

    def isPageChapter(url: str) -> bool:
        return False
    
    def scrapeChapter(webDriver: WebDriver, url: str) -> any:
        return None

class RanobelibScraper(DomainScraper):
    def __init__(self) -> None:
        super().__init__()

    def getDomain() -> str:
        return 'ranobelib.me'

    def _isSupported(url: str) -> bool:
        return urlparse(url).netloc == RanobelibScraper.getDomain()

    def _isPageInfoOrChaptersList(url: str) -> bool:
        pathname = urlparse(url).path
        match = re.fullmatch('^\/[a-z\-]+$', pathname)
        return match is not None

    def isPageInfo(url: str) -> bool:
        if not RanobelibScraper._isSupported(url):
            raise Exception(f'Page is not support foreign domain: {urlparse(url).netloc}')
        
        return RanobelibScraper._isPageInfoOrChaptersList(url)

    # TODO add return type for ranobe info
    def scrapeInfo(webDriver: WebDriver, url: str) -> any:
        if not RanobelibScraper.isPageInfo(url):
            raise Exception('Page is not available for scraping info for this domain')

        webDriver.get(url)

        res = dict()

        res['url'] = url
        res['slug'] = urlparse(url).path.replace('/', '')
        res['title'] = webDriver.find_element(By.CLASS_NAME, 'media-name__main').text
        res['title_alt'] = webDriver.find_element(By.CLASS_NAME, 'media-name__alt').text
        res['description'] = webDriver.find_element(By.CLASS_NAME, 'media-description__text').text

        add_info_block = webDriver.find_element(By.CLASS_NAME, 'media-info-list').find_elements(By.CLASS_NAME, 'media-info-list__item')

        add_info_title_substit = {
            'Тип': 'type',
            'Формат выпуска': 'format',
            'Год релиза': 'publish_year',
            'Статус тайтла': 'status',
            'Статус перевода': 'translation_status',
            'Автор': 'author',
            'Издательство': 'publishing_by',
            'Загружено глав': 'chapters',
            'Художник': 'artist',
            'Возрастной рейтинг': 'age_restriction',
            'Альтернативные названия': 'alt_titles'
        }
        emit_add_info_title = ['chapters']

        for item in add_info_block:
            item_title = item.find_element(By.CLASS_NAME, 'media-info-list__title').text
            item_value = item.find_element(By.CLASS_NAME, 'media-info-list__value').text

            if item_title in add_info_title_substit:
                item_title = add_info_title_substit[item_title]

            if item_title in emit_add_info_title:
                continue
            
            res[item_title] = item_value

        tags_container = webDriver.find_element(By.CLASS_NAME, 'media-tags')
        tags = tags_container.find_elements(By.CLASS_NAME, 'media-tag-item ')
        res['tags'] = []
        for tag in tags:
            if tag.text != '':
                res['tags'].append(tag.text)

        return res

    def isPageChaptersList(url: str) -> bool:
        if not RanobelibScraper._isSupported(url):
            raise Exception(f'Page is not support foreign domain: {urlparse(url).netloc}')

        return RanobelibScraper._isPageInfoOrChaptersList(url)

    def _scrape_chapter(element: WebElement):
        metadata_container = element.find_element(By.CLASS_NAME, 'media-chapter')

        id = metadata_container.get_attribute('data-id')

        chapter = dict()

        # chapter['isRed'] = metadata_container.get_attribute('data-is-read') == 'true'
        chapter['url'] = metadata_container.find_element(By.XPATH, './/a').get_attribute('href')
        chapter['title'] = metadata_container.find_element(By.CLASS_NAME, 'media-chapter__name').text
        # chapter['added_by'] = metadata_container.find_element(By.CLASS_NAME, 'media-chapter__username').text
        chapter['added_at'] = metadata_container.find_element(By.CLASS_NAME, 'media-chapter__date').text

        res = dict()
        res['id'] = id
        res['chapter'] = chapter
        return res
        
    def _scrape_cur_recycler(driver: WebDriver):
        container = driver.find_element(By.CLASS_NAME, 'vue-recycle-scroller__item-wrapper')
        chapters = container.find_elements(By.CLASS_NAME, 'vue-recycle-scroller__item-view')

        res = [RanobelibScraper._scrape_chapter(chapter) for chapter in chapters]

        return res
    
    # TODO add return type for chapters list
    def scrapeChaptersList(webDriver: WebDriver, url: str) -> any:
        if not RanobelibScraper.isPageChaptersList(url):
            raise Exception('Page is not available for scraping chapter list for this domain')

        webDriver.get(url)

        tabs = webDriver.find_element(By.CLASS_NAME, 'tabs__list')
        tabs.find_element(By.XPATH, "./li[@data-key='chapters']").click()
        webDriver.implicitly_wait(0.6)

        # TODO choose translator

        chapters_collection = dict()

        document_height = WebDriverScrollingUtils.getDocumentScrollHeight(webDriver)
        client_height = WebDriverScrollingUtils.getDocumentClientHeight(webDriver)
        while True:
            scraped_chapters = RanobelibScraper._scrape_cur_recycler(webDriver)
            for scraped_chapter in scraped_chapters:
                id = scraped_chapter['id']
                chapter = scraped_chapter['chapter']
                if chapter['title'] is not '':
                    chapters_collection[id] = chapter

            WebDriverScrollingUtils.documentScrollBy(webDriver, 0, client_height)
            webDriver.implicitly_wait(0.2)
            current_scroll = WebDriverScrollingUtils.getDocumentScrollTop(webDriver)
            if current_scroll >= document_height - client_height:
                break
        chapters = list(chapters_collection.values())
        
        res = dict()
        res['url'] = webDriver.current_url
        res['chapters'] = chapters

        return res

    def isPageChapter(url: str) -> bool:
        if not RanobelibScraper._isSupported(url):
            raise Exception(f'Page is not support foreign domain: {urlparse(url).netloc}')

        pathname = urlparse(url).path
        match = re.fullmatch('^\/[a-z\-]+\/v[\d]+\/c[\d]+', pathname)
        return match is not None
    
    # TODO add return type for chapter
    def scrapeChapter(webDriver: WebDriver, url: str) -> any:
        if not RanobelibScraper.isPageChapter(url):
            raise Exception('Page is not available for scraping chapter for this domain')

        webDriver.get(url)

        res = dict()

        res['url'] = url
        
        pathname = urlparse(url).path
        findVolChapRegex = '^\/[a-z\-]+\/v(\d+)\/c(\d+)'
        [volume, nomer] = re.fullmatch(findVolChapRegex, pathname).groups()
        res['volume'] = volume
        res['nomer'] = nomer

        res['title'] = webDriver.find_elements(By.CLASS_NAME, 'reader-header-action')[1].find_element(By.CLASS_NAME, 'reader-header-action__text').text
        res['content'] = webDriver.find_element(By.CLASS_NAME, 'reader-container').get_attribute('outerHTML')

        prevNextLinks = webDriver.find_element(By.CLASS_NAME, 'reader-header-actions').find_elements(By.TAG_NAME, 'a')
        def setLink(obj: dict, key: str, elem: WebElement):
            if elem.get_attribute('data-disabled') == '':
                obj[key] = None
            else:
                obj[key] = elem.get_attribute('href')
        setLink(res, 'prev', prevNextLinks[0])
        setLink(res, 'next', prevNextLinks[1])

        return res

class RanobehubScraper(DomainScraper):
    def __init__(self) -> None:
        super().__init__()

    def getDomain() -> str:
        return 'ranobehub.org'



class Scraper:
    webDriver: WebDriver
    scrapers: 'dict[str, DomainScraper]' = dict()

    def __init__(self, webDriver: WebDriver) -> None:
        self.webDriver = webDriver

        scrapers: list[DomainScraper] = [RanobelibScraper, RanobehubScraper]
        for scraper in scrapers:
            self.scrapers[scraper.getDomain()] = scraper

    def _getDomain(self, url: str) -> str:
        return urlparse(url).netloc

    def isSupported(self, url: str) -> bool:
        return self._getDomain(url) in self.scrapers

    def getDomainScraper(self, url: str) -> DomainScraper:
        if not self.isSupported(url):
            raise Exception('Not supported domain')
        
        return self.scrapers[self._getDomain(url)]

    def isPageInfo(self, url: str) -> bool:
        scraper = self.getDomainScraper(url)

        return scraper.isPageInfo(url)

    def scrapeInfo(self, url: str) :
        scraper = self.getDomainScraper(url)
        if not scraper.isPageInfo(url):
            raise Exception('Page is not info page')
        
        return scraper.scrapeInfo(self.webDriver, url)
        
    def isPageChaptersList(self, url: str) -> bool:
        scraper = self.getDomainScraper(url)

        return scraper.isPageChaptersList(url)

    def scrapeChaptersList(self, url: str) -> any:
        scraper = self.getDomainScraper(url)
        if not scraper.isPageChaptersList(url):
            raise Exception('Page is not chapters list')

        return scraper.scrapeChaptersList(self.webDriver, url)

    def isPageChapter(self, url: str) -> bool:
        scraper = self.getDomainScraper(url)

        return scraper.isPageChapter(url)

    def scrapeChapter(self, url: str) -> any:
        scraper = self.getDomainScraper(url)
        if not scraper.isPageChapter(url):
            raise Exception('Page is not chapter')

        return scraper.scrapeChapter(self.webDriver, url)
    


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

@app.post('/info/scrape')
def scrapeInfo(payload: UrlPayload):
    url = payload.url
    logger.info(f'Scraping info page: {url}')
    
    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')

    if not scraper.isPageInfo(url):
        raise HTTPException(400, 'Page is not info')
    
    info = scraper.scrapeInfo(url)
    
    return info

@app.post('/chapters-list/scrape')
def scrapeChapter(payload: UrlPayload):
    url = payload.url
    logger.info(f'Scraping chapters list page: {url}')
    
    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')

    if not scraper.isPageChaptersList(url):
        raise HTTPException(400, 'Page is not chapters list')
    
    chaptersList = scraper.scrapeChaptersList(url)
    
    return chaptersList

@app.post('/chapter/scrape')
def scrapeChapter(payload: UrlPayload):
    url = payload.url
    logger.info(f'Scraping chapter page: {url}')
    
    if not scraper.isSupported(url):
        raise HTTPException(501, 'Not supported domain')

    if not scraper.isPageChapter(url):
        raise HTTPException(400, 'Page is not chapter')
    
    chapter = scraper.scrapeChapter(url)
    
    return chapter
