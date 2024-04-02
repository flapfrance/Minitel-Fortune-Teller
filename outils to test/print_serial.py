#!/usr/bin/env python
from escpos.printer import Usb
usb_vendor_id = 0x067b #067B #04b8 
usb_product_id = 0x2303 #2303 #0e1f
#Bus 001 Device 006: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
p = Usb(usb_vendor_id, usb_product_id)
#Epson = printer.Serial("/dev/ttyUSB0",9600,8,2)
#p = printer.Serial("/dev/ttyUSB0",115200,8,2)
#p.charcode = 'CP850'
#p.codepage = 'CP850'
p.set(font='a', height=2, width=2, align='center')
p.text("Hello wOrld !!! \n")
p.text("0920192 \n")

#p.image("fortune.png")
p.cut()

