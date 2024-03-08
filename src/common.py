import logging
import pytz
import src.config
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


def get_current_date() -> str:
    current_date = datetime.strftime(datetime.now(pytz.timezone("Australia/Perth")), '%Y-%m-%d')
    return current_date


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


def build_url(url_parts: dict) -> str:
    """Generates a complete URL from various components. This may include prefixes or suffixes in addition 
    to the main part we are trying to add onto the base URL.

    Args:
        url_parts (dict): URL components including base, the part to be added, with optional prefix and suffix,
            e.g. base_url: https://legislation.gov.au, core_part: C2004Q00685, prefix: Series.

    Returns:
        str: Completed URL, e.g. 'https://legislation.gov.au/Series/C2004Q00685'
    """
    base_url = url_parts.get('base_url')
    core_part = url_parts.get('core_part')
    prefix = url_parts.get('prefix')
    suffix = url_parts.get('suffix')

    if not base_url or not core_part:
        logger.exception('Missing critical URL components, base "%s" and core "%s"', base_url, core_part)
        raise Exception

    if prefix and suffix:
        built_part = ''.join([prefix, '/', core_part, '/', suffix])
    elif prefix and not suffix:
        built_part = ''.join([prefix, '/', core_part])
    elif not prefix and suffix:
        built_part = ''.join([core_part, '/', suffix])
    else:
        built_part = core_part

    complete_url = urljoin(base_url, built_part)
    return complete_url


def build_url_from_config(provided_part=None) -> str:
    try:
        url_config = src.config.legislation_url_components
        page_type = src.config.current_stage
        current_section = src.config.current_section
        
        section_parts = get_section_components(current_section)
        if len(section_parts) > 1:
            section = section_parts[0]
            subsection = section_parts[1]
        else:
            section = None
            subsection = None

        if page_type == 'index' and section and subsection:
            part = url_config['index_urls'][section]['prefix']
            prefix = url_config['index_urls']['prefix']
            suffix = url_config['index_urls'][section][subsection]
        elif page_type == 'index':
            part = url_config['index_urls'][current_section]
            prefix = url_config['index_urls']['prefix']
            suffix = None
        elif isinstance(provided_part, str):
            part = provided_part
            prefix = url_config['section_urls'][page_type]['prefix']
            suffix = url_config['section_urls'][page_type].get('suffix')
        else:
            logger.error('No URL was provided for type "%s", subsection "%s", with config: %s', page_type, subsection, url_config)
            raise Exception

        url_parts = {
            'base_url': url_config['base_url'],
            'core_part': part,
            'prefix': prefix,
            'suffix': suffix
        }

        complete_url = build_url(url_parts)
        logger.debug('Completed URL: %s', complete_url)
        return complete_url
    except Exception as e:
        logger.exception('Problem building URL from configuration, with error: %s', e)
        logger.debug('Current state: section "%s", stage "%s"', src.config.current_section, src.config.current_stage)
        raise Exception(e)


def check_existing_documents(documents_list: list, new_document: dict) -> list:
    i = 0
    x = len(documents_list)
    current_datetime = ''.join([get_current_datetime(), ' AWST'])
    new_document['first_seen'] = current_datetime
    new_document['last_seen'] = current_datetime

    if x == 0:
        documents_list.append(new_document)
        return documents_list
    else:
        for old_document in documents_list:
            if old_document['register_id'] == new_document['register_id']:
                new_document['first_seen'] = old_document['first_seen']
                documents_list.remove(old_document)
                documents_list.insert(i, new_document)
                break
            elif x == (i + 1):
                documents_list.insert(0, new_document)
                break
            else:
                i = i + 1

        return documents_list


def get_section_components(section: str) -> list:
    return section.split('.')
