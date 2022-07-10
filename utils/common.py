from urllib.parse import urljoin


def build_url(base: str, part: str, prefix=None, suffix=None):
    if prefix and suffix:
        built_part = ''.join([prefix, '/', part, '/', suffix])
    elif prefix and not suffix:
        built_part = ''.join([prefix, '/', part])
    elif not prefix and suffix:
        built_part = ''.join([part, '/', suffix])
    else:
        built_part = part
    
    complete_url = urljoin(base, built_part)
    return complete_url


def build_url_from_config(common_config: dict, crawl_config: dict, type: str):
    base_url = common_config['base_url']
    part = crawl_config['landing_url']
    type_entry = ''.join([type, '_url'])
    prefix = common_config[type_entry].get('prefix')
    suffix = common_config[type_entry].get('suffix')

    complete_url = build_url(base_url, part, prefix, suffix)
    return complete_url
