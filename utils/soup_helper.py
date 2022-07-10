import re
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