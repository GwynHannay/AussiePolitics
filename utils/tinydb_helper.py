from tinydb import TinyDB, where
from tinydb.operations import add, set

db = TinyDB('docs/db.json')

def insert_record(record: dict):
    db.insert(record)


def update_record(record: dict):
    db.update(record, where('series_id') == record['series_id'])


def update_list(records: list, series_id: str):
    db.update(set('documents', records), where('series_id') == series_id) # type: ignore


def add_to_record(records: list, series_id: str):
    db.update(add('documents', records), where('series_id') == series_id) # type: ignore


def fetch_index_records(section: str) -> list:
    return db.search((where('stage') == 'index') & (where('section') == section))  # type: ignore


def fetch_series_records(section: str) -> list:
    return db.search((where('stage') == 'series') & (where('section') == section))  # type: ignore


def fetch_series_record_by_id(series_id: str) -> list:
    return db.search(where('series_id') == series_id) # type: ignore