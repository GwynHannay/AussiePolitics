import json
from utils import series, scrapy_helper


def main(sections: list):
    full_config = load_config()
    common_config = get_common_config(full_config)
    
    for section in sections:
        if section == 'constitution':
            crawl_config = full_config[section]
        else:
            crawl_config = full_config[section]['in_force']
        
        crawl_section(section, common_config, crawl_config)


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
    return config['common']


def crawl_section(section: str, common_config: dict, crawl_config: dict):
    urls = series.main(section, common_config, crawl_config)
    scrapy_helper.run_scrapy(urls)
