import re
import json
import os
from utils import series, scrapy_helper, soup_helper
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve
from zoneinfo import ZoneInfo


def main(sections: list):
    full_config = load_config()
    common_config = get_common_config(full_config)
    
    for section in sections:
        if section == 'constitution':
            crawl_config = full_config[section]
        else:
            crawl_config = full_config[section]['in_force']
        
        crawl_section(section, common_config, crawl_config)


def load_config():
    with open('config/legislation.json') as f:
        configs = json.loads(f.read())
        return configs


def read_config(config: dict, sections: list):
    relevant_config = {}
    for section in sections:
        relevant_config[section] = config[section]
    
    return relevant_config


def get_common_config(config: dict):
    return config['common']


def crawl_section(section: str, common_config: dict, crawl_config: dict):
    urls = series.main(section, common_config, crawl_config)
    scrapy_helper.run_scrapy(urls)


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