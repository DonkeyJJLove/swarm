from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL",
                         "postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    drone_id = data.get('drone_id')
    position = data.get('position')
    battery_level = data.get('battery_level')
    if not all([drone_id, position, battery_level]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO drone_data (drone_id, position, battery_level) VALUES (%s, %s, %s)",
        (drone_id, json.dumps(position), battery_level)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success"}), 200


@app.route('/api/drones/<drone_id>/status', methods=['GET'])
def get_drone_status(drone_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT position, battery_level FROM drone_data WHERE drone_id = %s ORDER BY timestamp DESC LIMIT 1",
        (drone_id,)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return jsonify(
            {"drone_id": drone_id, "position": result['position'], "battery_level": result['battery_level']}), 200
    else:
        return jsonify({"error": "Drone not found"}), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6001)
