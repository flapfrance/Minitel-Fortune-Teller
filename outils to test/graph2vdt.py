import qrcode

from numpy import array
from PIL import Image
def konvertiere_zu_8_graustufen(quellpfad, max_breite, max_hoehe, ziel_pfad):
    # Bild öffnen
    bild = Image.open(quellpfad)
    # Verhältnis von Breite zu Höhe beibehalten und die größte Dimension auf max setzen
    bild.thumbnail((max_breite, max_hoehe))
    # In Graustufen umwandeln
    bild = bild.convert('L')
    # Bild auf B/W reduzieren (auf 8 Graustufen reduzieren)
    bild = bild.quantize(colors=2)
    # Bild speichern
    bild.save(ziel_pfad)
    
def convert_to_minitel(image_data, width, height, block_width):
    minitel_data = []

    for y in range(0, height, 3):
        for x in range(0, width, 2):
            minitel_value = 0

            for i in range(3):
                for j in range(2):
                    if (y + i) * width + x + j < len(image_data):
                        pixel_value = int(image_data[(y + i) * width + x + j])
                        minitel_value += pixel_value * (2 ** (i * 2 + j))

            # Anpassung der Werte
            #if minitel_value >= 32 and minitel_value <= 63:
                #minitel_value += 64
            #elif minitel_value >= 96 and minitel_value <= 127:
                #minitel_value += 64

            minitel_data.append(minitel_value)

    # Formatierung in Zeilen
    formatted_data = [minitel_data[i:i + block_width] for i in range(0, len(minitel_data), block_width)]

    return formatted_data
def array_to_hex(row):
    hex_row = [hex(value)[2:].zfill(2) for value in row]
    return ' '.join(hex_row)
def send_to_mini(result):
    for row in result:
        hex_row = array_to_hex(row)
        print(hex_row)
def code(user_input):
    x = ""
    data = [[0, '0x20'], [1, '0x21'], [2, '0x22'], [3, '0x23'], [4, '0x24'], [5, '0x25'],
 [6, '0x26'], [7, '0x27'], [8, '0x28'], [9, '0x29'], [10, '0x2a'], [11, '0x2b'],
 [12, '0x2c'], [13, '0x2d'], [14, '0x2e'], [15, '0x2f'], [16, '0x30'], [17, '0x31'],
 [18, '0x32'], [19, '0x33'], [20, '0x34'], [21, '0x35'], [22, '0x36'], [23, '0x37'],
 [24, '0x38'], [25, '0x39'], [26, '0x3a'], [27, '0x3b'], [28, '0x3c'], [29, '0x3d'],
 [30, '0x3e'], [31, '0x3f'], [32, '0x60'], [33, '0x61'], [34, '0x62'], [35, '0x63'],
 [36, '0x64'], [37, '0x65'], [38, '0x66'], [39, '0x67'], [40, '0x68'], [41, '0x69'],
 [42, '0x6a'], [43, '0x6b'], [44, '0x6c'], [45, '0x6d'], [46, '0x6e'], [47, '0x6f'],
 [48, '0x70'], [49, '0x71'], [50, '0x72'], [51, '0x73'], [52, '0x74'], [53, '0x75'],
 [54, '0x76'], [55, '0x77'], [56, '0x78'], [57, '0x79'], [58, '0x7a'], [59, '0x7b'],
 [60, '0x7c'], [61, '0x7d'], [62, '0x7e'], [63, '0x7f']]

    # Eingabe der Zahl zwischen 0 und 63
    user_input = int(user_input)

# Überprüfe, ob die Eingabe im gültigen Bereich liegt
    if 0 <= user_input <= 63:
    # Rufe den passenden Code aus dem Array ab
        hex_value, decimal_value = data[int(user_input)]
        return decimal_value
        print(f"Hexadezimalwert: {hex_value}, Dezimalwert: {decimal_value}")
    else:
        print("Die Eingabe muss zwischen 0 und 63 liegen.")    
    
# Beispielaufruf
import qrcode
import pynitel, serial, os
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

img = qrcode.make('https://www.artphone.fr \n ART`n More \n The hotter call', border=0)
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")

#quellpfad = 'AP.png'  # Passe dies an den Dateipfad deines Bildes an
quellpfad = 'some_file.png'  # Passe dies an den Dateipfad deines Bildes an
zielbreite = 80
zielhöhe = 72
ziel_pfad = 'zielbild.png'  # Passe dies an den gewünschten Dateipfad für das Ausgabebild an

konvertiere_zu_8_graustufen(quellpfad, zielbreite, zielhöhe, ziel_pfad)

image = Image.open("zielbild.png")
image_width = image.size[0]
image_height = image.size[1]
block_width = int(image_width / 2) # Anzahl der Bytes pro Zeile im resultierenden Array
image_array = array(image.getdata())

print("Widht: ", image_width, " Height: ", image_height)

minitel_result = convert_to_minitel(image_array, image_width, image_height, block_width)
# Die resultierenden 200 Bytecodes sind jetzt in minitel_result.
for z in range(image_height // 3):
    print(minitel_result[z])
r = 1
m.pos(r)
for row in minitel_result:
    #m.pos(minitel_result)    
    for entry in row:        
        m.gr()
        m.sendchr(int(code(entry),16))
        #m._print(chr(entry))#, end=' ')
    r = r+1
    m.pos(r,1)
    print()
m.text()    
    #hex_row = array_to_hex(row)
    #print(hex_row)
