import os
import psycopg2
from flask import Flask

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
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")  # simple query to test connection
        result = cursor.fetchone()

        # Clean up
        cursor.close()
        connection.close()

        return f"Connection successful! Server time: {result[0]}"
    except Exception as e:
        return f"Error: {str(e)}"
