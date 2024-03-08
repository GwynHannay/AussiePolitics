import logging
import src.config
from tinydb import TinyDB, Query, where
from tinydb.operations import add, set


logger = logging.getLogger(__name__)

db = TinyDB('docs/db.json')
Series = Query()
Docs = Query()


def insert_record(record: dict):
    db.insert(record)


def update_record(record: dict):
    db.update(record, where('series_id') == record['series_id'])


def update_list(records: list, series_id: str):
    db.update(set('documents', records), where(
        'series_id') == series_id)  # type: ignore


def add_to_record(records: list, series_id: str):
    db.update(
        add('documents', records),
        where('series_id') == series_id  # type: ignore
    )


def get_records_by_current_stage() -> list:
    return db.search(
        (where('stage') == src.config.current_stage) &
        (where('section') == src.config.current_section)  # type: ignore
    )


def get_record_by_series_id(series_id: str) -> dict:
    return db.search(where('series_id') == series_id)[0]  # type: ignore


def get_record_by_document_id(document_id: str):
    return db.search(
        Series['documents'].any(
            Docs['register_id'] == document_id
        )  # type: ignore
    )
