from tinydb import TinyDB, where

db = TinyDB('docs/db.json')

def insert_record(record: dict):
    db.insert(record)


def fetch_index_records(section: str):
    return db.search((where('stage') == 'index') & (where('section') == section))