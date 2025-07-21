# imports
import obd
import time
import json
from datetime import datetime
from flask import Flask, send_file, jsonify
import threading
import os

# Flask server setup
app = Flask(__name__)
log_file = "/home/pi/obd_data.json"  # Path to JSON file

@app.route("/")
def home():
    return "OBD-II Fuel Tracker Server is running."

@app.route("/obd-data", methods=["GET"])
def get_obd_data():
    if os.path.exists(log_file):
        return send_file(log_file, mimetype="application/json")
    else:
        return jsonify({"error": "Data file not found."}), 404

# Function to run OBD logging in a background thread
def obd_logger():
    print("Connecting to OBD-II...")
    connection = obd.OBD()

    if not connection.is_connected():
        print("Failed to connect to OBD-II adapter.")
        return

    print("Connected.")

    cmd_speed = obd.commands.SPEED         # km/h
    cmd_fuel_rate = obd.commands.FUEL_RATE # L/h

    total_distance_km = 0
    total_fuel_liters = 0
    interval = 1  # seconds

    try:
        while True:
            speed_resp = connection.query(cmd_speed)
            fuel_resp = connection.query(cmd_fuel_rate)

            if speed_resp.value is not None and fuel_resp.value is not None:
                speed = speed_resp.value.to("km/h").magnitude
                fuel_rate = fuel_resp.value.to("L/h").magnitude

                distance_this_tick = speed / 3600
                fuel_this_tick = fuel_rate / 3600

                total_distance_km += distance_this_tick
                total_fuel_liters += fuel_this_tick

                fuel_efficiency = (total_fuel_liters / total_distance_km) * 100 if total_distance_km > 0 else None

                print(f"Speed: {speed:.2f} km/h | Fuel Rate: {fuel_rate:.2f} L/h | L/100km: {fuel_efficiency:.2f}")

                data = {
                    "timestamp": datetime.now().isoformat(),
                    "speed_kph": speed,
                    "fuel_rate_lph": fuel_rate,
                    "total_distance_km": total_distance_km,
                    "total_fuel_liters": total_fuel_liters,
                    "fuel_efficiency_l_per_100km": fuel_efficiency
                }

                with open(log_file, "w") as f:
                    json.dump(data, f, indent=4)
            else:
                print("Waiting for valid OBD-II response...")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("Stopped logging.")

# Start OBD logger in a separate thread
logger_thread = threading.Thread(target=obd_logger)
logger_thread.daemon = True
logger_thread.start()

# Start Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
