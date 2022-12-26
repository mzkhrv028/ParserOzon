import scrapy
import re
import json
from pathlib import Path
from typing import TypeVar, Optional, Iterable
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
        self.category = self.check_correct_category(category)
        self.input_path_data = self.search_input_data(outpath_data, category)

    @classmethod
    def from_crawler(cls, crawler: Crawler, **kwargs) -> CharacteristicProductSpiderTV:
        return cls(crawler.settings.get('OUTPATH_DATA'), **kwargs)

    def start_requests(self) -> Iterable[Request]:
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
    
    def get_start_urls(self) -> list[str]:
        with open(self.input_path_data, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [cardproduct['link'] for cardproduct in data]

    def _handle_data(self, data: str) -> Optional[dict]:
        match = re.search(r'(?<="webCharacteristics-939965-pdpPage2column-2":")\{.*?\}(?=")', data)
        if match:
            data = match.group()
        else:
            self.logger.error('Unsuccessfully handled')
            return match
        return json.loads(data.replace(r'\"', '"').replace(r'\\', '\\'))

    @staticmethod    
    def search_input_data(outpath: Path, category: str) -> Path:
        input_path = outpath / 'cardproduct' / category
        if not Path.exists(input_path):
            raise FileNotFoundError(f'directory does not exist: {input_path}')
        if not Path.is_dir(input_path):
            raise NotADirectoryError(f"not a directory: '{input_path}'")

        input_path_data = list(input_path.glob('**/*.json'))
        if not input_path_data:
            raise FileNotFoundError(f'directory is empty: {input_path}')
        return sorted(input_path_data)[0]

    @staticmethod
    def check_correct_category(category: str) -> str:
        if category not in CardproductSpider.categories:
            raise ValueError(f'category must be one of \'{", ".join(CardproductSpider.categories.keys())}\', not {category}')
        return category

