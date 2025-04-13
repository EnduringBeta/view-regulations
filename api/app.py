"""
Run the API to manage data CRUD requests

Use via `python3 app.py` or `flask run`
"""

import os
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

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

SUPPLY_INIT_DATA=True

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

init_agencies = []

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
            type VARCHAR(255) NOT NULL
        )"""
        cursor.execute(query_agencies)

        if supply_init_data:
            query_check_empty = f"SELECT COUNT(*) FROM {table_agencies}"
            cursor.execute(query_check_empty)
            result = cursor.fetchone()

            # Only insert data during init if no data present
            if result[0] == 0:
                query_add_agencies = f"INSERT INTO {table_agencies} (name, type) VALUES (%s, %s)"
                agencies_data = [(agency['name'], agency['type']) for agency in init_agencies]
                cursor.executemany(query_add_agencies, agencies_data)
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

@app.post("/agencies")
def add_agency():
    if request.is_json:
        agency = request.get_json()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"INSERT INTO {table_agencies} (name, type) VALUES (%s, %s)"
            agency_data = (agency['name'], agency['type'])
            cursor.execute(query, agency_data)
            conn.commit()
            conn.close()

            # Agency added
            return jsonify({'message': 'Agency added successfully!'}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 415

@app.route("/agencies", methods=["PUT"])
def update_agency():
    if request.is_json:
        agency = request.get_json()
        a_id = agency.get('id')
        a_name = agency.get('name')
        a_type = agency.get('type')

        if not a_id or not a_name or not a_type:
            return jsonify({"error": "Missing fields"}), 400

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"UPDATE {table_agencies} SET name = %s, type = %s WHERE id = %s"
            agency_data = (a_name, a_type, a_id)
            cursor.execute(query, agency_data)
            conn.commit()
            conn.close()

            # No data found/changed
            if cursor.rowcount == 0:
                return jsonify({"error": "Agency not found"}), 404

            # Agency updated
            return jsonify({"message": "Agency updated successfully!"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 415

@app.route("/agencies/<int:agency_id>", methods=["DELETE"])
def delete_agency(agency_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM {table_agencies} WHERE id = %s"
        cursor.execute(query, (agency_id,))
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Agency not found"}), 404

        # Agency removed
        return jsonify({"message": "Agency deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
