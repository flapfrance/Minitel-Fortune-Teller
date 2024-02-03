# Minitel-Fortune-Teller
A Fortune teller using an old french minitel and AI with ChatGPT. Special thanks to cquest and his Python library: https://github.com/cquest/pynitel and all the informations found at the "Musée du minitel" : https://www.museeminitel.fr/ . Also thanks to all the friends who helped to bring this project to life.

1.  Requirements: For the new Raspi-images based on Debian 12 (Bookworm), the installation of 3rd party pip components is restricted. To use them you can install them with `pip install "package_name" --break-system-packages` .
  -  Openai V1: `pip install openai` or if older Version is installed `pip install --upgrade openai`
  -  For USB relay (8 relays) : `pip install pyhid_usb_relay`
  -  For Thermal Printer: `pip install escpos`
  -  Add Printer to udev:     
    `lsusb` to find idVendor:isProduct  of printer (xxxx:yyyy) <br>     
    udev rules: `sudo nano /etc/udev/rules.d/something-escpos.rules` <br>           
    Add: `SUBSYSTEM=="usb", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="yyyy", MODE="0666", GROUP="dialout"`<br>     
    `sudo service udev restart`<br>     
    `sudo reboot`
  -  Module astroloic: `pip install kerykeion`
2.  After first start check  settings.ini
  -  add your Openai API code ( needs an account)
  -  check if the minitel can work with 4800 bauds. If there is a FNCT-Key change the Baudrate value to 4800.
3.  Divers:
  - And you need a minitel (best is Minitel1 with FNCT Key) and a connection cable USB to DIN .More infos here:
  - It's helpfull to block the carriage-return key, cause i didn't find a way to filter it out. The use can disturb the output on the screen.
