import obd
import time
import csv

# Try connecting to the OBD-II adapter (auto-detect)
print("Connecting to OBD-II adapter...")
connection = obd.OBD()  # for USB or Bluetooth (must be paired)

# Confirm connection
if not connection.is_connected():
    print("Failed to connect to OBD-II adapter.")
    exit()

print("Connected to vehicle.")

# OBD commands to read
commands = {
    "speed": obd.commands.SPEED,                # Vehicle speed
    "rpm": obd.commands.RPM,                    # Engine RPM
    "fuel": obd.commands.FUEL_LEVEL             # Fuel level (%)
}

# Open CSV file to log data
filename = "drive_log.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Speed (km/h)", "RPM", "Fuel Level (%)", "Feedback"])

    print("Logging started. Press Ctrl+C to stop.")

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # Query each command
            speed_resp = connection.query(commands["speed"])
            rpm_resp = connection.query(commands["rpm"])
            fuel_resp = connection.query(commands["fuel"])

            # Extract values or set to None
            speed = speed_resp.value.to("kph").magnitude if speed_resp.value else None
            rpm = rpm_resp.value.magnitude if rpm_resp.value else None
            fuel = fuel_resp.value.magnitude if fuel_resp.value else None

            # Generate simple eco-driving feedback
            feedback = ""
            if speed and speed > 110:
                feedback = "⚠️ Slow down to reduce emissions"
            elif rpm and rpm > 3000:
                feedback = "⚠️ High RPM — accelerate more smoothly"
            else:
                feedback = "✅ Eco-driving"

            # Write row to CSV
            writer.writerow([timestamp, speed, rpm, fuel, feedback])

            # Print to console
            print(f"[{timestamp}] Speed: {speed} km/h | RPM: {rpm} | Fuel: {fuel}% | {feedback}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
        print(f"Data saved to {filename}")