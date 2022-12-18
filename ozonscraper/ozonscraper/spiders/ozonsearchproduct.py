import scrapy
import re
import json
from pathlib import Path

OUTPATH_DATA = Path(Path.cwd().parent, "data")


class OzonSearchProductSpider(scrapy.Spider):
    name = 'OzonSearchProduct'
    allowed_domains = ['www.ozon.ru']
    start_urls = ['https://www.ozon.ru/category/smartfony-15502/']

    def parse(self, response):
        cardproduct_data = self._handle_data(response.text)
        cardproduct_dict = dict()

        for cardproduct_value in cardproduct_data["state"]["trackingPayloads"].values():
            if isinstance(cardproduct_value, dict) and cardproduct_value.get("type") == "product":
                cardproduct_dict[cardproduct_value['link']] = cardproduct_value
                yield cardproduct_value

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
