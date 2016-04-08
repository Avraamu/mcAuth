#/bin/bash

wget https://raw.githubusercontent.com/Avraamu/mcAuth/live/updater.py -O /home/minecraft/Downloads/updater.py
chmod 555 /home/minecraft/Downloads/updater.py

/home/minecraft/Downloads/updater.py
chmod 555 /home/minecraft/Downloads/mcAuth.py

mkdir /home/minecraft/.minecraft/

/home/minecraft/Downloads/mcAuth.py --newprofile


