import requests
import simplejson as json

url = 'https://authserver.mojang.com'
username = 'philip.groet@gmail.com'
password = ';!(tGQUxENVE91:[cF*s)sekb'
save_location = '/home/philip/.minecraft/launcher_profiles.json'

def dash(string):
    return string[0:8] + '-' + string[8:12] + '-' + string[12:16] + '-' + string[16:20] + '-' + string[20:]

class Login:
    def __init__(self):
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
            "username": username,
            "password": password
        }
        response = requests.post(url + "/authenticate", data=json.dumps(param))
        if response.status_code != 200:
            # throw error
            self.authenticated = False
            self.validClientToken = False
        else:
            jsonResponse = json.loads(response.text)
            self.accessToken = jsonResponse['accessToken']
            self.clientToken = jsonResponse['clientToken']
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
            self.authenticated = False
            self.validClientToken = False
        else:
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
            "clientToken": self.clientToken
        }
        response = requests.post(url + '/validate', data=json.dumps(param))
        if response.status_code != 204:
            self.validClientToken = False
        else:
            self.validClientToken = True

    def save(self):
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
                    "username": username,
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
        f_obj = open(save_location+'2', "w")
        f_obj.write(json.dumps(data))
        f_obj.close()


obj = Login()
obj.authenticate()
obj.save()