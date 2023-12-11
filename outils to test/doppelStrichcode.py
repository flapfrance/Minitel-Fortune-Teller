import barcode
from io import BytesIO
from barcode.writer import ImageWriter
from barcode import Code128 #EAN13
from PIL import Image
from escpos.printer import Usb
import random
usb_vendor_id = 0x04b8 
usb_product_id = 0x0e1f
p = Usb(usb_vendor_id, usb_product_id)

# Text & Options für den Barcode

codenum = random.randint(1, 100)
print("Kodierte Nummer: " + str(codenum))
cd= "cd" + str(codenum) 
cdI= "cd" + str(codenum) + "inv"

options = {
    'font_size': 0,
    'dpi': 200
    }

ean = barcode.get('code128')
ean(str(codenum), writer = ImageWriter()).save("./codes/" + cd, options = options)

# Lade das Bild , resize,
img = Image.open("./codes/" + cd +".png")
img = img.resize((380, img.height))
img.save("./codes/" + cd +".png") #,options = dict(font_size = 0))
img = img.rotate(180)

# Speichere das gedrehte Bild
rotated_filename = cdI + ".png"
img.save("./codes/" + rotated_filename)

# and print
p.image("./codes/" + cd + ".png")
p.text("----------> cut here ->-------->\n")
p.image("./codes/" + cdI + ".png")
p.text("\n \n")
#p.cut()
p.close()
