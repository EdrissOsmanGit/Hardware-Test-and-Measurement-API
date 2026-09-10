import serial
import time

ser = serial.Serial('COM3', 9600, timeout=2)  # replace COM3 with your port
time.sleep(2)  # Arduino resets on connect — must wait

ser.write(b"READ 0\n")
response = ser.readline().decode().strip()
print(f"Voltage: {response}")

ser.close()