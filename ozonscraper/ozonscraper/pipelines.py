# import json

# from itemadapter import ItemAdapter

# class JsonWriterPipeline:
#     def open_spider(self, spider):
#         self.file = open('cardproduct_data.jsonl', 'w')

#     def close_spider(self, spider):
#         self.file.close()

#     def process_item(self, item, spider):
#         return item