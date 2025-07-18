import obd
import sqlite3
import time
from datetime import datetime

# Connect to OBD-II over Bluetooth
connection = obd.OBD("/dev/rfcomm0")  # force use of Bluetooth port

# Connect to or create a local SQLite database
conn = sqlite3.connect('car_data.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS car_log (
    timestamp TEXT,
    speed REAL,
    rpm REAL,
    coolant_temp REAL
)
''')
conn.commit()

# Main loop to log car data every 2 seconds
try:
    while True:
        speed = connection.query(obd.commands.SPEED)
        rpm = connection.query(obd.commands.RPM)
        temp = connection.query(obd.commands.COOLANT_TEMP)

        if speed and rpm and temp:
            speed_val = speed.value.magnitude if speed.value else None
            rpm_val = rpm.value.magnitude if rpm.value else None
            temp_val = temp.value.magnitude if temp.value else None

            print(f"[{datetime.now()}] Speed: {speed_val} km/h, RPM: {rpm_val}, Temp: {temp_val} °C")

            cursor.execute("INSERT INTO car_log VALUES (?, ?, ?, ?)",
                           (datetime.now(), speed_val, rpm_val, temp_val))
            conn.commit()

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping...")
    connection.close()
    conn.close()
    print("Logging stopped by user.")
finally:
    connection.close()
    print("Connection closed.")