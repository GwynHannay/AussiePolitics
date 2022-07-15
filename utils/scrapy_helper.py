import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
from utils import series

class LegislationPipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item).asdict()
        if adaptor['page_type'] == 'index':
            series.process_index(adaptor)


def run_scrapy(urls, page_type, section):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'utils.legislation.settings')
    if "twisted.internet.reactor" in sys.modules:
        del sys.modules["twisted.internet.reactor"]
    process = CrawlerProcess(get_project_settings())
    process.crawl('pages', urls=urls, page_type=page_type, section=section)
    process.start()