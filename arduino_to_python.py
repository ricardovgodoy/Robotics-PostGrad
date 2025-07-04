import serial
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# ---- CONFIGURE THIS ----
SERIAL_PORT = 'COM8'  # Replace with your port, e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux/Mac
BAUD_RATE = 115200
OUTPUT_FILE = 'arduino_data011.csv'
MAX_PLOT_POINTS = 100 # How many data points to display on the plot at once
# ------------------------

# Global variables for plotting
fig, ax = plt.subplots()
timestamps = deque(maxlen=MAX_PLOT_POINTS)
analog_values = deque(maxlen=MAX_PLOT_POINTS)

def animate(i, ser, all_data):
    """
    This function is called periodically by FuncAnimation.
    It reads a line from the serial port, parses it, and updates the plot.
    """
    try:
        # Read a line from the serial port (with a timeout)
        line = ser.readline().decode('utf-8').strip()
        
        # Proceed only if the line is not empty
        if line:
            # Assuming the line contains a single numeric value
            value = float(line)
            timestamp = time.time()
            
            # Append data to deques for plotting
            timestamps.append(timestamp)
            analog_values.append(value)
            
            # Append to the main list for saving all data
            all_data.append([timestamp, value])

            # --- Update Plot ---
            ax.clear()  # Clear the current axes
            ax.plot(timestamps, analog_values, marker='o', linestyle='-')  # Plot the new data
            
            # --- Formatting ---
            ax.set_title('Real-time Analog Signal', fontsize=16)
            ax.set_ylabel('Analog Value', fontsize=12)
            ax.set_xlabel('Time', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.20)
            ax.grid(True) # Add a grid

    except (ValueError, UnicodeDecodeError):
        # Handle cases where the line is not a valid number or has decoding errors
        print(f"Warning: Could not parse line: '{line}'")
    except Exception as e:
        print(f"An error occurred in animate function: {e}")

def main():
    """
    Main function to set up serial connection, plotting, and data saving.
    """
    # This list will store ALL data points for the entire session
    all_data = []

    ser = None  # Initialize ser to None
    try:
        # Establish serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        # Give the Arduino a moment to reset
        time.sleep(2)
        
        # Create the animation. It calls the 'animate' function every 20ms.
        # fargs passes additional arguments (ser, all_data) to the animate function.
        ani = animation.FuncAnimation(fig, animate, fargs=(ser, all_data), interval=20)
        
        print("Plotting... Close the plot window to stop and save the data.")
        plt.show() # This blocking call displays the plot and runs the animation

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}. {e}")
        print("Please check the port name and ensure the device is connected.")

    finally:
        # This block executes when the plot window is closed
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed.")
        
        # Save all the collected data to a CSV file
        if all_data:
            print(f"\nSaving {len(all_data)} data points...")
            with open(OUTPUT_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'analog_value']) # Write header
                writer.writerows(all_data)
            print(f"Data successfully saved to {OUTPUT_FILE}")
        else:
            print("No data was collected to save.")

if __name__ == '__main__':
    main()
