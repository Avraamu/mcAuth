#/bin/bash

wget https://raw.githubusercontent.com/Avraamu/mcAuth/master/mcAuth.py -O /home/minecraft/Downloads/mcAuth.py
chmod 555 /home/minecraft/Downloads/mcAuth.py

read username
read password

echo '{"username":"$username","password":"$password"}' > /home/minecraft/Downloads/cred.json
chmod 444 /home/minecraft/Downloads/cred.json



