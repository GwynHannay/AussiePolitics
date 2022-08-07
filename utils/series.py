from utils import common, metadata_collector, soup_helper, tinydb_helper


def get_indexes(section: str, crawl_config: dict) -> list:
    """Scrapes the landing page for this section of the legislation website, and if there
    is an alphabetised index, will build complete URLs from each letter so we can scrape
    the list of documents.

    Args:
        section (str): Part of the legislation website we're scraping, e.g. Acts In Force,
            Constitution.
        crawl_config (dict): Config items relevant to our scraping.

    Returns:
        list: Complete URLs to be scraped.
    """
    sections = section.split('.')
    if len(sections) > 1:
        landing_page_link = common.build_url_from_config(
            crawl_config, type='index', subsection=sections[1])
    else:
        landing_page_link = common.build_url_from_config(
            crawl_config, type='index')

    landing_page_contents = soup_helper.get_soup_from_url(landing_page_link)

    raw_links = soup_helper.get_index_title_link(landing_page_contents)
    index_urls = []
    for link in raw_links:
        index_urls.append(common.build_url(landing_page_link, link))

    return index_urls


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
            soup = soup_helper.get_soup_from_text(row.get())
            series.append(soup_helper.get_series_id(soup))
    else:
        soup = soup_helper.get_soup_from_text(rows.get())
        series.append(soup_helper.get_series_id(soup))

    record = {
        'section': item['section'],
        'stage': item['page_type']
    }

    for series_id in series:
        record['series_id'] = series_id
        tinydb_helper.insert_record(record)


def get_series(section: str, crawl_config: dict) -> list:
    """Retrieves all document series entries from TinyDB with the stage of
    'index' and builds a list of complete URLs for the series page to be scraped.

    Args:
        section (str): Part of the legislation website we're scraping, e.g. Acts In Force,
            Constitution.
        crawl_config (dict): Config items relevant to our scraping.

    Returns:
        list: Complete URLs to be scraped.
    """
    docs = tinydb_helper.fetch_index_records(section)
    series_urls = []

    for document in docs:
        url = common.build_url(
            crawl_config['base_url'],
            part=document['series_id'],
            prefix=crawl_config['series_url']['prefix'])
        series_urls.append(url)

    return series_urls


def process_series(item: dict):
    series_id = str(item['link']).rpartition('/')[-1]
    series_record = tinydb_helper.fetch_series_record_by_id(series_id)[0]

    if series_record.get('stage') == 'index':
        record = {
            'section': item['section'],
            'stage': item['page_type'],
            'series_id': series_id
        }

        series_metadata = metadata_collector.main(
            item['metadata'].get(), 'series_pane')

        for field in series_metadata:
            record[field] = series_metadata[field]

        tinydb_helper.update_record(record)

    rows = item['rows']
    if series_record.get('documents'):
        documents = series_record['documents']
    else:
        documents = []

    if isinstance(rows, list):
        for row in rows:
            new_document = metadata_collector.main(row.get(), 'series_table')
            documents = check_existing_documents(documents, new_document)
    else:
        new_document = metadata_collector.main(rows.get(), 'series_table')
        documents = check_existing_documents(documents, new_document)

    tinydb_helper.update_list(documents, series_id)


def check_existing_documents(documents_list: list, new_document: dict) -> list:
    i = 0
    x = len(documents_list)
    current_datetime = ''.join([common.get_current_datetime(), ' AWST'])
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
    docs = tinydb_helper.fetch_series_records(section)

    for doc in docs:
        principal = metadata_collector.build_principal(doc)
        documents = check_existing_documents(doc['documents'], principal)
        tinydb_helper.update_list(documents, doc['series_id'])


def get_details(section: str, crawl_config: dict) -> list:
    series = tinydb_helper.fetch_series_records(section)
    details_urls = []

    for single in series:
        for document in single['documents']:
            url = common.build_url(
                crawl_config['base_url'],
                part=document['register_id'],
                prefix=crawl_config['download_url']['prefix'],
                suffix=crawl_config['download_url']['suffix'])
            details_urls.append(url)

    return details_urls


def process_details(item: dict):
    register_id = str(item['link']).split('/')[-2]
    series_record = tinydb_helper.fetch_series_record_by_document_id(register_id)[0]
    document = {}

    for doc in series_record['documents']:
        if doc['register_id'] == register_id:
            document = doc
            break
    
    document_metadata = metadata_collector.main(item['metadata'].get(), 'details')
    document_details = document | document_metadata

    download_link = metadata_collector.get_document_download_link(item['rows'].get())
    document_details['download_link'] = download_link
    
    documents = check_existing_documents(series_record['documents'], document_details)
    tinydb_helper.update_list(documents, series_record['series_id'])

    change_record = {
        'series_id': series_record['series_id'],
        'stage': 'details'
    }
    tinydb_helper.update_record(change_record)
