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

@app.route("/sensor/<int:sensor_id>")
def get_sensor(sensor_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get the latest 10 values
        cur.execute("""
            SELECT value, created_at
            FROM sensores
            WHERE sensor_id = %s
            ORDER BY created_at DESC
            LIMIT 10;
        """, (sensor_id,))
        rows = cur.fetchall()

        # Convert to lists for graph
        values = [r[0] for r in rows][::-1]        # reverse for chronological order
        timestamps = [r[1].strftime('%Y-%m-%d %H:%M:%S') for r in rows][::-1]
        
        return render_template("sensor.html", sensor_id=sensor_id, values=values, timestamps=timestamps, rows=rows)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"

    finally:
        if 'conn' in locals():
            conn.close()

@app.route("/hello")
def hello():
    return render_template("hello.html", user="Alvaro")

@app.route("/dashboard")
def dashboard():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener todos los IDs
        cur.execute("SELECT DISTINCT sensor_id FROM sensores ORDER BY sensor_id;")
        device_ids = [row[0] for row in cur.fetchall()]

        # ID seleccionado
        selected_raw = request.args.get("device", default=None)
        selected_id = selected_raw  # puede ser numero o "all"


        rows = []
        timestamps = []
        values = []
        last_update = None

        # todos
        if selected_id == "all":
                    cur.execute("""
                        SELECT sensor_id, value, created_at
                        FROM sensores
                        ORDER BY created_at DESC
                        LIMIT 100;
                    """)

            data = cur.fetchall()

            # Redondear
            rows = [(sid, round(val, 2), t) for sid, val, t in data]

            values = [val for _, val, _ in rows][::-1]
            timestamps = [t.strftime('%Y-%m-%d %H:%M:%S') for _, _, t in rows][::-1]

            return render_template(
                "dashboard.html",
                device_ids=device_ids,
                selected_id="all",
                rows=rows,
                values=values,
                timestamps=timestamps,
                last_update=None
            )

        # 1 sensor
        if selected_id is not None:
            try:
                selected_id_int = int(selected_id)
            except:
                selected_id_int = None

            if selected_id_int is not None:
                cur.execute("""
                    SELECT value, created_at
                    FROM sensores
                    WHERE sensor_id = %s
                    ORDER BY created_at DESC
                    LIMIT 10;
                """, (selected_id_int,))

                data = cur.fetchall()

                rows = [(round(val, 2), t) for val, t in data]

                if rows:
                    values = [v for v, _ in rows][::-1]
                    timestamps = [t.strftime('%Y-%m-%d %H:%M:%S') for _, t in rows][::-1]
                    last_update = rows[0][1]

        return render_template(
            "dashboard.html",
            device_ids=device_ids,
            selected_id=selected_id,
            rows=rows,
            values=values,
            timestamps=timestamps,
            last_update=last_update
        )

    except Exception as e:
        return f"Error: {e}"

    finally:
        if 'conn' in locals():
            conn.close()
