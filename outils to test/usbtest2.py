# To run with pyusb debugging:
#
#   PYUSB_DEBUG=debug python relay.py
#
# Grab the vendor and product codes from syslog when plugging in the relay:
#
#   usb 3-1: New USB device found, idVendor=1a86, idProduct=7523
#
import time
import usb.core
import usb.util

dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523)

if dev is None:
	raise ValueError("Device not found")

if dev.is_kernel_driver_active(0):
	dev.detach_kernel_driver(0)
	print("Ok bis hier ")
cfg = dev.get_active_configuration()
##print(cfg)
intf = cfg[(0,0)]

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

assert ep is not None

close_relay_cmd = [0xA0, 0x01, 0x01, 0xA2]
#open_relay_cmd = [0xA0, 0x01, 0x00, 0xA1]

# Since I'm using this to send a signal to a gate controller, I'm simulating just
# pressing a button to make the circuit for 2 seconds, then releasing:

ep.write(close_relay_cmd)
time.sleep(2)
ep.write(open_relay_cmd)
