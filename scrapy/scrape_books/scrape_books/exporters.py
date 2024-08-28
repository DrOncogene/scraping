from collections import defaultdict

from scrapy.exporters import JsonItemExporter

from .items import Book


class JsonGroupedItemExporter(JsonItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file, **kwargs)
        self.data = defaultdict(list)

    def export_item(self, item: Book):
        category = item.get('category')
        del item['category']
        self.data[category].append(dict(item))

    def finish_exporting(self):
        self.file.write(bytes(self.encoder.encode(self.data), encoding='utf-8'))
