#! /usr/bin/python
import usb.core

# Gerät finden 1a86:7523
import serial
import time

# COM-Port entsprechend deinem System anpassen (normalerweise "COMx" unter Windows oder "/dev/ttyUSBx" unter Linux)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Beispiel: Relais einschalten
#ser.write(b'DEIN BEFEHL ZUM EINSCHALTEN DES RELAIS')
ser.write(b'\x01')
# Wartezeit für die Stabilität der Verbindung
time.sleep(4)
ser.write(b'\x00')
# Beispiel: Relais ausschalten
#ser.write(b'DEIN BEFEHL ZUM AUSSCHALTEN DES RELAIS')

# Serial-Verbindung schließen
ser.close()
