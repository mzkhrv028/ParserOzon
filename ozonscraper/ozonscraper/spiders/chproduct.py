import scrapy
import re
import json
from pathlib import Path
from typing import TypeVar
from scrapy.http import Request
from scrapy.http import HtmlResponse
from scrapy.crawler import Crawler
from ozonscraper.items import ProductItem

CharacteristicProductSpiderTV = TypeVar('CharacteristicProductSpiderTV', bound='CharacteristicProductSpider')


class CharacteristicProductSpider(scrapy.Spider):
    name = 'chproduct'
    allowed_domains = ['www.ozon.ru']
    custom_settings = {
        'ITEM_PIPELINES': {
            'ozonscraper.pipelines.JsonWriterPipeline': 300,
        }
    }

    def __init__(self, outpath_data: Path = None, category: str = None, name: str = None, **kwargs) -> None:
        super(CharacteristicProductSpider, self).__init__(name, **kwargs)
        self.outpath_data = outpath_data
        self.category = category

    @classmethod
    def from_crawler(cls, crawler: Crawler, **kwargs) -> CharacteristicProductSpiderTV:
        return cls(crawler.settings.get('OUTPATH_DATA'), **kwargs)

    def start_requests(self) -> Request:
        start_urls = self.get_start_urls()
        for url in start_urls:
            yield Request('https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=' + url + '&layout_container=pdpPage2column&layout_page_index=2', dont_filter=True)

    def parse(self, response: HtmlResponse) -> ProductItem:
        product_data = self._handle_data(response.xpath('//div[@id="json"]/text()').get())

        product = ProductItem()
        product.link = re.search(r'(?<=https://www.ozon.ru).*?(?=features/)', product_data['link']).group()
        product.productTitle = product_data['productTitle']

        for characteristic in product_data['characteristics']:
            for cshort in characteristic['short']:
                product.characteristics[cshort['key']] = ', '.join([value['text'] for value in cshort['values']])
        return product
    
    def get_start_urls(self):
        outpath_cardproduct = self.outpath_data / 'cardproduct' / self.category# if Path.exists(self.outpath_data / 'cardproduct') else None
        outpath = sorted(list(outpath_cardproduct.glob('**/*.json')))[0]
        with open(outpath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [cardproduct['link'] for cardproduct in data]

    @staticmethod
    def _handle_data(data: str) -> dict:
        match = re.search(r'(?<="webCharacteristics-939965-pdpPage2column-2":")\{.*?\}(?=")', data)
        if match:
            data = match.group()
        else:
            print('[Error] Unsuccessfully handled')
            return match
        return json.loads(data.replace(r'\"', '"').replace(r'\\', '\\'))
