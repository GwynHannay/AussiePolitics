from utils import common


def main(section: str, common_config: dict, crawl_config: dict):
    if not section == 'constitution':
        get_indexes(common_config, crawl_config)


def get_url(common_config: dict, crawl_config: dict, type: str):
    base_url = common_config['base_url']
    part = crawl_config['landing_url']
    prefix = common_config['url_parts'][type].get('prefix')
    suffix = common_config['url_parts'][type].get('suffix')

    complete_url = common.build_url(base_url, part, prefix, suffix)
    return complete_url


def get_indexes(common_config: dict, crawl_config: dict):
    landing_page = get_url(common_config, crawl_config, type='index')
    print(landing_page)