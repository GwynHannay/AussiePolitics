import logging
import os
import sys
import src.series
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter


logging.basicConfig(
    filename='log.txt',
    format='[%(asctime)s] - %(levelname)s in %(name)s, %(funcName)s(): %(message)s',
    level=logging.DEBUG
)

class LegislationPipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item).asdict()
        if adaptor['page_type'] == 'index':
            src.series.process_index(adaptor)
        elif adaptor['page_type'] == 'series':
            src.series.process_series(adaptor)
        elif adaptor['page_type'] == 'details':
            src.series.process_details(adaptor)


def run_scrapy(urls: list, page_type: str, section: str):
    """Runs the Scrapy spider for the list of URLs provided.

    Args:
        urls (list): URLs to be scraped.
        page_type (str): Type of page we're scraping, e.g. 'index', 'series'.
        section (str): Section of the legislation website we're scraping, e.g. Acts In Force,
            Constitution.
    """
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE',
                          'utils.legislation.settings')

    # This prevents the error that the reactor is already installed when running
    # the spider again.
    if "twisted.internet.reactor" in sys.modules:
        del sys.modules["twisted.internet.reactor"]

    process = CrawlerProcess(get_project_settings())
    process.crawl('pages', urls=urls, page_type=page_type, section=section)
    process.start()