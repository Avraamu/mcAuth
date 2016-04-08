#!/usr/bin/python

import requests
import os

response = requests.get('http://raw.githubusercontent.com/Avraamu/mcAuth/live/mcAuth.py')
f_obj = open('/home/minecraft/mcAuth/mcAuth.py', 'w+')
f_obj.write(response.text)
f_obj.close()
