import pynitel, serial, os, openai, time

#******* Code start***************

m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 1200, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
        #os.system("echo -en '\x1b\x3a\x6b\x64' > /dev/ttyUSB0")        
os.system("stty -F /dev/ttyUSB0 speed 1200")
speed = 4800
sltime = 60

if speed == 4800:
     os.system("echo -en '\x1b\x3a\x6b\x76' > /dev/ttyUSB0")
     m.end()      
     os.system("stty -F /dev/ttyUSB0 speed 4800")
     m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 4800, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
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
m.drawscreen("Fortune.vdt")
time.sleep(5)
m.home()
m.resetzones()

m.pos(4,2)
m.scale(3)
m._print("Ta question?" )

#m.zone(ligne, colonne, longueur, texte, couleur)       
m.zone(7, 2, 38, "", m.blanc)
m.zone(9, 2, 38, "", m.blanc)
m.zone(11, 2, 38, "", m.blanc)
m.zone(13, 2, 38, "", m.blanc)
m.zone(15, 2, 38, "", m.blanc)
m.zone(17, 2, 38, "", m.blanc)
m.zone(19, 2, 38, "", m.blanc)
m.zone(21, 2, 38, "", m.blanc)

while True:
     x=7
     while x <= 21:
          if not x % 2 == 0:          
               print(x)
               m.pos(x,2)
               m.plot('.', 37)     
          x = x + 1
     zone = 1
     (zone, touche) = m.waitzones(zone, sltime)

     if touche == 1:
               
               print("Touche ENVOI: " + str(touche))
               mess = str("")
               for y in range(8):
                    if not m.zones[y]['texte'] == "":
                         mess = str(mess) + str(m.zones[y]['texte'] + " ")
               print(mess)               
     else:
          break
print(touche)
