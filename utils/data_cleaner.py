from datetime import datetime
from dateutil.parser import parse

def remove_whitespace(text):
    clean_text = " ".join(text.split())
    return clean_text


def standardise_date(date_field):
    parsed_date = parse(date_field)
    formatted_date = ''

    if isinstance(parsed_date, datetime):
        formatted_date = datetime.strftime(parsed_date, '%d %b %Y')
    
    return formatted_date