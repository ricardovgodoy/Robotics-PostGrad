import serial
import time
import csv

# ---- CONFIGURE THIS ----
SERIAL_PORT = 'COM3'      # e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux/Mac
BAUD_RATE    = 115200
OUTPUT_FILE  = 'arduino_data.csv'
# ------------------------

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    data = []

    try:
        # Give the Arduino a moment to reset
        time.sleep(2)
        print("Reading... Press Ctrl+C to stop and save.")

        while True:
            raw = ser.readline().decode('utf-8').strip()
            try:
                analog = int(raw)
            except ValueError:
                # Skip any non-numeric lines
                print("Non-numeric data, skipping:", repr(raw))
                continue

            # Timestamp in integer milliseconds
            ts_ms = int(time.time() * 1000)

            # Print with semicolon so you can also copy/paste easily
            print(f"{ts_ms};{analog}")
            data.append([ts_ms, analog])

    except KeyboardInterrupt:
        print("\nInterrupted. Saving data...")

        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['timestamp_ms', 'analog_value'])
            writer.writerows(data)

        print(f"Data saved to {OUTPUT_FILE}")

    finally:
        ser.close()
        print("Serial connection closed.")

if __name__ == '__main__':
    main()
