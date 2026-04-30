import serial
import serial.tools.list_ports
import time
import wave
import numpy as np


def findSerialDevice():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if 'STLink' in p.description:
            port_name = p.device
            return port_name  # /dev/cu.usbmodem11103
    return "N/A"

ser = serial.Serial(findSerialDevice(), 115200, timeout=10)

time.sleep(0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()

SAMPLE_RATE = 8264
data = []

for i in range(5*SAMPLE_RATE):
    response = ser.read(1)
    data.append(int.from_bytes(response, byteorder='big'))

# convert list to numpy array
data = np.array(data)
# normalise to 0 to 255 range:
data = (data - data.min()) / data.max() # scale to 0-1
data = data * 255 # scale to 0-255
data = data.astype(np.uint8) # convert to uint8 type

ser.close()

filename = 'prac7.wav'
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1) # mono audio (single channel)
    wf.setsampwidth(1) # 8 bits (1 byte ) per sample
    wf.setframerate(SAMPLE_RATE) # set the sample rate that the data was recorded at
    wf.writeframes(data.tobytes()) # write the audio data to the file
