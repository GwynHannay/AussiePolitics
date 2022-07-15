from tinydb import TinyDB, Query

db = TinyDB('db.json')

def insert_record(record: dict):
    db.insert(record)