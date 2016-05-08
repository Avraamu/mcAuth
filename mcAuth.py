#!/usr/bin/python

import sys
import getopt
import requests
import simplejson as json
import uuid
import os
import logging

proxy = {
    #'http': 'http://pg-webserver:30264'
}
useproxy = 0

url = 'https://authserver.mojang.com'
save_location = os.path.expanduser('~') + '/.minecraft/launcher_profiles.json'
cred_location = os.path.expanduser('~') + '/mcAuth/cred.json'
log_location = os.path.expanduser('~') + '/mcAuth/mcAuth.log'

logging.basicConfig(filename=log_location, level=logging.DEBUG)
logging.debug('\n\n***Starting script!')


def dash(string):
    return string[0:8] + '-' + string[8:12] + '-' + string[12:16] + '-' + string[16:20] + '-' + string[20:]


def unDash(string):
    return string.replace('-', '')

def isDashed(string):
    if string[8] == '-':
        return True
    else:
        return False

class Login:
    def __init__(self):
        self.loadcred()
        self.credLoaded = False
        self.profileLoaded = False
        self.authenticated = False
        self.clientToken = '' #Always dashed, except for bug in /authenticate endpoint
        self.accessToken = '' #Always dashed
        self.profileIdentifier = '' #Always dashed except for in selected_profile
        self.playerName = ''
        self.username = ''
        self.password = ''
        self.mojangid = ''
    
    def loadcred(self):
        try:
            if os.path.isfile(cred_location):
                f_obj = open(cred_location, 'r+')
                userpass = json.loads(f_obj.read())
                f_obj.close()
                self.username = userpass['username']
                self.password = userpass['password']
                if not 'mojangid' in userpass:
                    self.getmojangid()
                else:
                    self.mojangid = userpass['mojangid']
                logging.debug('Loaded credentials: ' + str(userpass))
                self.credLoaded = True
            else:
                logging.error('Could not find cred.json file...')
                self.credLoaded = False
        except:
            logging.error('Unknown error on credential loading!')
            self.credLoaded = False

    def savecred(self):
        userpass = {}
        userpass['username'] = self.username
        userpass['password'] = self.password
        userpass['mojangid'] = self.mojangid #undashed
        f_obj = open(cred_location, 'w+')
        f_obj.write(json.dumps(userpass))
        f_obj.close()

    def getmojangid(self):  #Need a valid accessToken for this to work
        headers = {'Authorization': 'Bearer ' + self.accessToken}
        response = requests.get('https://api.mojang.com/user', headers=headers, proxies=proxy)
        if response.status_code != 200:
            logging.error('Could not get mojangid: ' + response.text)
        else:
            self.mojangid = json.loads(response.text)['id']
            logging.debug('Got mojangid!: ' + self.mojangid)

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
            param["clientToken"] = self.clientToken
            logging.debug('Authenticating using existing clientToken: ' + self.clientToken)
        else:
            self.clientToken = uuid.uuid4().urn[9:]
            param['clientToken'] = self.clientToken
            logging.debug('No clientToken found, mew clientToken: ' + self.clientToken)

        response = requests.post(url + "/authenticate", data=json.dumps(param), proxies=proxy)
        if response.status_code != 200:
            # throw error
            logging.error('Could not authenticate! ' + response.text)
            self.authenticated = False
        else:
            jsonResponse = json.loads(response.text)
            logging.debug('Received accessToken: ' + jsonResponse['accessToken'])
            self.accessToken = jsonResponse['accessToken']
            logging.debug('Received clientToken: ' + jsonResponse['clientToken'])   #receive as dashed or undashed if clienttoken was not supplied on initial request
            if isDashed(jsonResponse['clientToken']):
                self.clientToken = jsonResponse['clientToken']
            else:
                self.clientToken = dash(jsonResponse['clientToken'])
            logging.debug('New clienToken: ' + self.clientToken)
            self.profileIdentifier = jsonResponse['availableProfiles'][0]['id']
            self.playerName = jsonResponse['availableProfiles'][0]['name']
            logging.debug('Successful new authentication (new clienttoken: ' + self.clientToken)
            self.authenticated = True

    def refresh(self):
        param = {
            "accessToken": self.accessToken,
            "clientToken": self.clientToken,
            "selectedProfile": {
                "id": self.profileIdentifier,
                "name": self.playerName
            }
        }
        response = requests.post(url + '/refresh', data=json.dumps(param), proxies=proxy)
        if response.status_code != 200:
            # throw error
            logging.error('Could not refresh!')
            self.authenticated = False
        else:
            logging.debug('Successful refresh!')
            jsonResponse = json.loads(response.text)
            self.accessToken = jsonResponse['accessToken']
            logging.debug('Received clientToken: ' + jsonResponse['clientToken'])
            self.clientToken = jsonResponse['clientToken']  #receive undashed
            self.profileIdentifier = jsonResponse['selectedProfile']['id']
            self.playerName = jsonResponse['selectedProfile']['name']
            self.authenticated = True
            self.validAccessToken = True

    def validate(self):
        logging.debug('Validating session with accessToken: ' + self.accessToken + ' and clientToken: ' + self.clientToken)
        param = {
            "accessToken": self.accessToken,
            "clientToken": self.clientToken #Dashed
        }
        response = requests.post(url + '/validate', data=json.dumps(param), proxies=proxy)
        if response.status_code != 204:
            self.authenticated = False
            logging.error('Token could not be validated!')
        else:
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
            "clientToken": self.clientToken,    #save as dashed
            "authenticationDatabase": {
                self.profileIdentifier: {
                    "username": self.username,
                    "accessToken": self.accessToken,
                    "userid": self.mojangid,
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
        try:
            logging.debug('Loading profile file.')
            f_obj = open(save_location, "r")
            loaded = json.loads(f_obj.read())
            f_obj.close()
            self.profileIdentifier = loaded['selectedUser']
            logging.debug('Loaded clientToken: ' + loaded['clientToken'])
            self.clientToken = loaded['clientToken']
            self.accessToken = loaded['authenticationDatabase'][self.profileIdentifier]['accessToken']
            self.mojangid = loaded['authenticationDatabase'][self.profileIdentifier]['userid']
            self.playerName = loaded['authenticationDatabase'][self.profileIdentifier]['displayName']

            if self.mojangid == '':
                self.getmojangid()
            logging.debug('Loaded profile data for user: ' + self.playerName + ' ' + self.username + ' ' + self.mojangid)
            self.profileLoaded = True
        except Exception as e:
            logging.error('Unable to load profile file...' + str(e))
            self.profileLoaded = False

    def cleanslate(self):
        try:
            logging.debug('Cleanslate...')
            self.clientToken = ''
            self.authenticate()
            self.saveauth()
        except:
            logging.exception('Failed to authencticate :(, not saving.')


def defaultrun():
    logging.debug('Default run...')
    
    try:
        obj.loadcred()
        if not obj.credLoaded:
            logging.exception('Unable to load credential file, giving up...')
        else:
            obj.loadauth()
            if not obj.profileLoaded:
                logging.error("Could not load profile file! Reauthenticating...")
                obj.cleanslate()
                logging.exception('Cleanslated')
            else:
                obj.validate()
                if not obj.authenticated:
                    logging.error('Profile does not seem to be authenticated! reauthenticating...')
                    obj.authenticate()
                    obj.saveauth()
    finally:
        logging.error('sys exec info: ' + str(sys.exc_info()[0]))
            
        logging.debug('Attempting minecraft launch...')
        os.system('java -jar ~/mcAuth/Minecraft.jar')
        logging.debug('Launcher seems to have been closed!')



#refreshing not working?
#       if not obj.validClientToken:
#       logging.debug('No valid clientToken, refreshing...')
#       obj.refresh()




helpstring = 'usage: mcAuth.py [-h] [--update] [--ct=CLIENTTOKEN] [--newprofile] [--cleanslate] [--validate] [--refresh] [--getmojangid]\n    Run without parameters for normal execution'

try:
    opts, args = getopt.getopt(sys.argv[1:],"h", ['ct=', 'update', 'newprofile', 'cleanslate', 'cs', 'validate', 'refresh', 'getmojangid'])
except getopt.GetoptError:
    print helpstring
    sys.exit(2)

obj = Login()
for opt, arg in opts:
    if opt == '-h':
        print helpstring
        sys.exit()

    if opt in ('--ct'):
        obj.clientToken = arg

    if opt in ('--newprofile'):
        print 'Username: '
        obj.username = raw_input()
        print 'Password: '
        obj.password = raw_input()
        obj.authenticate()
        if obj.authenticated:
            obj.getmojangid()
            obj.savecred()
            obj.saveauth()
            logging.debug('Seem to have authenticated!')
        else:
            logging.debug('Incorrect username or password')
        sys.exit()
    elif opt in ('--getmojangid'):
        obj.loadauth()  #Need a valid accessToken
        obj.getmojangid()
        obj.saveauth()  #Save mojangid to file

        f_obj = open(cred_location, 'r+')   #Read credentials, update, save
        contents = f_obj.read()
        contents = json.loads(contents)
        contents['mojangid'] = obj.mojangid
        f_obj.seek(0)
        f_obj.write(json.dumps(contents))
        f_obj.close()

        sys.exit()
    elif opt in ('--cleanslate', '--cs'):
        obj.cleanslate()
        sys.exit()
    elif opt in ('--validate'):
        obj.loadauth()
        obj.validate()
        sys.exit()
    elif opt in ('--refresh'):
        obj.loadauth()
        obj.refresh()
        obj.saveauth() 
        logging.debug('New accessToken is: ' + obj.accessToken)
        sys.exit()

defaultrun()

logging.info('Script execution came to an end')










