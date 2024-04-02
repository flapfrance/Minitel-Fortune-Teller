##*****************************************************
## Test for connecting Arduino and computer/raspi (Linux)
## Thanks to Flo for helping... :-)
##
##******************************************************

import serial.tools.list_ports
import time

def find_arduino_port():
    arduino_ports = [port.device for port in serial.tools.list_ports.comports() if 'Arduino' in port.description]
    if not arduino_ports:
        raise Exception("Arduino not found.")    
    if len(arduino_ports) > 1:
        print("More than one Arduinos found. Use the first one.")    
    return arduino_ports[0]

run = False
arduino_port = find_arduino_port()
print("Arduino port",arduino_port)
# initialize serial port
ser = serial.Serial(arduino_port, 19200)

try:
    while True:
        # Read data from Arduino Moneymaker
        data = ser.readline().decode('utf-8').strip()           
        print(data)
        
        
        if data == "OK":
            run = True
            ser.write("RUN\n".encode('utf-8')) # Send info to Arduino Moneymaker
            print("Running Programm")
            input("Press a Button")
            run = False
            ser.write("TRANSACTION_COMPLETE\n".encode('utf-8')) # Send info to Arduino Moneymaker
        elif data == "ENDED":
            print("Moneymaker is waiting for Money")

except KeyboardInterrupt:
    # End prog with ctrl-C
    ser.close()
