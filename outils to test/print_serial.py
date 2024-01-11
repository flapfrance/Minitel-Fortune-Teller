#!/usr/bin/env python
from escpos import *

#Bus 001 Device 006: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port

#Epson = printer.Serial("/dev/ttyUSB0",9600,8,2)
p = printer.Serial("/dev/ttyUSB0",115200,8,2)
p.charcode = 'CP850'
p.codepage = 'CP850'
p.set(font='a', height=2, width=2, align='center')
p.text("Hello wörld !!! \n")
p.text("0920192 \n")

p.image("fortune.png")
p.cut()

