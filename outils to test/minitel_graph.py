import pynitel, serial, os

#******* Code start***************

m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 1200, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
        #os.system("echo -en '\x1b\x3a\x6b\x64' > /dev/ttyUSB0")        
os.system("stty -F /dev/ttyUSB0 speed 1200")
speed = 4800
sltime = 60
if speed == 4800:
     os.system("echo -en '\x1b\x3a\x6b\x76' > /dev/ttyUSB0")
     m.end()      
     os.system("stty -F /dev/ttyUSB1 speed 4800")
     m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB1', 4800, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
     print("Baudrate: ", speed)
else:# speed == 1200:            
     print("Baudrate: ", speed)
m.home()
#os.system("echo -en '\x1b\x3a\x6A\x43' > /dev/ttyUSB0")
#m.step(1)# Set up OpenAI API key
#api_key = "your_api_key"
#openai.api_key = api_key
#m._print("Losgehts")
print("losgehts")
m.drawscreen("fortune.vdt")
time.sleep(2)

m.home()

m._print("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
m.pos(2)
m.gr()
m._print("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
m.pos(4)
m._print("abcdefghijklmnopqrstuvwxyz")
m.pos(5)
m.gr()
m._print("abcdefghijklmnopqrstuvwxyz")
m.pos(7)
m._print("1#@←→↑")
m.pos(8)
m.gr()
m._print("1#@←→↑")

m.pos(10)
m.gr()
m.sendchr(0x21)
m.sendchr(0x20)
m.sendchr(0x22)
m.sendchr(0x20)
m.sendchr(0x23)
m.sendchr(0x20)
m.sendchr(0x7F)
#m.sendchr(32)
#time.sleep(5)
#m.pos(4,2)
#m.scale(3)
#m._print("Ta question?" )

#0x20  0x21  0x22  0x23  0x24  0x25  0x26  0x27
#0x28  0x29  0x2A  0x2B  0x2C  0x2D  0x2E  0x2F
#0x30  0x31  0x32  0x33  0x34  0x35  0x36  0x37
#0x38  0x39  0x3A  0x3B  0x3C  0x3D  0x3E  0x3F
#0x60  0x61  0x62  0x63  0x64  0x65  0x66  0x67
#0x68  0x69  0x6A  0x6B  0x6C  0x6D  0x6E  0x6F
#0x70  0x71  0x72  0x73  0x74  0x75  0x76  0x77
#0x78  0x79  0x7A  0x7B  0x7C  0x7D  0x7E  0x7F
