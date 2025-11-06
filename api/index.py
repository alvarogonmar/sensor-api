from flask import Flask

app = Flask(__name__)

CONNECTION_STRING = os.getenv("CONN_STRING")

def get_connection():
    return psycop2.connect(CONNECTION_STRING)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/sensor')
def sensor():
    try:
        connection = get_connection()
        print("Connection successfull!")

        # Create a cursor to execute SQL
        cursor = connection.cursor()
