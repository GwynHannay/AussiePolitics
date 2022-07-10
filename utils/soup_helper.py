import re
from utils import common
from bs4 import BeautifulSoup
from urllib.request import urlopen


def get_soup(url: str):
    response = urlopen(url)
    soup = BeautifulSoup(response, "html.parser")
    return soup


def get_soup_elements(soup, elements: dict):
    results = []
    attributes = []
    
    if elements.get('class'):
        results = soup.find_all(elements['type'], class_=elements['class'])
    elif elements.get('value'):
        results = soup.find_all(elements['type'], value=elements['value'])
    
    for result in results:
        attributes.append(result[elements['attribute']])
    
    return attributes


def get_series_id(soup):
    series_details = soup.find_all('input', value='View Series')
    series_id = ''

    for button in series_details:
        series_id = re.findall(r'/Series/([A-Za-z0-9]*)"', str(button))[0]
    
    return series_id


def get_series_metadata(soup, series_id):
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
            document[header] = '09 Jul 1900' # TODO: Update this
        else:
            document[header] = ''
    metadata.append(document)

    return metadata


def get_document_metadata(soup, document_metadata):
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
        document_metadata['Admin Department'] = common.remove_whitespace(admin_department.text)
    else:
        document_metadata['Admin Department'] = ''
    
    comments = soup.find('tr', id=re.compile('trComments'))
    if comments:
        document_metadata['Comments'] = common.remove_whitespace(comments.text)
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
            formatted_date = common.standardise_date(document_metadata[field])
            document_metadata[field] = formatted_date
    
    return document_metadata