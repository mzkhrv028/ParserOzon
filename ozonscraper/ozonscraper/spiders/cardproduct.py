import scrapy
import re
import json
from typing import Union, Optional, Iterable

from scrapy.http import Request
from scrapy.http import HtmlResponse
from ozonscraper.items import CardproductItem


class CardproductSpider(scrapy.Spider):
    name = 'cardproduct'
    allowed_domains = ['www.ozon.ru']
    categories = {
        'smartphone': 'smartfony-15502',
        'laptop': 'noutbuki-15692',
        'tablets': 'planshety-15525',
        'tv': 'televizory-15528',
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            'ozonscraper.pipelines.JsonWriterPipeline': 300,
        }
    }

    def __init__(self, page: str = '1', category: str = 'smartphone', mode: str = None, name: str = None, **kwargs) -> None:
        super(CardproductSpider, self).__init__(name, category=category, **kwargs)
        
        try:
            self.page = int(page)
        except ValueError:
            raise ValueError(f'page must be an integer, not {page}')
        except Exception as ex:
            self.logger.critical(f'{ex}')

        if mode != 'full':
            self.mode = False

        if category not in CardproductSpider.categories:
            raise ValueError(f'category must be from CardproductSpider.categories, not {category}')
        else:
            self.category = category

    def start_requests(self) -> Iterable[Request]:
        start_urls = [f'https://www.ozon.ru/category/{self.categories[self.category]}/']
        for url in start_urls:
            for page in range(1, self.page + 1):
                    yield Request(url + f'?page={page}' if page > 1 else url, dont_filter=True)

    def parse(self, response: HtmlResponse) -> dict[str, Union[str, int]]:
        cardproduct_data = self._handle_data(response.text)

        if cardproduct_data is None:
            return {}

        for cardproduct_value in cardproduct_data['state']['trackingPayloads'].values():
            if isinstance(cardproduct_value, dict) and cardproduct_value.get('type') == 'product':
                if self.mode:
                    cardproduct = cardproduct_value
                else:
                    cardproduct = {key: cardproduct_value.get(key) for key in CardproductItem.__match_args__}
                yield cardproduct

    def _handle_data(self, data: str) -> Optional[dict]:
        match = re.search(r"(?<=window\.__NUXT__=JSON.parse\(\'){.*?}(?=\')", data, flags=re.DOTALL)
        if match:
            data = match.group()
        else:
            self.logger.error('Unsuccessfully handled')
            return match
        return json.loads(data
            .replace(r'\n', '')
            .replace(r'\\', '\\')
            .replace(r'\"', '"')
            .replace(r'\\"', "\'")
            .replace('"{', '{')
            .replace('}"', '}')
        )