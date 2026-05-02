import serial
import serial.tools.list_ports
import time
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime



def findSerialDevice():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if 'STLink' in p.description:
            port_name = p.device
            return port_name
    return "N/A"

def outputs(data):
    # data_min = data.min()
    # data_max = data.max()
    # data_norm = (data - data_min) / (data_max - data_min)
    # data_uint8 = (data_norm * 255).astype(np.uint8)
    data_uint8 = data.astype(np.int8)

    # have datetime in file names so they dont overwrite
    now = datetime.now()
    # base_filename = 'outputs/' + now.strftime("%Y%m%d%H%M%S")+'output'

    base_filename = 'output'

    with wave.open(f'{base_filename}.wav', 'wb') as wf:
        wf.setnchannels(1) # ie this is mono audio
        wf.setsampwidth(1)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data_uint8.tobytes())

    t = np.arange(len(data_uint8)) / SAMPLE_RATE

    plt.figure(figsize=(10, 4))
    plt.plot(t, data_uint8)
    plt.title('Waveform')
    plt.xlabel('t')
    plt.ylabel('A')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{base_filename}_waveform.png', dpi=150)
    plt.close()

    with open(f'{base_filename}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_rate', SAMPLE_RATE])
        writer.writerow(['sample_index', 'amplitude'])
        for i, sample in enumerate(data_uint8):
            writer.writerow([i, int(sample)])

    print(f'Saved: {base_filename}.wav, {base_filename}_waveform.png, {base_filename}_fft.png, {base_filename}.csv')
    return

def runM(DURATION):
    data = []

    ser.write(b'm' + bytes([DURATION]))
    ser.flush()

    # for i in range(5*SAMPLE_RATE):
    #     response = ser.read(1)
    #     data.append(int.from_bytes(response, byteorder='big'))
    expected = DURATION * SAMPLE_RATE
    raw = ser.read(expected) # wait for N bytes
    data = list(raw)    

    data = np.array(data, dtype=np.float64)
    return data

def runD():
    data = []
    ser.write(b'd')
    ser.flush()

    while True: # add way to end this
        raw = ser.read(1)
        print(raw)
        data.append(raw[0])
        if len(data) >= 4 and data[-4:] == [0xEE, 0xAF, 0xDD, 0xEE]:
            print("End Word Received")
            break

    data = data[:-4] 
    data = np.array(data, dtype=np.float64)
    return data




#----------------------------MAIN---------------------------------
ser = serial.Serial(findSerialDevice(), 921600, timeout=None)

time.sleep(0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()

# loop = True
# while(loop):
#     mode = input("Enter 'm' for Manual Recording Mode\nEnter 'd' Distance Trigger Mode\nEnter 'q' to quit the program:\n")
#     if (mode == 'm'):
#         dur = int(input("Manual Recording Mode: Enter length in seconds:\n"))
#         if ( (dur>10 ) or (dur<=0) ):
#             print("Invalid input")
#             continue
#         print("Recording...")
#         data = runM(dur)
#         outputs(data)
#         loop = False

#     elif (mode == 'd'):
#         loop = False
#         continue

#     elif (mode == 'q'):
#         loop = False
#         continue
#     else:
#         print("Invalid input")
#         continue

SAMPLE_RATE = 22050
DURATION = 5
# data = runM(DURATION)
data = runD()
outputs(data)

ser.close()
#-----------------------------ENDMAIN----------------------------