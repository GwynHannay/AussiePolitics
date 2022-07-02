from utils import common


def main(section: str, common_config: dict, crawl_config: dict):
    if not section == 'constitution':
        index_urls = get_indexes(common_config, crawl_config)
        print(index_urls)


def get_url_from_parts(common_config: dict, crawl_config: dict, type: str):
    base_url = common_config['base_url']
    part = crawl_config['landing_url']
    type_entry = ''.join([type, '_url'])
    prefix = common_config[type_entry].get('prefix')
    suffix = common_config[type_entry].get('suffix')

    complete_url = get_url(base_url, part, prefix, suffix)
    return complete_url


def get_url(base_url, part, prefix=None, suffix=None):
    complete_url = common.build_url(base_url, part, prefix, suffix)
    return complete_url


def get_indexes(common_config: dict, crawl_config: dict):
    landing_page_link = get_url_from_parts(common_config, crawl_config, type='index')
    landing_page_contents = common.get_soup(landing_page_link)
    landing_elements = {
        'type': 'a',
        'class': common_config['title_link_class'],
        'attribute': 'href'
    }

    raw_links = common.get_soup_elements(landing_page_contents, landing_elements)
    index_urls = []
    for link in raw_links:
        index_urls.append(get_url(landing_page_link, link))
    
    return index_urls