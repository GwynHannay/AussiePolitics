import logging
import pytz
from urllib.parse import urljoin
from datetime import date, datetime, timedelta
from dateutil.parser import parse


logger = logging.getLogger(__name__)


def get_current_datetime() -> str:
    logger.debug('get_current_datetime()')
    current_datetime = datetime.strftime(datetime.now(
        pytz.timezone("Australia/Perth")), '%Y-%m-%d %H:%M:%S')
    logger.debug('Returning current datetime: %s', current_datetime)
    return current_datetime


def remove_whitespace(text: str) -> str:
    """Cleans a string of any additional whitespace such as double spacing or tab characters.

    Args:
        text (str): String to be cleaned.

    Returns:
        str: Cleaned string with only single whitespace characters.
    """
    clean_text = " ".join(text.split())
    return clean_text


def standardise_date(date_field: str) -> str:
    """Attempts to parse a string as a datetime, then formats it to our standard date.

    Args:
        date_field (str): Hopefully a parseable datetime.

    Returns:
        str: Date formatted as we want to use it.
    """
    parsed_date = parse(date_field)
    formatted_date = ''

    if isinstance(parsed_date, datetime):
        formatted_date = datetime.strftime(parsed_date, '%d %b %Y')

    return formatted_date


def transform_string_to_date(date_string: str) -> date:
    return datetime.strptime(date_string, '%d %b %Y')


def get_previous_date_string(date_string: str) -> str:
    converted_to_datetime = transform_string_to_date(date_string)
    previous_date = converted_to_datetime - timedelta(days=1)
    new_date_string = previous_date.strftime('%d %b %Y')
    return new_date_string


def build_url(base: str, part: str, prefix=None, suffix=None) -> str:
    """Receives different parts of a URL and generates a complete URL. This may include
    prefixes or suffixes in addition to the main part we are trying to add onto the base URL.

    Args:
        base (str): Base URL, e.g. 'https://legislation.gov.au'
        part (str): URL part to be joined, e.g. 'Browse/ByTitle/Acts', 'C2004Q00685'
        prefix (str, optional): Prefix to be joined to the URL part, e.g. 'Series'. Defaults to None.
        suffix (str, optional): Suffix to be joined to the URL part, e.g. 'Download'. Defaults to None.

    Returns:
        str: Completed URL, e.g. 'https://legislation.gov.au/Series/C2004Q00685'
    """
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


# TODO: This may need to be more generic
def build_url_from_config(config: dict, type: str, subsection=None, provided_part=None) -> str:
    base_url = config['base_url']
    section = config['section']

    if type == 'index':
        prefix = config['index_url']['prefix']
        if subsection:
            part = section['prefix']
            suffix = section[subsection]
        else:
            part = section
            suffix = None
    else:
        if isinstance(provided_part, str):
            part = provided_part
        else:
            logger.error('No URL was provided for type "%s", subsection "%s", with config: %s', type, subsection, config)
            raise Exception
        prefix = config['section_urls'][type]['prefix']
        suffix = config['section_urls'][type].get('suffix')

    complete_url = build_url(base_url, part, prefix, suffix)
    return complete_url
