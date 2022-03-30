import json
import lxml.html
import requests
import sqlite3


candidate_url = 'https://www.abc.net.au/news/elections/federal/2022/guide/candidates'
debug = True

if debug:
    db_file = 'auspol.db'


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, isolation_level=None)
    except Exception as e:
        msg = 'Trouble creating database: {}. Error: {}'.format(db_file, e)
        raise Exception(msg)
    
    query = (
        "SELECT name FROM sqlite_master WHERE type = 'table';"
    )

    results = conn.execute(query)

    tables = results.fetchall()

    if tables:
        for table in tables:
            print(table)
    else:
        table_create = """
            CREATE TABLE IF NOT EXISTS candidates (
                id integer PRIMARY KEY,
                given_name text,
                family_name text,
                party text,
                electorate text,
                status text
            );
        """

        conn.execute(table_create)
        conn.commit()
    
    return conn


def get_candidates():
    req = requests.get(candidate_url)

    if req.status_code != 200:
        msg = 'Trouble accessing candidates list: {}'.format(candidate_url)
        raise Exception(msg)
    
    doc = lxml.html.fromstring(req.content)

    candidate_tables = doc.xpath('//table[@id="candidatestable"]')
    rows = []

    for table in candidate_tables:
        for row in table[1].xpath('.//tr'):
            rows.append(row)

        hrow = table[0].xpath('.//th')

        if (
            hrow[0].text_content() == 'Candidate'
        ):
            pass
        else:
            msg = 'Could not find candidate table'
            raise Exception(msg)
        
        if len(rows) < 1:
            msg = 'No rows found for candidates'
            raise Exception(msg)
    
    return rows


def process_candidates(candidates):
    dbconn = create_connection('auspol.db')
    all_candidates = []

    for row in candidates:
        candidate = {}
        candidate['given_name'] = row.xpath('.//td[@class="candidate"]')[0].text.strip()
        candidate['family_name'] = row.xpath('.//td[@class="candidate"]//span[@class="familyname"]')[0].text
        statuses = row.xpath('.//td[@class="candidate"]//span[contains(@class, "pty")]')

        if len(statuses) > 0:
            candidate['status'] = statuses[0].text
        
        candidate['party'] = row.xpath('.//td[contains(@class, "party")]//span')[0].text
        candidate['electorate'] = row.xpath('.//td[@class="electorate"]/a')[0].text

        query = """
            SELECT count(id), coalesce(id, 0)
            FROM candidates
            WHERE given_name = ?
                AND family_name = ?
                AND party = ?
                AND electorate = ?;
        """

        args = (candidate['given_name'], candidate['family_name'], candidate['party'], candidate['electorate'])
        result = dbconn.execute(query, args)

        id = result.fetchone()
        if id[0] > 0:
            candidate['id'] = id[1]
        else:
            candidate['id'] = None
        
        all_candidates.append(candidate)
    
    return all_candidates
        