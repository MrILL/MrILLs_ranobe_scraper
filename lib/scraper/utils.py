from selenium.webdriver.chrome.webdriver import WebDriver

class WebDriverScrollingUtils:
    def getDocumentScrollHeight(driver: WebDriver) -> int:
        return driver.execute_script('return document.documentElement.scrollHeight')

    def getDocumentClientHeight(driver: WebDriver) -> int:
        return driver.execute_script('return document.documentElement.clientHeight')

    def getDocumentScrollTop(driver: WebDriver) -> int:
        return driver.execute_script('return document.documentElement.scrollTop')

    def documentScrollBy(driver: WebDriver, x: int, y: int) -> None:
        return driver.execute_script(f"window.scrollBy({x}, {y})")
