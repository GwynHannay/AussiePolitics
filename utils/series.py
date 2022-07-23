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
            crawl_config['base_url'], part=document['series_id'], prefix=crawl_config['series_url']['prefix'])
        series_urls.append(url)

    return series_urls


def process_series(item: dict):
    series_id = str(item['link']).rpartition('/')[-1]
    series_status = tinydb_helper.check_series_status(series_id)[0]

    if series_status.get('stage') == 'index':
        record = {
            'section': item['section'],
            'stage': item['page_type'],
            'series_id': series_id
        }

        series_metadata = metadata_collector.main(item['metadata'].get(), 'series_pane')

        for field in series_metadata:
            record[field] = series_metadata[field]
        
        tinydb_helper.update_record(record)

    rows = item['rows']
    documents = []

    if isinstance(rows, list):
        for row in rows:
            documents.append(metadata_collector.main(row.get(), 'series_table'))
    else:
        documents.append(metadata_collector.main(rows.get(), 'series_table'))
    
    tinydb_helper.add_to_record(documents, series_id)
