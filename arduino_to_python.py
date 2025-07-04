import serial
import time
import csv

# ---- CONFIGURE THIS ----
SERIAL_PORT = 'COM3'  # Replace with your port, e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux/Mac
BAUD_RATE = 115200
OUTPUT_FILE = 'arduino_data.csv'
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
            line = ser.readline().decode('utf-8').strip()
            timestamp = time.time()
            print(f"{timestamp}, {line}")
            data.append([timestamp, line])
    
    except KeyboardInterrupt:
        print("\nInterrupted. Saving data...")

        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'analog_value'])
            writer.writerows(data)

        print(f"Data saved to {OUTPUT_FILE}")

    finally:
        ser.close()
        print("Serial connection closed.")

if __name__ == '__main__':
    main()
