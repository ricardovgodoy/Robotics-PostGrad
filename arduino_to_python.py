import serial
import time
import csv
from collections import deque
import matplotlib.pyplot as plt

# ---- CONFIGURE THIS ----
SERIAL_PORT = 'COM8'     # e.g. 'COM3' on Windows or '/dev/ttyUSB0' on Linux/Mac
BAUD_RATE   = 115200
OUTPUT_FILE = 'arduino_data.csv'
MAX_POINTS  = 100        # how many points to show on the plot at once
# ------------------------

def main():
    # Open serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    
    # Prepare data storage
    data = []
    timestamps = deque(maxlen=MAX_POINTS)
    values     = deque(maxlen=MAX_POINTS)
    
    # Set up real‐time plot
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], '-o')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Analog Value')
    ax.set_title('Real-Time Signal from Arduino')

    start_time = time.time()
    
    try:
        time.sleep(2)  # let Arduino reset
        print("Reading... Press Ctrl+C to stop and save.")
        
        while True:
            raw = ser.readline().decode('utf-8').strip()
            now = time.time() - start_time
            
            try:
                val = float(raw)
            except ValueError:
                # skip lines that can't be parsed
                continue
            
            # Store datum
            data.append([now, val])
            timestamps.append(now)
            values.append(val)
            
            # Update plot data
            line.set_data(timestamps, values)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.01)
            
    except KeyboardInterrupt:
        print("\nInterrupted. Saving data...")
        
        # Save to CSV
        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'analog_value'])
            writer.writerows(data)
        print(f"Data saved to {OUTPUT_FILE}")
        
    finally:
        ser.close()
        plt.ioff()
        plt.show()
        print("Serial connection closed.")

if __name__ == '__main__':
    main()
