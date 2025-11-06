import os
import psycopg2
from flask import Flask,request, jsonify, render_template
from dotenv import load_dotenv

# Load enviroment variables from .env
load_dotenv()

app = Flask(__name__)

# Get connection string from environment variable
CONNECTION_STRING = os.getenv("CONN_STRING")

def get_connection():
    return psycopg2.connect(CONNECTION_STRING)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About Page'

@app.route('/sensor')
def sensor():
    try:
        # Connect to the database
        connection = get_connection()
        print("Connection successfull!")
        
        cursor = connection.cursor()

        #Example query
        cursor.execute("SELECT NOW();")  # simple query to test connection
        result = cursor.fetchone()
        print("Current Time: ", result)

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return f"Current time: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/sensor/<int:sensor_id>", methods=["POST"])
def insert_sensor_value(sensor_id):
    value = request.args.get("value", type=float)
    if value is None:
        return jsonify({"error": "Missing 'value' query parameter"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Insert into sensors table
        cur.execute(
            "INSERT INTO sensores (sensor_id, value) VALUES (%s, %s)",
            (sensor_id, value)
        )
        conn.commit()

        return jsonify({
            "message": "Sensor value inserted successfully",
            "sensor_id": sensor_id,
            "value": value
        }), 201

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'conn' in locals():
            conn.close()
