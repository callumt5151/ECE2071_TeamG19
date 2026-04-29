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

msg = b'Msg\n'
checksum = 0
for b in msg:
    checksum ^= b

ser.write(msg + bytes([checksum]))
ser.flush()

response = ser.readline() 
print("received:")
decoded = response.decode().strip()
print(decoded) # have to use response[0] for hex int not decode, i think is for strings


ser.close()
print("")


# msg = b'_Message to send\n'
# checksum = 0
# for b in msg:
#     checksum ^= b
# ser.write(b'_')
# time.sleep(0.1)
# ser.write(b'Message to send\n')
# ser.write(bytes([checksum]))
# ser.flush()




# # while True:
# #     data = ser.read(size=5)  # read 5 bytes (your "005\r\n")
# #     print(data.decode(), end="")  # end="" because \r\n already handles newlines

# ser.write('A'.encode())
# ser.flush()
# print("sent A")

# while True:
#     data = ser.read(size=5)  # read 5 bytes (your "005\r\n")
#     print(data.decode(), end="")  # end="" because \r\n already handles newlines

# # NOTE: The read function returns a list of bytes, so you must convert it to a string to print it properly. This can
# # be done by adding .decode() to the variable containing your binary data. Similarly, the write function
# # accepts a list of bytes, so you would need to add .encode() to the string you wish to send.

# filename = "data.txt"
# f = open(filename, 'w')
# for i in range(100):
#     ser.write(b'A')
#     ser.flush()
        
#     response = ser.read(size=5)
#     decoded = response.decode().strip()
#     f.write(decoded + "\n")



