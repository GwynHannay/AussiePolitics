import logging
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen


logger = logging.getLogger(__name__)


def get_soup_from_url(url: str) -> BeautifulSoup:
    """Receives a URL and returns a BeautifulSoup object from that web page.

    Args:
        url (str): URL to be scraped.

    Returns:
        BeautifulSoup: Parsed HTML from the provided URL.
    """
    response = urlopen(url)
    soup = BeautifulSoup(response, "html.parser")
    return soup


def get_soup_from_text(text: str) -> BeautifulSoup:
    """Receives a string of HTML and returns a BeautifulSoup object from it.

    Args:
        text (str): HTML as a string.

    Returns:
        BeautifulSoup: Parsed HTML from the provided string.
    """
    soup = BeautifulSoup(text, "html.parser")
    return soup


# TODO: Make this generic for any class of a href
def get_index_title_link(soup: BeautifulSoup) -> list:
    results = soup.find_all('a', class_='TitleLetter')
    attributes = []

    for result in results:
        attributes.append(result['href'])

    return attributes


def get_link_by_class(soup: BeautifulSoup, class_name: str) -> list:
    results = soup.find_all('a', class_=class_name)
    attributes = []

    for result in results:
        attributes.append(result['href'])

    return attributes


def get_text_by_class(soup: BeautifulSoup, element: str, class_name: str) -> str | None:
    item = soup.find(element, class_=class_name)
    if item:
        return item.text
    else:
        return None


def get_link_using_regex_id(soup: BeautifulSoup, id: str) -> str | None:
    link = soup.find('a', id=re.compile(id))

    if link:
        return link['href']
    else:
        return None


def get_element_text(soup: BeautifulSoup, element: str) -> str | None:
    item = soup.find(element)
    if item:
        return item.text
    else:
        return None


def get_text_using_exact_id(soup: BeautifulSoup, element: str, id: str) -> str | None:
    """Generic function that receives a BeautifulSoup object, an element type, and the
    element's ID, then returns either the text of that element, or None if it was not
    found.

    Args:
        soup (BeautifulSoup): Parsed HTML to search.
        element (str): Name of the element we are finding, e.g. 'span', 'tr'.
        id (str): ID of that element.

    Returns:
        str | None: Text from the element, or nothing if the element matching that ID
            wasn't found.
    """
    item = soup.find(element, id=id)
    if item:
        return item.text
    else:
        return None


def get_text_using_regex_id(soup: BeautifulSoup, element: str, id: str) -> str | None:
    item = soup.find(element, id=re.compile(id))
    if item:
        return item.text
    else:
        return None


def get_series_ids_from_buttons(soup: BeautifulSoup) -> list:
    series_details = soup.find_all('input', value='View Series')
    series_ids = []

    for button in series_details:
        series_id = re.findall(r'/Series/([A-Za-z0-9]*)"', str(button))[0]
        series_ids.append(series_id)

    return series_ids


def iterate_over_series_columns(soup: BeautifulSoup, metadata: dict):
    column_names = metadata['untitled_column_names']
    series_table = soup.find('div', _class=metadata['div_class'])
    # Extract the div class content
    document = {}
    i = 0
    if series_table:
        for column in series_table.tr.findChildren('td', recursive=False):
            if column.find('table'):
                continue

            document[column_names[i]] = column.text.strip()
            
            if column_names[i] == column_names[-1]:
                break
            
            i = i + 1
    
    return document
