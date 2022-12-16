import logging
import helpers.webparser
import utils.common
import utils.config


logger = logging.getLogger(__name__)


def build_principal_document(document: dict) -> dict:
    columns = get_template('series_table')['column_order']
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


def get_series_pane(page_content: str):
    template = get_template('series_pane')
    completed_template = fill_out_template(page_content, template)

    return completed_template


def get_series_compilations(page_content: str):
    template = get_template('series_table')
    record = fill_out_template(page_content, template)
    completed_template = fill_out_table_template(page_content, record)

    return completed_template


def get_details_pane(page_content: str):
    template = get_template('details_pane')
    completed_template = fill_out_template(page_content, template)

    return completed_template


def fill_out_template(page_content: str, template: dict) -> dict:
    soup = helpers.webparser.get_soup_from_text(page_content)
    record = {}

    for field in template['columns']:
        if field.get('id'):
            field_text = helpers.webparser.get_text_using_exact_id(
                soup, field['element'], field['id'])
        elif field.get('id_like'):
            field_text = helpers.webparser.get_text_using_regex_id(
                soup, field['element'], field['id_like'])
        elif field.get('class'):
            field_text = helpers.webparser.get_text_by_class(
                soup, field['element'], field['class'])
        else:
            field_text = helpers.webparser.get_element_text(
                soup, field['element'])

        if field_text:
            record[field['name']] = utils.common.remove_whitespace(field_text)

    return record


def fill_out_table_template(item_text: str, completed_template: dict):
    soup = helpers.webparser.get_soup_from_text(item_text)
    columns = helpers.webparser.iterate_over_series_columns(
        soup, get_template('series_table'))

    if completed_template.get('incorporated_amendments_linked'):
        completed_template['incorporated_amendments'] = completed_template['incorporated_amendments_linked']
        amendment_url = helpers.webparser.get_link_using_regex_id(
            soup, 'hlIncorpTo')
        if amendment_url:
            completed_template['amendment_id'] = amendment_url.split('/')[-1]

    for column in columns:
        completed_template[column] = columns[column]

    ordered_template = order_columns(
        completed_template, get_template('series_table')['column_order'])
    return ordered_template


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