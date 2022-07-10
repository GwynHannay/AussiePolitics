import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter

class LegislationPipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        print('Pipeline Here')
        print(ItemAdapter(item).asdict())
        print('End of Pipeline')


def run_scrapy(urls):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'utils.legislation.settings')
    process = CrawlerProcess(get_project_settings())
    process.crawl('pages', urls=urls)
    process.start()