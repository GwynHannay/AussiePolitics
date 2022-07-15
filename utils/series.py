from utils import common, soup_helper, tinydb_helper


def get_indexes(section: str, crawl_config: dict):
    sections = section.split('.')
    if len(sections) > 1:
        landing_page_link = common.build_url_from_config(crawl_config, type='index', subsection=sections[1])
    else:
        landing_page_link = common.build_url_from_config(crawl_config, type='index')

    landing_page_contents = soup_helper.get_soup_from_url(landing_page_link)

    raw_links = soup_helper.get_index_title_link(landing_page_contents)
    index_urls = []
    for link in raw_links:
        index_urls.append(common.build_url(landing_page_link, link))
    
    return index_urls


def process_index(item: dict):
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


def get_series(crawl_config: dict):
    pass