import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlopen


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
    print(metadata)