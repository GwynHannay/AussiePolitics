from utils import common, soup_helper


def main(section: str, common_config: dict, crawl_config: dict):
    if not section == 'constitution':
        index_urls = get_indexes(common_config, crawl_config)
    else:
        index_urls = []
    
    return index_urls


def get_indexes(common_config: dict, crawl_config: dict):
    landing_page_link = common.build_url_from_config(common_config, crawl_config, type='index')
    landing_page_contents = soup_helper.get_soup(landing_page_link)
    landing_elements = {
        'type': 'a',
        'class': common_config['title_link_class'],
        'attribute': 'href'
    }

    raw_links = soup_helper.get_soup_elements(landing_page_contents, landing_elements)
    index_urls = []
    for link in raw_links:
        index_urls.append(common.build_url(landing_page_link, link))
    
    return index_urls


def get_series(common_config: dict, crawl_config: dict):
    series_elements = {
        'type': 'input',
        'value': common_config['series_input_value'],
        'attribute': None
    }