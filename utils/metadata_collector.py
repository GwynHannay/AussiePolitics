from utils import common, soup_helper


def main(item_text: str, metadata_type: str) -> dict:
    metadata_template = get_template(metadata_type)
    completed_template = fill_out_template(item_text, metadata_template)
    
    if metadata_type == 'series_table':
        soup = soup_helper.get_soup_from_text(item_text)
        columns = soup_helper.iterate_over_series_columns(soup, get_series_column_names())

        if completed_template.get('incorporated_amendments_linked'):
            completed_template['incorporated_amendments'] = completed_template['incorporated_amendments_linked']
            amendment_url = soup_helper.get_link_using_regex_id(soup, 'hlIncorpTo')
            if amendment_url:
                completed_template['amendment_id'] = amendment_url.split('/')[-1]

        for column in columns:
            completed_template[column] = columns[column]
        
        ordered_template = order_columns(completed_template, get_series_column_order())
        return ordered_template
    else:
        return completed_template


def get_template(metadata_type: str) -> list:
    if metadata_type == 'series_pane':
        return get_series_pane_metadata_template()
    elif metadata_type == 'series_table':
        return get_series_table_metadata_template()
    else:
        return []


def get_series_pane_metadata_template() -> list:
    template = [
        {
            'name': 'title',
            'element': 'h2',
            'class': 'wraptext'
        },
        {
            'name': 'notation',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblSeriesNotations'
        },
        {
            'name': 'admin_departments',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblAdminDepts'
        },
        {
            'name': 'details',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblDetails'
        },
        {
            'name': 'commence_label',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblCommences'
        },
        {
            'name': 'commence_date_formatted',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblCommencesDate'
        },
        {
            'name': 'repealed_label',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblRepealedFieldLabel'
        },
        {
            'name': 'repealed_date_formatted',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblRepealed'
        },
        {
            'name': 'repeal_reason',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblRepealingReason'
        },
        {
            'name': 'ceased_label',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblCeasedFieldLabel'
        },
        {
            'name': 'ceased_datetime_formatted',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblCeased'
        },
        {
            'name': 'ceasing_reason',
            'element': 'span',
            'id': 'MainContent_SeriesPane_lblCeasingReason'
        }
    ]

    return template


def get_series_table_metadata_template() -> list:
    template = [
        {
            'name': 'document_status',
            'element': 'span',
            'id_like': 'lblTitleStatus'
        },
        {
            'name': 'incorporated_amendments',
            'element': 'span',
            'id_like': 'lblIncorpTo'
        },
        {
            'name': 'incorporated_amendments_linked',
            'element': 'a',
            'id_like': 'hlIncorpTo'
        }
    ]

    return template


def get_series_column_names() -> list:
    column_names = [
        'registered_date',
        'register_id',
        'comp_no',
        'start_date',
        'end_date'
    ]

    return column_names


def get_series_column_order() -> list:
    columns_in_order = [
        'register_id',
        'document_status',
        'registered_date',
        'comp_no',
        'start_date',
        'end_date',
        'incorporated_amendments',
        'amendment_id'
    ]

    return columns_in_order


def fill_out_template(item: str, template: list) -> dict:
    soup = soup_helper.get_soup_from_text(item)
    record = {}

    for field in template:
        if field.get('id'):
            field_text = soup_helper.get_text_using_exact_id(soup, field['element'], field['id'])
        elif field.get('id_like'):
            field_text = soup_helper.get_text_using_regex_id(soup, field['element'], field['id_like'])
        elif field.get('class'):
            field_text = soup_helper.get_text_by_class(soup, field['element'], field['class'])
        else:
            field_text = soup_helper.get_element_text(soup, field['element'])

        if field_text:
            record[field['name']] = common.remove_whitespace(field_text)
    
    return record


def order_columns(original_record: dict, column_order: list) -> dict:
    ordered_record = {}

    for column in column_order:
        if original_record.get(column):
            if str(column).endswith('_date'):
                ordered_record[column] = common.standardise_date(original_record[column])
            else:
                ordered_record[column] = original_record[column]
        else:
            ordered_record[column] = ''

    return ordered_record