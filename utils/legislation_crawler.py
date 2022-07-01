import re
import json
import os
import utils.data_cleaner as dc
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve
from zoneinfo import ZoneInfo
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main(sections: list):
    full_config = load_config()
    crawl_config = read_config(full_config, sections)
    print(crawl_config)


def load_config():
    with open('config/legislation.json') as f:
        configs = json.loads(f.read())
        return configs


def read_config(config: dict, sections: list):
    relevant_config = {}
    relevant_config['common'] = config['common']
    for section in sections:
        relevant_config[section] = config[section]
    
    return relevant_config


federal_register_url = 'https://www.legislation.gov.au'

register_sections = {
    'Constitution' : 'ByTitle/Constitution/InForce',
    'Acts' : 'ByTitle/Acts/InForce/0/0/Principal',
    # 'ByTitle/LegislativeInstruments',
    # 'ByTitle/NotifiableInstruments',
    # 'ByTitle/Gazettes',
    # 'ByTitle/Bills',
    # 'ByRegDate/AdministrativeArrangementsOrders',
    # 'ByTitle/NorfolkIslandLegislation',
    # 'ByTitle/PrerogativeInstruments'
}

def run_scrapy(url):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'utils.legislation.settings')
    process = CrawlerProcess(get_project_settings())
    process.crawl('pages', url=url)
    process.start()


def get_url(document_type):
    return register_sections[document_type]


def build_scrape_url(base_url, url_part, type=None):
    match type:
        case None:
            return urljoin(base_url, url_part)
        case 'index':
            return urljoin(base_url, ''.join(['Browse/', url_part]))
        case 'series':
            return urljoin(base_url, ''.join(['Series/', url_part]))
        case 'download':
            return urljoin(base_url, ''.join(['Details/', url_part, '/Download']))


def get_soup(url):
    response = urlopen(url)
    soup = BeautifulSoup(response, "html.parser")
    return soup


def get_constitution():
    scrape_url = build_scrape_url(federal_register_url, get_url('Constitution'), type='index')
    soup = get_soup(scrape_url)
    series_details = soup.find_all('input', value='View Series')
    series_id = ''

    for button in series_details:
        series_id = re.findall(r'/Series/([A-Za-z0-9]*)"', str(button))[0]
    
    return series_id


def get_series(series_id):
    landing_url = build_scrape_url(federal_register_url, series_id, type='series')
    soup = get_soup(landing_url)

    metadata = []
    title = ''
    table_contents = soup.find_all('table', class_='rgMasterTable')
    
    headings = []
    for header in table_contents[0].thead.find_all('th', class_='rgHeader'):
        headings.append(header.text)
    
    for row in table_contents[0].tbody.findChildren('tr', recursive=False):
        document = {}
        i = 0
        for columns in row.findChildren('td', recursive=False):
            if columns.find('table'):
                title = columns.table.find('a').text
                status = columns.table.find('span', id=re.compile('lblTitleStatus')).text
                document[headings[i]] = ''.join([title, ' [', status, ']'])
            else:
                document[headings[i]] = columns.text.strip()
            i = i + 1
        metadata.append(document)
    
    document = {}
    for header in headings:
        if header == 'Title':
            document[header] = ''.join([title, ' [Principal]'])
        elif header == 'RegisterId':
            document[header] = series_id
        elif header == 'Comp No.':
            document[header] = '0'
        elif header == 'Start Date':
            document[header] = '09 Jul 1900'
        else:
            document[header] = ''
    metadata.append(document)

    return metadata


def get_download_details(document_metadata):
    download_page_url = build_scrape_url(federal_register_url, document_metadata['RegisterId'], type='download')
    soup = get_soup(download_page_url)

    title_status = soup.find('span', id=re.compile('lblTitleStatus'))
    if title_status:
        document_metadata['Title Status'] = title_status.text
    else:
        document_metadata['Title Status'] = ''
    
    details = soup.find('span', id=re.compile('lblDetail'))
    if details:
        document_metadata['Details'] = details.text
    else:
        document_metadata['Details'] = ''
    
    description = soup.find('span', id=re.compile('lblBD'))
    if description:
        document_metadata['Description'] = description.text
    else:
        document_metadata['Description'] = ''

    admin_department = soup.find('span', id=re.compile('lblAdminDept'))
    if admin_department:
        document_metadata['Admin Department'] = dc.remove_whitespace(admin_department.text)
    else:
        document_metadata['Admin Department'] = ''
    
    comments = soup.find('tr', id=re.compile('trComments'))
    if comments:
        document_metadata['Comments'] = dc.remove_whitespace(comments.text)
    else:
        document_metadata['Comments'] = ''
    
    registered = soup.find('input', id=re.compile('hdnPublished'))
    if registered:
        document_metadata['Registered Datetime'] = registered['value']
    else:
        document_metadata['Registered Datetime'] = ''
    
    start_date = soup.find('span', id=re.compile('lblStartDate$'))
    if start_date:
        document_metadata['Start Date'] = start_date.text
    
    end_date = soup.find('span', id=re.compile('lblEndDate$'))
    if end_date:
        document_metadata['End Date'] = end_date.text
    
    download_link = soup.find('a', id=re.compile('hlPrimaryDoc'))
    if download_link:
        document_metadata['Download Link'] = download_link['href']
    else:
        document_metadata['Download Link'] = ''
    
    date_fields = ['Registered', 'Start Date', 'End Date']
    for field in date_fields:
        if str(document_metadata[field]).strip(' '):
            formatted_date = dc.standardise_date(document_metadata[field])
            document_metadata[field] = formatted_date
    
    return document_metadata


def download_file(document_metadata, filepath='docs'):
    download_link = document_metadata['Download Link']
    cache_filename = '.cache_constitution'
    _, headers = urlretrieve(download_link, cache_filename)
    content_disposition = headers.get('Content-Disposition')
    filename = re.findall(r'filename=([A-Za-z0-9]*\.docx)', content_disposition)
    content_type = headers.get('Content-Type')
    
    if filename and content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        new_filename = filename[0]
        with open(cache_filename, 'rb') as cached:
            file_content = cached.read()
            with open(os.path.join(filepath, new_filename), 'wb') as saved_file:
                saved_file.write(file_content)
        os.remove(cache_filename)

        document_metadata['Filename'] = new_filename
        document_metadata['Last Download Date'] = datetime.now(tz=ZoneInfo("Australia/Perth")).strftime('%d %b %Y %H:%M AWST')
        
        with open(os.path.join(filepath, ''.join([str(document_metadata['RegisterId']), '.json'])), 'w') as metadata_file:
            json.dump(document_metadata, metadata_file, ensure_ascii=False, indent=4)
    
    return document_metadata