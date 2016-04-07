#!/usr/bin/python

import sys
import getopt
import requests
import simplejson as json
import os
import logging

url = 'https://authserver.mojang.com'
save_location = os.path.expanduser('~') + '/.minecraft/launcher_profiles.json'
cred_location = os.path.expanduser('~') + '/Downloads/cred.json'


logging.basicConfig(filename=os.path.expanduser('~') + '/Downloads/mcAuth.log', level=logging.DEBUG)
logging.debug('\n\n***Starting script!')


def dash(string):
    return string[0:8] + '-' + string[8:12] + '-' + string[12:16] + '-' + string[16:20] + '-' + string[20:]


def unDash(string):
    return string.replace('-', '')


class Login:
    def __init__(self):
        f_obj = open(cred_location)
        userpass = json.loads(f_obj.read())
        self.username = userpass['username']
        self.password = userpass['password']

        self.authenticated = False
        self.validClientToken = False
        self.clientToken = ''
        self.accessToken = ''
        self.profileIdentifier = ''
        self.playerName = ''

    def authenticate(self):
        param = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": self.username,
            "password": self.password
        }
        if self.clientToken != '':
            param["clientToken"] = dash(self.clientToken)

        response = requests.post(url + "/authenticate", data=json.dumps(param))
        if response.status_code != 200:
            # throw error
            logging.error('Could not authenticate!')
            self.authenticated = False
            self.validClientToken = False
        else:
            logging.debug('Successful new authentication')
            jsonResponse = json.loads(response.text)
            self.accessToken = jsonResponse['accessToken']
            self.clientToken = unDash(jsonResponse['clientToken'])
            self.profileIdentifier = jsonResponse['availableProfiles'][0]['id']
            self.playerName = jsonResponse['availableProfiles'][0]['name']
            self.authenticated = True
            self.validClientToken = True

    def refresh(self):
        param = {
            "accessToken": self.accessToken,
            "clientToken": self.clientToken,
            "selectedProfile": {
                "id": self.profileIdentifier,
                "name": self.playerName
            }
        }
        response = requests.post(url + '/refresh', data=json.dumps(param))
        if response.status_code != 200:
            # throw error
            logging.error('Could not refresh!')
            self.authenticated = False
            self.validClientToken = False
        else:
            logging.debug('Successful refresh!')
            jsonResponse = json.loads(response.text)
            self.accessToken = jsonResponse['accessToken']
            self.clientToken = jsonResponse['clientToken']
            self.profileIdentifier = jsonResponse['selectedProfile']['id']
            self.playerName = jsonResponse['selectedProfile']['name']
            self.authenticated = True
            self.validClientToken = True

    def validate(self):
        param = {
            "accessToken": self.accessToken,
            "clientToken": dash(self.clientToken)
        }
        response = requests.post(url + '/validate', data=json.dumps(param))
        if response.status_code != 204:
            self.validClientToken = False
            logging.error('Token could not be validated!')
        else:
            self.validClientToken = True
            self.authenticated = True
            logging.debug('Token valid!')

    def saveauth(self):
        data = {
            "profiles": {   
                self.playerName: {
                    "name": self.playerName
                }
            },
            "selectedProfile": self.playerName,
            "clientToken": dash(self.clientToken),
            "authenticationDatabase": {
                self.profileIdentifier: {
                    "username": self.username,
                    "accessToken": self.accessToken,
                    "userid": "0698f5053e7748cf9740f8de370aa1c1",
                    "uuid": dash(self.profileIdentifier),
                    "displayName": self.playerName
                }
            },
            "selectedUser": self.profileIdentifier,
            "launcherVersion": {
                "name": "1.6.61",
                "format": 18
            }
        }
        f_obj = open(save_location, "w")
        f_obj.write(json.dumps(data))
        f_obj.close()
        f_obj = open(save_location+'.generated', "w")
        f_obj.write(json.dumps(data))
        f_obj.close()

    def loadauth(self):
        f_obj = open(save_location, "r")
        loaded = json.loads(f_obj.read())
        f_obj.close()
        self.profileIdentifier = unDash(loaded['selectedUser'])
        self.clientToken = unDash(loaded['clientToken'])
        self.accessToken = loaded['authenticationDatabase'][self.profileIdentifier]['accessToken']
        self.playerName = loaded['authenticationDatabase'][self.profileIdentifier]['displayName']


def defaultrun():
	try:
	    obj = Login()
	    try:
		logging.debug('Attempting launcher_profiles.json read')
		obj.loadauth()
		logging.debug('Loaded profile data for user: ' + obj.playerName + ' ' + obj.username)
	    except Exception as e:
		logging.exception("Could not load authenticate file! Reauthenticating...")
		obj.authenticate()

	    obj.validate()
	    if not obj.validClientToken:
		logging.debug('No valid clientToken, refreshing...')
		obj.refresh()

	    if not obj.authenticated:
		logging.debug('Profile does not seem to be authenticated! reauthenticating...')
		obj.authenticate()

	    logging.debug('Saving authentication...')
	    obj.saveauth()
	except Exception as e:
	    logging.exception("CRITICAL: Could not authenticate at all")


	logging.debug('Attempting minecraft launch...')
	try:
	    os.system('java -jar ~/Downloads/Minecraft.jar')
	    logging.debug('Launcher seems to have been closed!')
	except Exception as e:
	    logging.exception("Unable to start launcher!")

def cleanslate():
	obj = Login()
	try:
		logging.debug('Trying authenticate...')
		obj.authenticate()
		obj.saveauth()
	except:
		logging.exception('Failed to authencticate :(, not saving.')


try:
	opts, args = getopt.getopt(sys.argv[1:],"h", ["cleanslate", "cs"])
except getopt.GetoptError:
	print 'usage: mcAuth.py [--cleanslate] [-h]'
	sys.exit(2)
for opt, arg in opts:
	if opt == "-h":
		print 'usage: mcAuth.py [--cleanslate] [-h]'
		print "    Run without parameters for normal execution \n    Run with --cs or --cleanslate option for new authenticate session"
		sys.exit()
	elif opt in ("--cleanslate", "--cs"):
		cleanslate()
		sys.exit()

defaultrun()

logging.info('Script execution came to an end')










