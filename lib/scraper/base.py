from selenium.webdriver.chrome.webdriver import WebDriver
from abc import ABC, abstractmethod

from lib.entities import Info, ChaptersList, InfoWithList, Chapter

class DomainScraper(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def getDomain(self) -> str:
        pass

    @abstractmethod
    def _isSupported(self, url: str) -> bool:
        pass

    @abstractmethod
    def isPageInfo(self, url: str) -> bool:
        pass

    @abstractmethod
    def scrapeInfo(self, webDriver: WebDriver, url: str) -> Info:
        pass

    @abstractmethod
    def isPageChaptersList(self, url: str) -> bool:
        pass

    @abstractmethod
    def scrapeChaptersList(self, webDriver: WebDriver, url: str) -> ChaptersList:
        pass

    @abstractmethod
    # Starting point is info page
    def scrapeInfoWithList(self, webDriver: WebDriver, url: str) -> InfoWithList:
        pass

    @abstractmethod
    def isPageChapter(self, url: str) -> bool:
        pass
    
    @abstractmethod
    def scrapeChapter(self, webDriver: WebDriver, url: str) -> Chapter:
        pass
