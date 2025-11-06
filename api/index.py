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
