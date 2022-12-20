import scrapy
import re
import json
from scrapy.http import Request
from scrapy.http import Response
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

    def __init__(self, page: str = 1, category: str = 'smartphone', mode: str = None, name: str = None, **kwargs) -> None:
        super(CardproductSpider, self).__init__(name, category=category, **kwargs)
        self.page = int(page)
        self.mode = mode
        self.category = category

    def start_requests(self) -> Request:
        start_urls = [f'https://www.ozon.ru/category/{self.categories[self.category]}/']
        for url in start_urls:
            for page in range(1, self.page + 1):
                    yield Request(url + f'?page={page}' if page > 1 else url, dont_filter=True)

    def parse(self, response: Response) -> dict:
        cardproduct_data = self._handle_data(response.text)

        for cardproduct_value in cardproduct_data['state']['trackingPayloads'].values():
            if isinstance(cardproduct_value, dict) and cardproduct_value.get('type') == 'product':
                if self.mode == "full":
                    cardproduct = cardproduct_value
                else:
                    cardproduct = {key: cardproduct_value.get(key) for key in CardproductItem.__match_args__}
                yield cardproduct

    @staticmethod
    def _handle_data(data: str) -> dict:
        match = re.search(r"(?<=window\.__NUXT__=JSON.parse\(\').+}(?=\')", data, flags=re.DOTALL)

        if match:
            data = match.group()
        else:
            print('[Error] Unsuccessfully handled')
            return match

        return json.loads(data
            .replace(r'\n', '')
            .replace(r'\\', '\\')
            .replace(r'\"', '"')
            .replace(r'\\"', "\'")
            .replace('"{', '{')
            .replace('}"', '}')
        )