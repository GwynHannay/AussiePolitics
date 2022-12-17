import logging
import helpers.webparser
import utils.common
import utils.config
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def build_principal_document(document: dict) -> dict:
    columns = get_template('series')['series_table']['column_order']
    principal = {}

    first_document = get_first_document_in_series(document['documents'])

    for col in columns:
        match col:
            case 'register_id':
                principal[col] = document['series_id']
            case 'document_status':
                principal[col] = 'Principal'
            case 'comp_no':
                principal[col] = '0'
            case 'start_date':
                if document['section'] == 'constitution':
                    principal[col] = '09 Jul 1900'
                else:
                    principal[col] = document['commence_date_formatted']
            case 'end_date':
                if first_document.get('start_date'):
                    principal[col] = utils.common.get_previous_date_string(
                        first_document['start_date'])
                else:
                    principal[col] = ''
            case _:
                principal[col] = ''

    return principal


def get_series(page_content: str):
    series_metadata = get_template('series')
    page_soup = helpers.webparser.get_soup_from_text(page_content)
    series_template = {}
    records = None

    utils.config.set_current_metadata(series_metadata['series_pane'])
    utils.config.set_current_page_soup(page_soup)
    series_template = fill_out_template()

    utils.config.set_current_metadata(series_metadata['series_table'])
    records = fill_out_table_template()

    series_template['documents'] = records
    return series_template


def get_details(page_content: str):
    details_metadata = get_template('details_pane')
    page_soup = helpers.webparser.get_soup_from_text(page_content)

    utils.config.set_current_metadata(details_metadata)
    utils.config.set_current_page_soup = page_soup
    details_template = fill_out_template()

    return details_template


def fill_out_template(section_soup: BeautifulSoup | None = None) -> dict:
    record = {}
    metadata_template = utils.config.current_metadata

    if not section_soup:
        page_soup = utils.config.current_page_soup

        section_soup = check_soup_sections(metadata_template, page_soup)
        if not section_soup:
            section_soup = page_soup

    for field in metadata_template['columns']:
        if field.get('id'):
            field_text = helpers.webparser.get_text_using_exact_id(
                section_soup, field['element'], field['id'])
        elif field.get('id_like'):
            field_text = helpers.webparser.get_text_using_regex_id(
                section_soup, field['element'], field['id_like'])
        elif field.get('class'):
            field_text = helpers.webparser.get_text_by_class(
                section_soup, field['element'], field['class'])
        else:
            field_text = helpers.webparser.get_element_text(
                section_soup, field['element'])

        if field_text:
            record[field['name']] = utils.common.remove_whitespace(field_text)

    return record


def fill_out_table_template():
    metadata_template = utils.config.current_metadata
    page_soup = utils.config.current_page_soup
    records = []

    section_soup = check_soup_sections(metadata_template, page_soup)
    if not section_soup:
        section_soup = page_soup
    
    if section_soup.tbody:
        for row in section_soup.tbody.findChildren('tr', recursive=False):
            base_record = fill_out_template(row)
            unnamed_columns = helpers.webparser.iterate_over_series_columns(
                row, metadata_template['untitled_column_names'])

            if base_record.get('incorporated_amendments_linked'):
                base_record['incorporated_amendments'] = base_record['incorporated_amendments_linked']
                amendment_url = helpers.webparser.get_link_using_regex_id(
                    page_soup, 'hlIncorpTo')
                if amendment_url:
                    base_record['amendment_id'] = amendment_url.split('/')[-1]

            for column in unnamed_columns:
                base_record[column] = unnamed_columns[column]

            ordered_template = order_columns(
                base_record, metadata_template['column_order'])
            records.append(ordered_template)
    
    return records


def check_soup_sections(metadata_template: dict, page_soup: BeautifulSoup) -> BeautifulSoup | None:
    new_soup = None
    if metadata_template.get('div_class'):
        new_soup = helpers.webparser.get_element_from_class(page_soup, 'div', metadata_template['div_class'])
        if not new_soup:
            logger.exception('Section div %s not found in soup: %s', metadata_template['div_class'], page_soup)
            raise Exception
    
    if metadata_template.get('table_class') and new_soup:
        new_soup = helpers.webparser.get_element_from_class(new_soup, 'table', metadata_template['table_class'])
        if not new_soup:
            logger.exception('Table %s not found in soup: %s', metadata_template['table_class'], page_soup)
            raise Exception
    
    return new_soup


def get_series_ids(page_content: str) -> list:
    soup = helpers.webparser.get_soup_from_text(page_content)
    series_ids = helpers.webparser.get_series_ids_from_buttons(soup)

    return series_ids


def order_columns(original_record: dict, column_order: list) -> dict:
    ordered_record = {}
    print(original_record)

    for column in column_order:
        if original_record.get(column):
            if str(column).endswith('_date'):
                print(column)
                ordered_record[column] = utils.common.standardise_date(
                    original_record[column])
            else:
                ordered_record[column] = original_record[column]
        else:
            ordered_record[column] = ''

    return ordered_record


def get_first_document_in_series(documents: list) -> dict:
    if len(documents) > 1:
        sorted_compilations = sorted(documents, key=lambda i: (
            i['comp_no'], utils.common.transform_string_to_date(i['start_date']), i['register_id']))
        first_document = sorted_compilations[0]
    elif len(documents) == 1:
        first_document = documents[0]
    else:
        first_document = {}
    
    return first_document


def get_template(metadata_type: str) -> dict:
    try:
        metadata_config = utils.config.site_metadata
        template = metadata_config.get(metadata_type)
        if not isinstance(template, dict):
            logger.exception(
                'Did not find a valid template for metadata type "%s" in global dict "%s"', metadata_type, metadata_config)
            raise Exception
        return template
    except Exception as e:
        logger.exception(
            'Problem retrieving metadata type "%s" with error: %s', metadata_type, e)
        raise Exception


def get_document_download_link(item: str) -> str | None:
    soup = helpers.webparser.get_soup_from_text(item)
    link = helpers.webparser.get_link_using_regex_id(soup, id='hlPrimaryDoc')

    return link