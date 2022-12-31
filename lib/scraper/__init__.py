from selenium.webdriver.chrome.webdriver import WebDriver

from urllib.parse import urlparse

from .base import DomainScraper
from .domains import RanobelibScraper, RanobehubScraper
from lib.entities import Info, ChaptersList, InfoWithList, Chapter



class Scraper:
    webDriver: WebDriver
    scrapers: 'dict[str, DomainScraper]' = dict()

    def __init__(self, webDriver: WebDriver) -> None:
        self.webDriver = webDriver

        scrapers: list[DomainScraper] = [RanobelibScraper()]
        # scraper.append(RanobehubScraper()) # TODO

        for scraper in scrapers:
            self.scrapers[scraper.getDomain()] = scraper

    def getDomain(self, url: str) -> str:
        return urlparse(url).netloc

    def isSupported(self, url: str) -> bool:
        return self.getDomain(url) in self.scrapers

    def getDomainScraper(self, url: str) -> DomainScraper:
        if not self.isSupported(url):
            raise Exception('Not supported domain')
        
        return self.scrapers[self.getDomain(url)]

    def isPageInfo(self, url: str) -> bool:
        scraper = self.getDomainScraper(url)

        return scraper.isPageInfo(url)

    def scrapeInfo(self, url: str) -> Info :
        scraper = self.getDomainScraper(url)
        if not scraper.isPageInfo(url):
            raise Exception('Page is not info page')
        
        return scraper.scrapeInfo(self.webDriver, url)
        
    def isPageChaptersList(self, url: str) -> bool:
        scraper = self.getDomainScraper(url)

        return scraper.isPageChaptersList(url)

    def scrapeChaptersList(self, url: str) -> ChaptersList:
        scraper = self.getDomainScraper(url)
        if not scraper.isPageChaptersList(url):
            raise Exception('Page is not chapters list')

        return scraper.scrapeChaptersList(self.webDriver, url)

    def scrapeInfoWithList(self, url: str) -> InfoWithList:
        scraper = self.getDomainScraper(url)
        if not scraper.isPageInfo(url):
            raise Exception('Page is not info page')
        
        return scraper.scrapeInfoWithList(self.webDriver, url)

    def isPageChapter(self, url: str) -> bool:
        scraper = self.getDomainScraper(url)

        return scraper.isPageChapter(url)

    def scrapeChapter(self, url: str) -> Chapter:
        scraper = self.getDomainScraper(url)
        if not scraper.isPageChapter(url):
            raise Exception('Page is not chapter')

        return scraper.scrapeChapter(self.webDriver, url)
