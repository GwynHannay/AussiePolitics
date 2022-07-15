from urllib.parse import urljoin
from datetime import datetime
from dateutil.parser import parse



def remove_whitespace(text):
    clean_text = " ".join(text.split())
    return clean_text


def standardise_date(date_field):
    parsed_date = parse(date_field)
    formatted_date = ''

    if isinstance(parsed_date, datetime):
        formatted_date = datetime.strftime(parsed_date, '%d %b %Y')
    
    return formatted_date


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


def build_url_from_config(config: dict, type: str, subsection=None):
    base_url = config['base_url']
    section = config['section']
    type_entry = ''.join([type, '_url'])

    if subsection:
        part = section['prefix']
        suffix = section[subsection]
    else:
        part = section
        suffix = config[type_entry].get('suffix')

    prefix = config[type_entry].get('prefix')

    complete_url = build_url(base_url, part, prefix, suffix)
    return complete_url
