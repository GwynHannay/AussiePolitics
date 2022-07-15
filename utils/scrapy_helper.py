import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
from utils import tinydb_helper

class LegislationPipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        print('Pipeline Here')
        items = ItemAdapter(item).asdict()
        record = {
            'link': items['link'],
            'page_type': items['page_type']
        }
        tinydb_helper.insert_record(record)
        print('End of Pipeline')


def run_scrapy(urls, page_type):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'utils.legislation.settings')
    if "twisted.internet.reactor" in sys.modules:
        del sys.modules["twisted.internet.reactor"]
    process = CrawlerProcess(get_project_settings())
    process.crawl('pages', urls=urls, page_type=page_type)
    process.start()