import matplotlib.pyplot as plt
import psycopg2
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db")

def fetch_data():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT drone_id, battery_level FROM drone_data WHERE timestamp > NOW() - INTERVAL '1 hour'")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def plot_battery_levels(data):
    drone_ids = [row[0] for row in data]
    battery_levels = [row[1] for row in data]
    plt.figure(figsize=(10, 6))
    plt.bar(drone_ids, battery_levels, color='skyblue')
    plt.xlabel('Drone ID')
    plt.ylabel('Battery Level (%)')
    plt.title('Battery Levels of Drones in the Last Hour')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('/app/battery_levels.png')
    plt.close()

if __name__ == "__main__":
    data = fetch_data()
    plot_battery_levels(data)
    print("Battery levels plot generated.")
