import json
from utils import series, scrapy_helper, common


page_types = ['index', 'series', 'download']


def main(sections: list):
    full_config = load_config()
    crawl_config = get_common_config(full_config)
    
    for section in sections:
        piece = section.split('.')[0]
        crawl_config['section'] = full_config['index_urls'][piece]
        crawl_section(section, crawl_config)


def load_config():
    with open('config/legislation.json') as f:
        configs = json.loads(f.read())
        return configs


def read_config(config: dict, sections: list):
    relevant_config = {}
    for section in sections:
        relevant_config[section] = config[section]
    
    return relevant_config


def get_common_config(config: dict):
    common_config = {
        'base_url': config['base_url'],
        'index_url': {
            'prefix': config['index_urls']['prefix']
        },
        'series_url': config['series_url'],
        'download_url': config['download_url']
    }
    return common_config


def crawl_section(section: str, crawl_config: dict):
    index_urls = series.get_indexes(section, crawl_config)

    if index_urls:
        scrapy_helper.run_scrapy(urls=[index_urls[2]], page_type='index')
    else:
        index_url = common.build_url_from_config(config=crawl_config, type='index')
        scrapy_helper.run_scrapy(urls=[index_url], page_type='index')
    
    print('Finished: {}'.format(section))
