"""
Run the API to manage data CRUD requests

Use via `python3 app.py` or `flask run`
"""

import json
import logging
import os
import requests
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(filename='flask_app.log', level=logging.DEBUG)

MYSQL_DATABASE=os.environ.get('MYSQL_DATABASE', 'mydatabase')
MYSQL_USER=os.environ.get('MYSQL_USER', 'myuser')
MYSQL_PASSWORD=os.environ.get('MYSQL_PASSWORD', 'insecure')

table_agencies='agencies'

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DATABASE
}

INIT_AGENCIES_URL="https://www.ecfr.gov/api/admin/v1/agencies.json"

SUPPLY_INIT_DATA=True

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def _get_init_agency_data():
    try:
        response = requests.get(INIT_AGENCIES_URL)
        response.raise_for_status()
        data = response.json()

        return data['agencies']
    except Exception as e:
        print(f"Error getting initial player data: {e}")
        raise e

def _clean_field(value):
    return value if value is not None else ''

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

        if supply_init_data:
            query_check_empty = f"SELECT COUNT(*) FROM {table_agencies}"
            cursor.execute(query_check_empty)
            result = cursor.fetchone()

            # Only insert data during init if no data present
            if result[0] == 0:
                # Get agency data
                agencies = _get_init_agency_data()

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
