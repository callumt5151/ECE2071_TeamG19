import serial
import serial.tools.list_ports
import time
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv


def findSerialDevice():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if 'STLink' in p.description:
            port_name = p.device
            return port_name  # /dev/cu.usbmodem11103
    return "N/A"

ser = serial.Serial(findSerialDevice(), 921600, timeout=10)

time.sleep(0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()

SAMPLE_RATE = 8000 #????? is this gonna be okay
data = []

# ser.write(b'm')
# ser.flush()
# ser.write(bytes([5]))
# ser.flush()
ser.write(b'm' + bytes([5]))
ser.flush()

# for i in range(5*SAMPLE_RATE):
#     response = ser.read(1)
#     data.append(int.from_bytes(response, byteorder='big'))
expected = 5 * SAMPLE_RATE
raw = ser.read(expected) # wait for N bytes
data = list(raw)    


# STUFF TO PRODUCE OUTPUT
data = np.array(data, dtype=np.float64)

data_min = data.min()
data_max = data.max()
data_norm = (data - data_min) / (data_max - data_min)
data_uint8 = (data_norm * 255).astype(np.uint8) # normalise the data

ser.close()

base_filename = 'output'

with wave.open(f'{base_filename}.wav', 'wb') as wf:
    wf.setnchannels(1) # ie this is mono audio
    wf.setsampwidth(1)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(data_uint8.tobytes())

# t = np.arange(len(data_uint8)) / SAMPLE_RATE

# plt.figure(figsize=(10, 4))
# plt.plot(t, data_uint8)
# plt.title('Audio Recording: Amplitude vs Time')
# plt.xlabel('Time (s)')
# plt.ylabel('Amplitude (8-bit, 0-255)')
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.savefig(f'{base_filename}_waveform.png', dpi=150)
# plt.close()

# signal_centred = data_uint8.astype(np.float64) - 127.5

# fft_vals = np.fft.rfft(signal_centred)
# fft_freqs = np.fft.rfftfreq(len(signal_centred), d=1/SAMPLE_RATE)
# fft_magnitude = np.abs(fft_vals)

# fft_db = 20 * np.log10(fft_magnitude + 1e-6)

# plt.figure(figsize=(10, 4))
# plt.plot(fft_freqs, fft_db)
# plt.title('Audio Recording: Frequency Spectrum (FFT)')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Magnitude (dB)')
# plt.grid(True, alpha=0.3)
# plt.xlim(0, SAMPLE_RATE / 2) 
# plt.tight_layout()
# plt.savefig(f'{base_filename}_fft.png', dpi=150)
# plt.close()

# with open(f'{base_filename}.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(['sample_rate', SAMPLE_RATE])
#     writer.writerow(['sample_index', 'amplitude'])
#     for i, sample in enumerate(data_uint8):
#         writer.writerow([i, int(sample)])

# print(f'Saved: {base_filename}.wav, {base_filename}_waveform.png, {base_filename}_fft.png, {base_filename}.csv')