import pyhid_usb_relay, time, sys
try:
    relay = pyhid_usb_relay.find()
except:
    print("No adequat USB Device found")
    time.sleep(5)
    sys.exit()
    
print(relay.state)
print("Toggeling relay")
for x in range(8,0,-1):
    print(x)
    relay.toggle_state(x)
    time.sleep(0.05)
    print("State relais nummer: ",x ,relay.get_state(x))

print(relay.state)

time.sleep(2)

print("Toggeling relay")
for x in range(8,0,-1):
    print(x)
    relay.toggle_state(x)
    time.sleep(0.05)
    print("State relais nummer: ",x ,relay.get_state(x))

print(relay.state)


time.sleep(5)
relay.toggle_state(1)
print(relay.state)

time.sleep(10)
relay.toggle_state(1)
print(relay.state)

time.sleep(10)
relay.set_state(1, True)
print(relay.state)

time.sleep(10)
relay.set_state(1, False)
print(relay.state)


