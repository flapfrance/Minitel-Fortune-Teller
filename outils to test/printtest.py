import random
from escpos.printer import Usb

def read_codepages(usb_vendor_id, usb_product_id):
    # Verbinden Sie sich mit dem USB-Drucker
    p = Usb(usb_vendor_id, usb_product_id)

    # Drucken Sie einen Testbeleg, der Codepage-Informationen enthält
    #p.text("\x1D\x54\x04")  # ESC/POS-Befehl für Codepage-Informationen
    #p.charcode(code = 'CP850')
    #p.charcode = 'CP850'
    #p.codepage = 'CP850'
    #p.text("test \n")
    x = "ÄäÖöÜü éàèùò \n Æ æ œ Œ  ç Ç \n ë Ë Ï ï « » €\n"
#***Adaptation to printer
    x = x.replace("œ", "oe")
    x = x.replace("Œ", "Oe")
    x = x.replace("€", "Euro ")
    
    #p.text(x)
    #for z in range(1,25):
    z = random.randint(1,24)
    print(z)
    #p.text(str(z))
    #p.set(font='a', height=2, width=1, align='center')
    #p.image("./pics/code_"+ str(z) + ".png")
    p.text("Test")
    # Schneide das Papier
    p.cut()

    # Trennen Sie die Verbindung zum Drucker
    p.close()

# Ersetzen Sie die folgenden Werte durch die tatsächlichen Vendor-ID und Product-ID Ihres Druckers
usb_vendor_id = 0x067B #04b8 
usb_product_id = 0x2303 #0e1f

read_codepages(usb_vendor_id, usb_product_id)
