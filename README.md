# Minitel-Fortune-Teller
A Fortune teller using an old french minitel and AI
1.  Requirements: For the new Raspi-images based on Debian 12 (Bookworm), the installation of 3rd party pip components is restricted. To use them you can install them with `pip install "package_name" --break-system-packages` .
  -  Openai V1: `pip install openai` or if older Version is installed `pip install --upgrade openai`
  -  For USB relay (8 relays) : `pip install pyhid_usb_relay`
  -  For Thermal Printer: `pip install escpos`
  -  Module astroloic: `pip install kerykeion`
2.  After first start check  settings.ini
  -  add your Openai API code ( needs an account)
  -  check if the minitel can work with 4800 bauds. If there is a FNCT-Key change the Baudrate value to 4800.
3.  And you need a minitel with a connection cable USB to DIN . It's helpfull to block the carriage-return key, cause i didn't find a way to filter it out. The use can diturb the output on the screen.
