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
	logging.debug('Authenticating using clientToken: ' + self.clientToken)
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
	else:
	    logging.debug('Sending no clientToken for authentication.')

        response = requests.post(url + "/authenticate", data=json.dumps(param))
        if response.status_code != 200:
            # throw error
            logging.error('Could not authenticate!')
            self.authenticated = False
            self.validClientToken = False
        else:
            jsonResponse = json.loads(response.text)
	    logging.debug('Received accessToken: ' + jsonResponse['accessToken'])
            self.accessToken = jsonResponse['accessToken']
            logging.debug('Received clientToken: ' + jsonResponse['clientToken'])	#receive as undashed
            self.clientToken = unDash(jsonResponse['clientToken'])
            self.profileIdentifier = jsonResponse['availableProfiles'][0]['id']
            self.playerName = jsonResponse['availableProfiles'][0]['name']
            self.authenticated = True
            self.validClientToken = True
            logging.debug('Successful new authentication')

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
            logging.debug('Received clientToken: ' + jsonResponse['clientToken'])
            self.clientToken = jsonResponse['clientToken']	#receive undashed
            self.profileIdentifier = jsonResponse['selectedProfile']['id']
            self.playerName = jsonResponse['selectedProfile']['name']
            self.authenticated = True
            self.validClientToken = True

    def validate(self):
	logging.debug('Validating session...')
        param = {
            "accessToken": self.accessToken,
            "clientToken": dash(self.clientToken) #Dashed
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
	logging.debug('Saving profile data to file.')
        data = {
            "profiles": {   
                self.playerName: {
                    "name": self.playerName
                }
            },
            "selectedProfile": self.playerName,
            "clientToken": dash(self.clientToken),	#save as dashed
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
	logging.debug('Loading profile file.')
        f_obj = open(save_location, "r")
        loaded = json.loads(f_obj.read())
        f_obj.close()
        self.profileIdentifier = unDash(loaded['selectedUser'])
        logging.debug('Loaded clientToken: ' + loaded['clientToken'])
        self.clientToken = unDash(loaded['clientToken'])
        self.accessToken = loaded['authenticationDatabase'][self.profileIdentifier]['accessToken']
        self.playerName = loaded['authenticationDatabase'][self.profileIdentifier]['displayName']
	logging.debug('Loaded profile data for user: ' + self.playerName + ' ' + self.username)


def defaultrun():
	try:
	    obj = Login()
	    try:
		obj.loadauth()
	    except Exception as e:
		logging.exception("Could not load authenticate file! Reauthenticating...")
		obj.authenticate()

	    obj.validate()
#refreshing not working?
#	    if not obj.validClientToken:
#		logging.debug('No valid clientToken, refreshing...')
#		obj.refresh()

	    if not obj.authenticated:
		logging.debug('Profile does not seem to be authenticated! reauthenticating...')
		obj.authenticate()

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
	opts, args = getopt.getopt(sys.argv[1:],"h", ["cleanslate", "validate", "refresh"])
except getopt.GetoptError:
	print 'usage: mcAuth.py [-h] [--cleanslate] [--validate] [--refresh]'
	sys.exit(2)
for opt, arg in opts:
	if opt == "-h":
		print 'Usage: mcAuth.py [-h] [--cleanslate] [--validate] [--refresh]'
		print "    Run without parameters for normal execution"
		sys.exit()
	elif opt in ("--cleanslate"):
		cleanslate()
		sys.exit()
	elif opt in ("--validate"):
		obj = Login()
		obj.loadauth()
		obj.validate()
		sys.exit()
	elif opt in ("--refresh"):
		obj = Login()
		obj.loadauth()
		obj.refresh()
		obj.saveauth() 
		logging.debug('New accessToken is: ' + obj.accessToken)
		sys.exit()
defaultrun()

logging.info('Script execution came to an end')










