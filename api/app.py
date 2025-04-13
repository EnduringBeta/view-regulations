"""
Run the API to manage data CRUD requests

Use via `python3 app.py` or `flask run`
"""

import datetime
import json
import logging
import os
import requests
import mysql.connector
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(filename='flask_app.log', level=logging.DEBUG)

MYSQL_DATABASE=os.environ.get('MYSQL_DATABASE', 'mydatabase')
MYSQL_USER=os.environ.get('MYSQL_USER', 'myuser')
MYSQL_PASSWORD=os.environ.get('MYSQL_PASSWORD', 'insecure')

table_agencies='agencies'
table_regulations='regulations'

class RegulationFinder:
    def __init__(self, title, subtitle=None, chapter=None, subchapter=None, part=None, subpart=None):
        self.title = title
        self.subtitle = subtitle
        self.chapter = chapter
        self.subchapter = subchapter
        self.part = part
        self.subpart = subpart
        #self.section = section
        #self.appendix = appendix

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DATABASE
}

INIT_AGENCIES_URL="https://www.ecfr.gov/api/admin/v1/agencies.json"
INIT_REGULATIONS_URL_PREFIX="https://www.ecfr.gov/api/versioner/v1/full/"

SUPPLY_INIT_DATA=True

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def _clean_field(value):
    return value if value is not None else ''

# Feels a bit clunky to return a tuple when the data could be combined
def _get_agencies(conn, cursor):
    # Get agency data
    agencies = None

    try:
        response = requests.get(INIT_AGENCIES_URL)
        response.raise_for_status()
        data = response.json()

        agencies = data['agencies']
    except Exception as e:
        print(f"Error getting initial agency data: {e}")
        raise e

    if not agencies:
        print(f"Error getting initial agency data!")
        conn.commit()
        conn.close()
        return

    query_add_agencies = f"INSERT INTO {table_agencies} \
        (name, short_name, display_name, sortable_name, slug, cfr_references) \
        VALUES ({'%s, %s, %s, %s, %s, %s'})"

    # 1. Add top-level agencies
    agency_data = [
        (
            agency['name'],
            _clean_field(agency.get('short_name', '')),
            agency['display_name'],
            agency['sortable_name'],
            agency['slug'],
            json.dumps(agency['cfr_references']),
        )
        for agency in agencies
    ]
    #print(agency_data)

    cursor.executemany(query_add_agencies, agency_data)
    conn.commit()

    # Retrieve IDs for top-level agencies
    cursor.execute(f"SELECT id, slug FROM {table_agencies}")
    agency_id_map = {row[1]: row[0] for row in cursor.fetchall()}

    # 2. Add child agencies with reference to parent
    child_agencies = []
    for agency in agencies:
        if 'children' in agency:
            for child in agency['children']:
                child['parent_id'] = agency_id_map.get(agency['slug'])
                child_agencies.append(child)
    
    child_agency_data = [
        (
            child['name'],
            _clean_field(child.get('short_name', '')),
            child['display_name'],
            child['sortable_name'],
            child['slug'],
            json.dumps(child['cfr_references']),
            child['parent_id'],
        )
        for child in child_agencies
    ]
    query_add_child_agencies = f"INSERT INTO {table_agencies} \
        (name, short_name, display_name, sortable_name, slug, cfr_references, parent_id) \
        VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.executemany(query_add_child_agencies, child_agency_data)
    conn.commit()

    print('Added initial agencies!')

    agencies.append(child_agencies)
    return agencies, agency_id_map

# https://github.com/usgpo/bulk-data/blob/main/ECFR-XML-User-Guide.md
def _get_regulation_xml(reg_finder, date):
    if reg_finder.subchapter and not reg_finder.chapter:
        print(f"Cannot get regulation text with subchapter {reg_finder.subchapter} without chapter; ignoring...")
        return
    elif reg_finder.subpart and not reg_finder.part:
        print(f"Cannot get regulation text of subpart {reg_finder.subpart} without part; ignoring...")
        return

    # Assemble URL
    url = f"{INIT_REGULATIONS_URL_PREFIX}{date}/title-{reg_finder.title}.xml"
    if reg_finder.subtitle:
        url += f"?subtitle={reg_finder.subtitle}"
    if reg_finder.chapter:
        url += f"?chapter={reg_finder.chapter}"
        if reg_finder.subchapter:
            url += f"?subchapter={reg_finder.subchapter}"
    if reg_finder.part:
        url += f"?part={reg_finder.part}"
        if reg_finder.subpart:
            url += f"?subpart={reg_finder.subpart}"

    print(f"Getting regulation text: {reg_finder.title} {reg_finder.subtitle} {reg_finder.chapter} {reg_finder.subchapter} {reg_finder.part} {reg_finder.subpart}")

    # TODOROSS: error about size
    regulation_xml = None

    try:
        response = requests.get(url)
        response.raise_for_status()
        regulation_xml = ET.fromstring(response.content)
    except Exception as e:
        print(f"Error getting regulation text: {e}")
        raise e

    if regulation_xml is None:
        print(f"Error getting regulation text!")
        return
    
    return regulation_xml

def _count_regulation_words(regulation_xml):
    # Count words in the regulation text withing HEAD and P tags
    word_count = 0

    try:
        for e in regulation_xml.iter():
            if e.tag == 'HEAD' or e.tag == 'P':
                # Handle <I> internal tags, etc.
                full_text = ''.join(e.itertext())
                word_count += len(full_text.split())
    except Exception as e:
        print(f"Error counting words in regulation text: {e}")
        raise e

    return word_count

# Get regulation text for each agency's title, chapter, and part
# TODOROSS: check for duplicates
def _get_regulations(conn, cursor, agencies, agency_id_map, date):
    for agency in agencies:
        references = agency.get('cfr_references', [])
        if not references:
            continue
        for reference in references:
            reg_finder = RegulationFinder(
                reference.get('title'),
                reference.get('subtitle'),
                reference.get('chapter'),
                reference.get('subchapter'),
                reference.get('part'),
                reference.get('subpart')
            )
            regulation_xml = _get_regulation_xml(reg_finder, date)
            regulation_text = ET.tostring(regulation_xml, encoding='unicode')
            count = _count_regulation_words(regulation_xml)

            query_regulation = f"INSERT INTO {table_regulations} \
                (agency_id, title, subtitle, chapter, subchapter, \
                part, subpart, date, text, word_count) \
                VALUES ({'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s'})"
            
            agency_id = agency_id_map.get(agency['slug'])
            if not agency_id:
                print(f"Agency ID not found for slug {agency['slug']}")
                continue

            regulation_data = (
                agency_id,
                reg_finder.title,
                reg_finder.subtitle,
                reg_finder.chapter,
                reg_finder.subchapter,
                reg_finder.part,
                reg_finder.subpart,
                date,
                regulation_text,
                count
            )

            try:
                cursor.execute(query_regulation, regulation_data)
                conn.commit()
            except Exception as e:
                print(f"Error adding regulation data: {e}")
                raise e
    
    print('Added initial regulations!')
    return

def _initialize_db(supply_init_data = False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create database if it doesn't exist
        query_database = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}"
        cursor.execute(query_database)
        conn.commit()

        # Create agencies table if it doesn't exist
        query_agencies = f"""CREATE TABLE IF NOT EXISTS {table_agencies} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            short_name VARCHAR(255) NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            sortable_name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) NOT NULL,
            cfr_references JSON NOT NULL,
            parent_id INT
        )"""
        cursor.execute(query_agencies)

        # Create regulations table if it doesn't exist
        query_regulations = f"""CREATE TABLE IF NOT EXISTS {table_regulations} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agency_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            subtitle VARCHAR(255),
            chapter VARCHAR(255),
            subchapter VARCHAR(255),
            part VARCHAR(255),
            subpart VARCHAR(255),
            date DATE NOT NULL,
            text LONGTEXT NOT NULL,
            word_count INT NOT NULL
        )"""
        cursor.execute(query_regulations)

        if supply_init_data:
            query_check_empty = f"SELECT COUNT(*) FROM {table_agencies}"
            cursor.execute(query_check_empty)
            result = cursor.fetchone()

            # Only insert data during init if no data present
            if result[0] == 0:
                agencies, agency_id_map = _get_agencies(conn, cursor)

                date = datetime.datetime.now().strftime('%Y-01-01')
                _get_regulations(conn, cursor, agencies, agency_id_map, date)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

# Ensure database is initialized
with app.app_context():
    _initialize_db(SUPPLY_INIT_DATA)

@app.route('/')
def index():
    return 'No regulation data here... Try "/agencies" or port 3000!'

@app.get("/agencies")
def get_agencies():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_agencies}"
        cursor.execute(query)
        agencies = cursor.fetchall()
        conn.close()

        # Return agencies
        # Flask doesn’t automatically convert lists to JSON
        return jsonify(agencies)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/agencies/<int:agency_id>", methods=["GET"])
def get_agency(agency_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_agencies} WHERE id = %s"
        cursor.execute(query, (agency_id,))
        agency = cursor.fetchone()
        conn.close()

        if not agency:
            return jsonify({"error": "Agency not found"}), 404

        # Return agency
        return jsonify(agency), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
