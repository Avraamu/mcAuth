#!/usr/bin/python

import requests
import os

response = requests.get('https://raw.githubusercontent.com/Avraamu/mcAuth/live/mcAuth.py')
f_obj = open('mcAuth.py', 'w+')
f_obj.write(reponse.text)
f_obj.close()
