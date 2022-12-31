from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from typing import List
from urllib.parse import urlparse
import re
from dataclasses import dataclass

from lib.scraper.utils import WebDriverScrollingUtils
from lib.scraper.base import DomainScraper

from lib.entities import Info, ChaptersList, ChaptersListUnit, InfoWithList, Chapter

@dataclass
class ChapterMetadata:
    id: str
    chapter: ChaptersListUnit

class RanobelibScraper(DomainScraper):
    def getDomain(self) -> str:
        return 'ranobelib.me'

    def _isSupported(self, url: str) -> bool:
        return urlparse(url).netloc == self.getDomain()

    def _isPageInfoOrChaptersList(self, url: str) -> bool:
        pathname = urlparse(url).path
        match = re.fullmatch('^\/[a-z\-]+$', pathname)
        return match is not None

    def isPageInfo(self, url: str) -> bool:
        if not self._isSupported(url):
            raise Exception(f'Page is not support foreign domain: {urlparse(url).netloc}')
        
        return self._isPageInfoOrChaptersList(url)

    # TODO add return type for ranobe info
    def scrapeInfo(self, webDriver: WebDriver, url: str) -> Info:
        if not self.isPageInfo(url):
            raise Exception('Page is not available for scraping info for this domain')

        webDriver.get(url)

        title = webDriver.find_element(By.CLASS_NAME, 'media-name__main').text
        
        res = Info(self.getDomain(), url, title)

        res.slug = urlparse(url).path.replace('/', '')
        res.title_alt = webDriver.find_element(By.CLASS_NAME, 'media-name__alt').text
        res.description = webDriver.find_element(By.CLASS_NAME, 'media-description__text').text

        add_info_block = webDriver.find_element(By.CLASS_NAME, 'media-info-list').find_elements(By.CLASS_NAME, 'media-info-list__item')
        add_info_title_substit = {
            'Тип': 'type',
            'Формат выпуска': 'format',
            'Год релиза': 'publish_year',
            'Статус тайтла': 'status',
            'Статус перевода': 'translation_status',
            'Автор': 'author',
            'Издательство': 'publishing_by',
            'Художник': 'artist',
            'Загружено глав': 'chapters_count',
            'Возрастной рейтинг': 'age_restriction',
            'Альтернативные названия': 'alt_titles'
        }
        emit_add_info_title = ['chapters_count']
        for item in add_info_block:
            key = item.find_element(By.CLASS_NAME, 'media-info-list__title').text
            value = item.find_element(By.CLASS_NAME, 'media-info-list__value').text
            if key in add_info_title_substit:
                key = add_info_title_substit[key]
            if key in emit_add_info_title:
                continue
            res.__setattr__(key, value)

        tags_container = webDriver.find_element(By.CLASS_NAME, 'media-tags')
        tags_el = tags_container.find_elements(By.CLASS_NAME, 'media-tag-item ')
        res.tags = []
        for tag_el in tags_el:
            tag = tag_el.text
            if tag != '':
                res.tags.append(tag)

        return res

    def isPageChaptersList(self, url: str) -> bool:
        if not self._isSupported(url):
            raise Exception(f'Page is not support foreign domain: {urlparse(url).netloc}')

        return self._isPageInfoOrChaptersList(url)

    def _scrape_chapter(self, element: WebElement) -> ChapterMetadata:
        metadata_container = element.find_element(By.CLASS_NAME, 'media-chapter')

        id = metadata_container.get_attribute('data-id')

        url = metadata_container.find_element(By.XPATH, './/a').get_attribute('href')
        title = metadata_container.find_element(By.CLASS_NAME, 'media-chapter__name').text
        # added_by = metadata_container.find_element(By.CLASS_NAME, 'media-chapter__username').text
        added_at = metadata_container.find_element(By.CLASS_NAME, 'media-chapter__date').text
        chapter = ChaptersListUnit(url, title, added_at=added_at)

        return ChapterMetadata(id, chapter)
        
    def _scrape_cur_recycler(self, driver: WebDriver) -> List[ChapterMetadata]:
        container = driver.find_element(By.CLASS_NAME, 'vue-recycle-scroller__item-wrapper')
        chapters = container.find_elements(By.CLASS_NAME, 'vue-recycle-scroller__item-view')

        return [self._scrape_chapter(chapter) for chapter in chapters]
    
    # TODO add return type for chapters list
    def scrapeChaptersList(self, webDriver: WebDriver, url: str) -> ChaptersList:
        if not self.isPageChaptersList(url):
            raise Exception('Page is not available for scraping chapters list for this domain')

        webDriver.get(url)

        tabs = webDriver.find_element(By.CLASS_NAME, 'tabs__list')
        tabs.find_element(By.XPATH, "./li[@data-key='chapters']").click()
        webDriver.implicitly_wait(0.6)

        # TODO choose translator

        chapters_collection = dict()

        document_height = WebDriverScrollingUtils.getDocumentScrollHeight(webDriver)
        client_height = WebDriverScrollingUtils.getDocumentClientHeight(webDriver)
        while True:
            scraped_chapters = self._scrape_cur_recycler(webDriver)
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
        
        return ChaptersList(
            domain=self.getDomain(), 
            url=webDriver.current_url, 
            chapters=chapters
        )

    def _goToListFromInfo(self, webDriver: WebDriver) -> None:
        # in this domain info placed on the same page as chapters
        webDriver.find_element(By.XPATH, '//li[2]').click()
        return

    def scrapeInfoWithList(self, webDriver: WebDriver, url: str) -> InfoWithList:
        if not self.isPageInfo(url):
            raise Exception('Page is not available for scraping info with chapters list for this domain')

        info = self.scrapeInfo(webDriver, url)
        self._goToListFromInfo(webDriver)
        chapters_list = self.scrapeChaptersList(webDriver, webDriver.current_url)

        return InfoWithList(
            domain=self.getDomain(), 
            info=info, 
            chapters_list=chapters_list
        )

    def isPageChapter(self, url: str) -> bool:
        if not self._isSupported(url):
            raise Exception(f'Page is not support foreign domain: {urlparse(url).netloc}')

        pathname = urlparse(url).path
        match = re.fullmatch('^\/[a-z\-]+\/v[\d]+\/c[\d]+', pathname)
        return match is not None
    
    # TODO add return type for chapter
    def scrapeChapter(self, webDriver: WebDriver, url: str) -> Chapter:
        if not self.isPageChapter(url):
            raise Exception('Page is not available for scraping chapter for this domain')

        webDriver.get(url)
        
        pathname = urlparse(url).path
        findVolChapRegex = '^\/[a-z\-]+\/v(\d+)\/c(\d+)'
        [volume, nomer] = re.fullmatch(findVolChapRegex, pathname).groups()

        title = webDriver.find_elements(By.CLASS_NAME, 'reader-header-action')[1].find_element(By.CLASS_NAME, 'reader-header-action__text').text
        content = webDriver.find_element(By.CLASS_NAME, 'reader-container').get_attribute('outerHTML')

        prevNextLinks = webDriver.find_element(By.CLASS_NAME, 'reader-header-actions').find_elements(By.TAG_NAME, 'a')
        def extractLink(elem: WebElement):
            if elem.get_attribute('data-disabled') == '':
                return None
            else:
                return elem.get_attribute('href')
        prev = extractLink(prevNextLinks[0])
        next = extractLink(prevNextLinks[1])

        return Chapter(
            domain=self.getDomain(), 
            url=url, 
            volume=volume, 
            nomer=nomer, 
            title=title, 
            content=content, 
            prev=prev, 
            next=next
        )
