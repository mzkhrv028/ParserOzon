import json
import time
from pathlib import Path
from typing import TypeVar
from scrapy.spiders import Spider
from scrapy.crawler import Crawler
from scrapy.item import Item
from itemadapter import ItemAdapter
from scrapy.utils.python import to_bytes

JsonWriterPipelineTV = TypeVar('JsonWriterPipelineTV', bound='JsonWriterPipeline')


class JsonWriterPipeline:
    def __init__(self, outpath_data: Path) -> None:
        self.outpath_data = outpath_data
        self.first_item = True

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> JsonWriterPipelineTV:
        return cls(crawler.settings.get('OUTPATH_DATA'))

    def open_spider(self, spider: Spider) -> None:
        outpath_data = self._handle_outpath(self.outpath_data / spider.name / spider.category)
        self.file = open(f'{outpath_data}/{time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime())}.json', 'w')
        self.file.write('[\n')

    def process_item(self, item: Item, spider: Spider) -> Item:
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(',\n')
        json.dump(ItemAdapter(item).asdict(), self.file, ensure_ascii=False, indent=4)
        return item
    
    def close_spider(self, spider: Spider) -> None:
        self.file.write('\n]')
        self.file.close()
        
    @staticmethod
    def _handle_outpath(outpath: Path) -> Path:
        if not Path.exists(outpath):
            Path.mkdir(outpath, parents=True)
        if not Path.is_dir(outpath):
            raise NotADirectoryError(f"[Error] Not a directory: '{outpath}'")
        return outpath