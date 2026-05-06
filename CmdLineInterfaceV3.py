import serial
import serial.tools.list_ports
import time
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime

SAMPLE_RATE = 22050
# DURATION = 2

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
    data_uint8 = data.astype(np.uint8)

    # have datetime in file names so they dont overwrite
    now = datetime.now()
    base_filename = 'outputs/' + now.strftime("%Y%m%d%H%M%S")+'output'

    # base_filename = 'output'

    with wave.open(f'{base_filename}.wav', 'wb') as wf:
        wf.setnchannels(1) # ie this is mono audio
        wf.setsampwidth(1)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data_uint8.tobytes())

    t = np.arange(len(data_uint8)) / SAMPLE_RATE

    plt.figure(figsize=(80, 10)) # make wide so wave form looks legit
    plt.plot(t[3:], data_uint8[3:]) # get rid of weird transients at start
    plt.title('Wave')
    plt.xlabel('t')
    plt.ylabel('A')
    plt.tight_layout()
    plt.savefig(f'{base_filename}_wave.png')
    plt.close()

    with open(f'{base_filename}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_index', 'amplitude'])
        for i, sample in enumerate(data_uint8):
            writer.writerow([i, int(sample)])

    print("Output files were saved to the outputs folder")
    return

def runM(DURATION):
    time.sleep(0.2)
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
    time.sleep(0.2)
    print("\nPlace hand over sensor to begin recording or ctrl+C to exit this mode")
    data = []
    ser.write(b'd')
    ser.flush()
    while (1): # add way to end this????
        raw = ser.read(1) # IT HANGS HERE NO TIMEOUT
        data.append(raw[0])
        if len(data) == 1:
            print("Distance Trigger Mode Recording...")
        if len(data) >= 4 and data[-4:] == [0xEE, 0xAF, 0xDD, 0xEE]:
            print("Distance Trigger Mode Recording Complete!")
            break

    data = data[:-4] 
    data = np.array(data, dtype=np.float64)
    return data



#----------------------------MAIN---------------------------------
ser = serial.Serial(findSerialDevice(), 921600, timeout=None)

time.sleep(0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()

loop = True
while(loop):
    mode = input("\nEnter 'm' for Manual Mode\nEnter 'd' Distance Trigger Mode\nEnter 'q' to quit the program\n")
    if (mode == 'm'):
        dur = int(input("\nManual Mode: Enter length of recording in seconds\n"))
        if ( (dur>10 ) or (dur<=0) ):
            print("Invalid input")
            continue
        print("\nManual Mode Recording...")
        data = runM(dur)
        print("Manual Mode Recording Complete!")
        outputs(data)

    elif (mode == 'd'):
        try:
            while (1):
                data = runD()
                outputs(data)
            continue
        except KeyboardInterrupt: # triggers if u do ctrlC ONLY INSIDE THIS TRY BLOCK maybe only works for unix systems?
            time.sleep(0.2)
            ser.write(b's')
            ser.flush()
            print("\nDistance Trigger Mode was exited")
            continue
    

    elif (mode == 'q'):
        loop = False
        continue
    else:
        print("Invalid input")
        continue


ser.close()
#-----------------------------ENDMAIN----------------------------