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

table_animals='animals'

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

init_animals = [
    {"name": "Lexi", "type": "hamster"},
    {"name": "Lorelei", "type": "hamster"},
    {"name": "Woo", "type": "hamster"},
    {"name": "Demi", "type": "dog"},
]

def _initialize_db(supply_init_data = False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create database if it doesn't exist
        query_database = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}"
        cursor.execute(query_database)
        conn.commit()

        # Create animals table if it doesn't exist
        query_animals = f"""CREATE TABLE IF NOT EXISTS {table_animals} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL
        )"""
        cursor.execute(query_animals)

        if supply_init_data:
            query_check_empty = f"SELECT COUNT(*) FROM {table_animals}"
            cursor.execute(query_check_empty)
            result = cursor.fetchone()

            # Only insert data during init if no data present
            if result[0] == 0:
                query_add_animals = f"INSERT INTO {table_animals} (name, type) VALUES (%s, %s)"
                animals_data = [(animal['name'], animal['type']) for animal in init_animals]
                cursor.executemany(query_add_animals, animals_data)
                print('Added initial animals!')

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
    return 'No animals here... Try "/animals" or port 3000!'

@app.get("/animals")
def get_animals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_animals}"
        cursor.execute(query)
        animals = cursor.fetchall()
        conn.close()

        # Return animals
        # Flask doesn’t automatically convert lists to JSON
        return jsonify(animals)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/animals/<int:animal_id>", methods=["GET"])
def get_animal(animal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_animals} WHERE id = %s"
        cursor.execute(query, (animal_id,))
        animal = cursor.fetchone()
        conn.close()

        if not animal:
            return jsonify({"error": "Animal not found"}), 404

        # Return animal
        return jsonify(animal), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/animals")
def add_animal():
    if request.is_json:
        animal = request.get_json()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"INSERT INTO {table_animals} (name, type) VALUES (%s, %s)"
            animal_data = (animal['name'], animal['type'])
            cursor.execute(query, animal_data)
            conn.commit()
            conn.close()

            # Animal added
            return jsonify({'message': 'Animal added successfully!'}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 415

@app.route("/animals", methods=["PUT"])
def update_animal():
    if request.is_json:
        animal = request.get_json()
        a_id = animal.get('id')
        a_name = animal.get('name')
        a_type = animal.get('type')

        if not a_id or not a_name or not a_type:
            return jsonify({"error": "Missing fields"}), 400

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"UPDATE {table_animals} SET name = %s, type = %s WHERE id = %s"
            animal_data = (a_name, a_type, a_id)
            cursor.execute(query, animal_data)
            conn.commit()
            conn.close()

            # No data found/changed
            if cursor.rowcount == 0:
                return jsonify({"error": "Animal not found"}), 404

            # Animal updated
            return jsonify({"message": "Animal updated successfully!"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 415

@app.route("/animals/<int:animal_id>", methods=["DELETE"])
def delete_animal(animal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM {table_animals} WHERE id = %s"
        cursor.execute(query, (animal_id,))
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Animal not found"}), 404

        # Animal removed
        return jsonify({"message": "Animal deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
