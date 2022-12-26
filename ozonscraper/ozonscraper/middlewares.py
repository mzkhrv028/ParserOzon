from typing import TypeVar
from selenium import webdriver

from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.crawler import Crawler
from scrapy.http.request import Request
from scrapy.spiders import Spider


SeleniumMiddlewareTV = TypeVar('SeleniumMiddlewareTV', bound='SeleniumMiddleware')


class SeleniumMiddleware:
    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> SeleniumMiddlewareTV:
        c = cls(crawler.settings.get('USER_AGENT'))
        crawler.signals.connect(c.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(c.spider_closed, signal=signals.spider_closed)
        return c

    def process_request(self, request: Request, spider: Spider) -> HtmlResponse:
        try:
            self.driver.get(request.url)
            page_source = self.driver.page_source
        except Exception as ex:
            self.driver.close()
            self.driver.quit()
            print(ex)
        return HtmlResponse(request.url, encoding='utf-8', body=page_source)

    def spider_opened(self, spider: Spider) -> None:
        self.driver = webdriver.Firefox(options=self._set_options_driver())

    def spider_closed(self, spider: Spider) -> None:
        self.driver.close()
        self.driver.quit()
    
    def _set_options_driver(self) -> webdriver.FirefoxOptions:
        options = webdriver.FirefoxOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={self.user_agent}')
        options.add_argument('--start-maximized')
        options.add_argument('--headless')
        return options