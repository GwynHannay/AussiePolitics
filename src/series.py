import logging
import helpers.db
import helpers.webparser
import utils.common
import utils.config
import utils.metadata


logger = logging.getLogger(__name__)


def get_index_urls() -> list:
    """Scrapes the landing page for this section of the legislation website, and if there
    is an alphabetised index, will build complete URLs from each letter so we can scrape
    the list of documents.

    Args:
        section (str): Part of the legislation website we're scraping, e.g. Acts In Force,
            Constitution. May contain a subsection, indicated by a period, e.g. acts.in_force
        crawl_config (dict): Config items relevant to our scraping.

    Returns:
        list: Complete URLs to be scraped.
    """
    section = utils.config.current_section
    sections = section.split('.')
    if len(sections) > 1:
        logger.debug(
            'Building URL for the index pages of subsection in sections "%s"', sections)
        landing_page_link = utils.common.build_url_from_config(
            crawl_config, type='index', subsection=sections[1])
    else:
        logger.debug('Building URL for index pages of section "%s"', section)
        landing_page_link = utils.common.build_url_from_config(
            crawl_config, type='index')

    landing_page_contents = helpers.webparser.get_soup_from_url(landing_page_link)
    raw_links = helpers.webparser.get_index_title_link(landing_page_contents)

    index_urls = []
    logger.debug(
        'Iterating through raw links to build URLs for scraping: %s', raw_links)
    for link in raw_links:
        index_urls.append(utils.common.build_url(landing_page_link, link))

    return index_urls


def get_metadata_urls() -> list:
    """Builds URLs for web scraping from the TinyDB records stored in previous scrapes.

    Args:
        page_type (str): Web page types, e.g. index, series, details.
        section (str): Part of the legislation website we're scraping, e.g. Acts In Force,
            Constitution.
        crawl_config (dict): Config items relevant to our scraping.

    Returns:
        list: List of URLs built from TinyDB records.
    """
    logger.debug('Fetching DB records')
    records = helpers.db.get_records_by_current_stage()

    urls = []
    logger.debug('Iterating through DB records')
    for series in records:
        try:
            if page_type == 'series':
                url = utils.common.build_url_from_config(
                    crawl_config, page_type, provided_part=series['series_id'])
                urls.append(url)
            else:
                for document in series['documents']:
                    url = utils.common.build_url_from_config(
                        crawl_config, page_type, provided_part=document['register_id'])
                    urls.append(url)
        except Exception as e:
            logger.exception(
                'Failed building URLs for type "%s" in section "%s" with error: %s', page_type, section, e)
            raise Exception

    return urls


def process_index(item: dict):
    """Receives scraped elements from the index page of this section of legislation,
    extracts the document ID for the full series of this document, then inserts a record
    into our TinyDB for the document series with its current stage.

    Args:
        item (dict): Items from Scrapy's Item Pipeline.
    """
    rows = item['rows']

    series = []
    if isinstance(rows, list):
        
        for row in rows:
            soup = helpers.webparser.get_soup_from_text(row.get())
            series.append(helpers.webparser.get_series_id(soup))
    else:
        soup = helpers.webparser.get_soup_from_text(rows.get())
        series.append(helpers.webparser.get_series_id(soup))

    record = {
        'section': item['section'],
        'stage': 'series'
    }

    for series_id in series:
        record['series_id'] = series_id
        helpers.db.insert_record(record)


def process_series(item: dict):
    series_id = str(item['link']).rpartition('/')[-1]
    series_record = helpers.db.get_record_by_series_id(series_id)[0]

    if series_record.get('stage') == 'index':
        record = {
            'section': item['section'],
            'stage': 'details',
            'series_id': series_id
        }

        series_metadata = utils.metadata.main(
            item['metadata'].get(), 'series_pane')

        for field in series_metadata:
            record[field] = series_metadata[field]

        helpers.db.update_record(record)

    rows = item['rows']
    if series_record.get('documents'):
        documents = series_record['documents']
    else:
        documents = []

    if isinstance(rows, list):
        for row in rows:
            new_document = utils.metadata.main(row.get(), 'series_table')
            documents = check_existing_documents(documents, new_document)
    else:
        new_document = utils.metadata.main(rows.get(), 'series_table')
        documents = check_existing_documents(documents, new_document)

    helpers.db.update_list(documents, series_id)


def process_details(item: dict):
    register_id = str(item['link']).split('/')[-2]
    series_record = helpers.db.fetch_series_record_by_document_id(register_id)[
        0]
    document = {}

    for doc in series_record['documents']:
        if doc['register_id'] == register_id:
            document = doc
            break

    document_metadata = utils.metadata.main(
        item['metadata'].get(), 'details')
    document_details = document | document_metadata

    download_link = utils.metadata.get_document_download_link(
        item['rows'].get())
    document_details['download_link'] = download_link

    documents = check_existing_documents(
        series_record['documents'], document_details)
    helpers.db.update_list(documents, series_record['series_id'])

    change_record = {
        'series_id': series_record['series_id'],
        'stage': 'download'
    }
    helpers.db.update_record(change_record)


def check_existing_documents(documents_list: list, new_document: dict) -> list:
    i = 0
    x = len(documents_list)
    current_datetime = ''.join([utils.common.get_current_datetime(), ' AWST'])
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


def add_principal_to_series(section: str):
    docs = helpers.db.fetch_series_records(section)

    for doc in docs:
        principal = utils.metadata.build_principal(doc)
        documents = check_existing_documents(doc['documents'], principal)
        helpers.db.update_list(documents, doc['series_id'])
