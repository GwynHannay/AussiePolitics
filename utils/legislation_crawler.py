import re
import os
import utils.data_cleaner as dc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve


federal_register_url = 'https://www.legislation.gov.au'

register_sections = [
    'ByTitle/Constitution/InForce'
    # 'ByTitle/Acts',
    # 'ByTitle/LegislativeInstruments',
    # 'ByTitle/NotifiableInstruments',
    # 'ByTitle/Gazettes',
    # 'ByTitle/Bills',
    # 'ByRegDate/AdministrativeArrangementsOrders',
    # 'ByTitle/NorfolkIslandLegislation',
    # 'ByTitle/PrerogativeInstruments'
]


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
    scrape_url = build_scrape_url(federal_register_url, register_sections[0], type='index')
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
    i = 0
    for header in headings:
        if i == 0:
            document[header] = ''.join([title, ' [Principal]'])
        elif header == 'RegisterId':
            document[header] = series_id
        else:
            document[header] = ''
        i = i + 1
    metadata.append(document)

    return metadata


def get_download_details(document_metadata):
    download_page_url = build_scrape_url(federal_register_url, document_metadata['RegisterId'], type='download')
    soup = get_soup(download_page_url)

    title_status = soup.find('span', id=re.compile('lblTitleStatus'))
    if title_status:
        document_metadata['Title Status'] = title_status.text
    
    details = soup.find('span', id=re.compile('lblDetail'))
    if details:
        document_metadata['Details'] = details.text
    
    description = soup.find('span', id=re.compile('lblBD'))
    if description:
        document_metadata['Description'] = description.text
    admin_department = soup.find('span', id=re.compile('lblAdminDept'))
    if admin_department:
        document_metadata['Admin Department'] = dc.remove_whitespace(admin_department.text)
    
    comments = soup.find('tr', id=re.compile('trComments'))
    if comments:
        document_metadata['Comments'] = dc.remove_whitespace(comments.text)
    
    registered = soup.find('input', id=re.compile('hdnPublished'))
    if registered:
        document_metadata['Registered Datetime'] = registered['value']
    
    start_date = soup.find('span', id=re.compile('lblStartDate$'))
    if start_date:
        document_metadata['Start Date'] = start_date.text
    
    end_date = soup.find('span', id=re.compile('lblEndDate$'))
    if end_date:
        document_metadata['End Date'] = end_date.text
    
    download_link = soup.find('a', id=re.compile('hlPrimaryDoc'))
    if download_link:
        document_metadata['Download Link'] = download_link['href']
    
    return document_metadata


def download_file(document_metadata):
    download_link = document_metadata['Download Link']
    cache_filename = '.cache_constitution'
    _, headers = urlretrieve(download_link, cache_filename)
    content_disposition = headers.get('Content-Disposition')
    filename = re.findall(r'filename=([A-Za-z0-9]*\.docx)', content_disposition)
    content_type = headers.get('Content-Type')
    
    if filename and content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        with open(cache_filename, 'rb') as cached:
            file_content = cached.read()
            with open(filename[0], 'wb') as saved_file:
                saved_file.write(file_content)
        os.remove(cache_filename)