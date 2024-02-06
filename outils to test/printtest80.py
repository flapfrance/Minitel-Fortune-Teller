# **********************************************
# 80mm printer: 0456:0808
# udev rules: sudo nano /etc/udev/rules.d/97-escpos.rules
#           SUBSYSTEM=="usb", ATTRS{idVendor}=="0456", ATTRS{idProduct}=="0808", MODE="0666", GROUP="dialout"
#           sudo service udev restart
#           sudo reboot
# Einstellungen für 80mm printerr: 58 Zeichen
# p = Usb(0x0456, 0x080d, out_ep=3, profile='TM-P80')
# p.ln() before graphics
# p.image("/home/seb/projects/minitel/fortune/WM/pics/code_"+ str(z) + ".png", impl='bitImageColumn')
# *************************************************************************
import random
from escpos.printer import Usb
def read_codepages(usb_vendor_id, usb_product_id):
    # Verbinden Sie sich mit dem USB-Drucker
    p = Usb(usb_vendor_id, usb_product_id, in_ep=0x81, out_ep=0x03, profile='TM-P80')
    
    # Drucken Sie einen Testbeleg, der Codepage-Informationen enthält
    #p.text("\x1D\x54\x04")  # ESC/POS-Befehl für Codepage-Informationen
    #p.charcode('UTF8')#ISO_8859-15') #code = 'CP850')
    #p.charcode(code='Greek')
    #p.codepage = 'CP850'
    
    p.set(font='a', height=4, width=4, align='center')
    p.ln()
    p.text("TEST \n")
    x = "ÄäÖöÜü éàèùò \n Æ æ œ Œ  ç Ç \n ë Ë Ï ï « » €\n"
    #p.text("First: " + x)
#***Adaptation to printer
    #x = x.replace("œ", "oe")
    #x = x.replace("Œ", "Oe")
    #x = x.replace("€", "Euro ")
    #print(x)
    #p.text("second \n" + x)
    #p.ln()
    p.text("12345678921234567893123456789412345678951234567890")
    #p.ln()
    #p.barcode('4006381333931', 'EAN13', 64, 2, '', '')
    #p.qr('WISH WIZARD PROJECT \n https://www.facebook.com/wishwizardproject', 0, 5, 2, impl='bitImageColumn')
    p.cut("PART")
    z = random.randint(1,24)
    
    #print(z)
    #p.text(str(z))
    p.set(font='a', height=2, width=1, align='center')
    p.text("If you find a person with the same code, \n you should connect with!") 
    p.ln()
    p.image("/home/seb/projects/minitel/fortune/WM/pics/code_"+ str(z) + ".png", impl='bitImageColumn')
    #p.text("Test \n")
    # Schneide das Papier
    p.cut()

    # Trennen Sie die Verbindung zum Drucker
    p.close()

# Ersetzen Sie die folgenden Werte durch die tatsächlichen Vendor-ID und Product-ID Ihres Druckers
usb_vendor_id = 0x0456 #067B #04b8 
usb_product_id = 0x0808 #2303 #0e1f

read_codepages(usb_vendor_id, usb_product_id)



