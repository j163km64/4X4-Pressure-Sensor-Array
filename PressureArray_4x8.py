import serial
import time
import datetime       #延时使用
import binascii
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread

plt.ion() # turning interactive mode on

# Configure the serial port
ser = serial.Serial('COM5', 460800)  # Replace 'COM1' with the appropriate port and baud rate

def interpret_protocol_frame(frame):
    global pressure_data
    pressure_data = []
    if len(frame) != 70:
        raise ValueError("Frame must be exactly 70 bytes long")

    # Extract the head (first 2 bytes)
    head = frame[:2]

    # Extract the CNT (next 2 bytes) and convert to integer
    cnt = int.from_bytes(frame[2:4], byteorder='big')

    # Extract the data frame (next 64 bytes)
    data_frame = frame[4:68]
    # Transform the data frame to integer data (32 points)
    for i in range(0, len(data_frame), 2):
        adc_data = int.from_bytes(data_frame[i:i+2], byteorder='big')
        pressure_data.append(adc_data)

    checksum = frame[68:]

    # Return the updated dictionary with the integer data
    return {
        'head': head,
        'cnt': cnt,
        'data_frame': pressure_data,
        'checksum': checksum
    }

def readSerialData():
    # Read the serial data

    while True:
        raw_data = ser.read(70)
        
        if raw_data[:2] == b'\xff\x84':
            # Parse the protocol frame
            data = interpret_protocol_frame(raw_data)
            print(data)

def plot_heatmap(data):
    # Reape the data to 4x8
    data_matrix = np.array(data).reshape((4, 8))
    
    plt.imshow(data_matrix, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.title('4x8 Heatmap of Serial Data')
    plt.show()

def main():
    global pressure_data
    pressure_data = 0
    t1 = Thread(target=readSerialData)# Read the data from the serial port
    # 启动线程运行
    t1.start()

    while True:
        if pressure_data != 0:
            data_matrix = np.array(pressure_data).reshape((4, 8))
            data_matrix.transpose()
            sns.heatmap(data_matrix, vmin = 200,vmax=800,cmap='mako')
            plt.pause(0.01)
            plt.clf()

    t1.join()
    
if __name__=="__main__":
    main()
    #debug()

