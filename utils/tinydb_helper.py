from tinydb import TinyDB, Query

db = TinyDB('docs/db.json')

def insert_record(record: dict):
    db.insert(record)