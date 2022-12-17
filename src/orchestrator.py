import logging
import helpers.crawler
import utils.common
import utils.config
import src.downloader
import src.series


logger = logging.getLogger(__name__)


def main():
    website_sections = utils.config.sections_to_crawl

    for section in website_sections:
        utils.config.set_current_section(section)
        logger.info('---- START SECTION: %s ----', section)
        process_website_section()
        

def process_website_section():
    stages = utils.config.stages

    for stage in stages:
        utils.config.set_current_stage(stage)
        logger.info('---- BEGIN STAGE: %s ----', stage)

        if stage in utils.config.page_types:
            logger.info('---- BEGIN CRAWL ----')
            crawl_webpage()
        elif stage == 'principal':
            logger.info('---- ADD PRINCIPAL ----')
            src.series.add_principal_to_series()
        elif stage == 'download':
            logger.info('---- DOWNLOAD ITEMS ----')
            src.downloader.download_files()


def crawl_webpage():
    urls = get_urls()
    helpers.crawler.run_scrapy(urls)


def get_urls() -> list:
    page_type = utils.config.current_stage
    match page_type:
        case 'index':
            urls = src.series.get_index_urls()
        case 'series':
            urls = src.series.get_metadata_urls()
        case 'details':
            urls = src.series.get_metadata_urls()
        case _:
            logger.exception('No valid page type given: %s', page_type)
            raise Exception
    
    return urls
