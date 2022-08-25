import logging
import helpers.db
import helpers.webparser
import utils.common
import utils.config
import utils.metadata


logger = logging.getLogger(__name__)


def get_index_urls() -> list:
    landing_page_link = utils.common.build_url_from_config()
    landing_page_contents = helpers.webparser.get_soup_from_url(landing_page_link)
    raw_links = helpers.webparser.get_index_title_link(landing_page_contents)

    index_urls = []
    if raw_links:
        for link in raw_links:
            url_parts = {
                'base_url': landing_page_link,
                'core_part': link
            }
            index_urls.append(utils.common.build_url(url_parts))
    else:
        index_urls.append(landing_page_link)

    return index_urls


def get_metadata_urls() -> list:
    records = helpers.db.get_records_by_current_stage()

    urls = []
    for series in records:
        url_parts = get_url_parts(series)

        for part in url_parts:
            urls.append(utils.common.build_url_from_config(part))

    return urls


def get_url_parts(series_record: dict) -> list:
    stage = utils.config.current_stage

    url_parts = []
    if stage == 'series':
        url_parts.append(series_record['series_id'])
    elif stage == 'details':
        for document in series_record['documents']:
            url_parts.append(document['register_id'])
    else:
        raise Exception
    
    return url_parts


def process_index(item: dict):
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

    if series_record.get('stage') == 'series':
        record = {
            'section': item['section'],
            'stage': 'details',
            'series_id': series_id
        }

        series_metadata = utils.metadata.fill_out_template(
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
            new_document = utils.metadata.fill_out_template(row.get(), 'series_table')
            documents = utils.common.check_existing_documents(documents, new_document)
    else:
        new_document = utils.metadata.fill_out_template(rows.get(), 'series_table')
        documents = utils.common.check_existing_documents(documents, new_document)

    helpers.db.update_list(documents, series_id)


def process_details(item: dict):
    register_id = str(item['link']).split('/')[-2]
    series_record = helpers.db.get_record_by_document_id(register_id)[
        0]
    document = {}

    for doc in series_record['documents']:
        if doc['register_id'] == register_id:
            document = doc
            break

    document_metadata = utils.metadata.fill_out_template(
        item['metadata'].get(), 'details_pane')
    document_details = document | document_metadata

    download_link = utils.metadata.get_document_download_link(
        item['rows'].get())
    document_details['download_link'] = download_link

    documents = utils.common.check_existing_documents(
        series_record['documents'], document_details)
    helpers.db.update_list(documents, series_record['series_id'])

    change_record = {
        'series_id': series_record['series_id'],
        'stage': 'download'
    }
    helpers.db.update_record(change_record)


def add_principal_to_series():
    docs = helpers.db.get_records_by_current_stage()

    for doc in docs:
        principal = utils.metadata.build_principal_document(doc)
        documents = utils.common.check_existing_documents(doc['documents'], principal)
        helpers.db.update_list(documents, doc['series_id'])
