import scrapy
import re
import json
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlencode

from scrapy.http import Request
from scrapy.http import HtmlResponse
from scrapy.crawler import Crawler
from ozonscraper.items import ProductItem
from ozonscraper.spiders.cardproduct import CardproductSpider


CharacteristicProductSpiderTV = TypeVar('CharacteristicProductSpiderTV', bound='CharacteristicProductSpider')


class CharacteristicProductSpider(scrapy.Spider):
    name = 'chproduct'
    allowed_domains = ['www.ozon.ru']
    custom_settings = {
        'ITEM_PIPELINES': {
            'ozonscraper.pipelines.JsonWriterPipeline': 300,
        }
    }

    def __init__(self, outpath_data: Path, category: str, name: str = None, **kwargs) -> None:
        super(CharacteristicProductSpider, self).__init__(name, **kwargs)
        self.outpath_data = outpath_data

        if category not in CardproductSpider.categories:
            raise ValueError(f'category must be from CardproductSpider.categories, not {category}')
        else:
            self.category = category

    @classmethod
    def from_crawler(cls, crawler: Crawler, **kwargs) -> CharacteristicProductSpiderTV:
        return cls(crawler.settings.get('OUTPATH_DATA'), **kwargs)

    def start_requests(self) -> Request:
        start_urls = self.get_start_urls()
        for url in start_urls:
            params = {
                'url': url,
                'layout_container': 'pdpPage2column',
                'layout_page_index': '2',
            }
            yield Request('https://www.ozon.ru/api/composer-api.bx/page/json/v2?' + urlencode(params), dont_filter=True)

    def parse(self, response: HtmlResponse) -> ProductItem:
        product = ProductItem()
        product_data = self._handle_data(response.xpath('//div[@id="json"]/text()').get())

        if product_data is None:
            return product

        product.link = re.search(r'(?<=https://www.ozon.ru).*?(?=features/)', product_data['link']).group()
        product.productTitle = product_data['productTitle']

        for characteristic in product_data['characteristics']:
            for cshort in characteristic['short']:
                product.characteristics[cshort['key']] = ', '.join([value['text'] for value in cshort['values']])
        return product
    
    def get_start_urls(self):
        outpath_cardproduct = self._check_outpath(self.outpath_data / 'cardproduct' / self.category)
        outpath = sorted(list(outpath_cardproduct.glob('**/*.json')))[0]
        with open(outpath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [cardproduct['link'] for cardproduct in data]

    def _handle_data(self, data: str) -> dict:
        match = re.search(r'(?<="webCharacteristics-939965-pdpPage2column-2":")\{.*?\}(?=")', data)
        if match:
            data = match.group()
        else:
            self.logger.error('Unsuccessfully handled')
            return match
        return json.loads(data.replace(r'\"', '"').replace(r'\\', '\\'))
        
    @staticmethod
    def _check_outpath(outpath: Path) -> Path:
        if not Path.exists(outpath):
            raise FileNotFoundError(f'directory does not exist: {outpath}')
        if not Path.is_dir(outpath):
            raise NotADirectoryError(f"not a directory: '{outpath}'")
        return outpath 

