from flask import Flask, jsonify, send_file
import os
import psycopg2
import json

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL",
                         "postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/server/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT drone_id, position, battery_level FROM drone_data ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    data = [{"drone_id": row[0], "position": row[1], "battery_level": row[2]} for row in rows]
    return jsonify(data), 200


@app.route('/server/visualization', methods=['GET'])
def get_visualization():
    # Zakładając, że visualization.py generuje wykres i zapisuje go jako battery_levels.png
    return send_file('/app/battery_levels.png', mimetype='image/png')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
