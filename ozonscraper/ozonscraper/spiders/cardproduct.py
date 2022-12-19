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
        "smartphone": "smartfony-15502",
        "laptop": "noutbuki-15692",
        "tablets": "planshety-15525",
        "tv": "televizory-15528",
    }
    start_urls = ['https://www.ozon.ru/category/smartfony-15502/']

    custom_settings = {
        "FEEDS": {
            'data/%(name)s/smartphone/%(time)s.json': {
                'format': 'json',
                'encoding': 'utf8',
                'fields': None,
                'store_empty': False,
                'indent': 4,
                'item_export_kwargs': {
                'export_empty_fields': True,
                },
            },
        }
    }

    def __init__(self, page: str = 1, name: str = None, **kwargs):
        super(CardproductSpider, self).__init__(name, **kwargs)
        self.page = int(page)

    def start_requests(self):
        for url in self.start_urls:
            for page in range(1, self.page + 1):
                    yield Request(url + f"?page={page}" if page > 1 else url, dont_filter=True)

    def parse(self, response: Response):
        cardproduct_data = self._handle_data(response.text)

        for cardproduct_value in cardproduct_data["state"]["trackingPayloads"].values():
            if isinstance(cardproduct_value, dict) and cardproduct_value.get("type") == "product":
                cardproduct = {key: cardproduct_value.get(key) for key in CardproductItem.__match_args__}
                yield CardproductItem(**cardproduct)

    @staticmethod
    def _handle_data(data: str) -> dict:
        match = re.search(r"(?<=window\.__NUXT__=JSON.parse\(\').+}(?=\')", data, flags=re.DOTALL)

        if match:
            data = match.group()
        else:
            print("[Error] Unsuccessfully handled")
            return match

        data = json.loads(data
            .replace(r'\n', '')
            .replace(r'\\', '\\')
            .replace(r'\"', '"')
            .replace(r'\\"', "\'")
            .replace('"{', '{')
            .replace('}"', '}')
        )

        return data
