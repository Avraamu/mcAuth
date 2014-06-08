import requests
import simplejson as json
import os.path

base_url = "https://authserver.mojang.com"
login_file = "testrun.txt"
username = ""
password = ""
file = "~/.minecraft/launcher_profiles.json"


class McSession(object):
    def __init__(self, file_name, username, password):
        self.file_name = file_name
        self.username = username
        self.password = password
        self.clienttoken = ""
        self.file_c = {}

    def load_file(self):
        if not os.path.exists(self.file_name):
            f_obj_tmp = open(self.file_name, "w")
            f_obj_tmp.write(" ")
            f_obj_tmp.close()
        f_obj = open(self.file_name, "r")
        file_c = f_obj.read()
        f_obj.close()
        return file_c

    def save_file(self):
        f_obj = open(self.file_name, "w")
        f_obj.write(json.dumps(self.file_c.text))
        f_obj.close()
        return "File %s saved!" % self.file_name

    def authenticate_new(self):
        param = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": self.username,
            "password": self.password,
            "clientToken": self.clienttoken
        }
        self.file_c = requests.post(base_url + "/authenticate", data=json.dumps(param))
        print self.file_c.text

    def validate_cur_session(self):
        param = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": self.username,
            "password": self.password,
            "clientToken": self.clienttoken
        }
        req = requests.post(base_url + "/validate", data=json.dumps(param))
        if req.text == "":
            return True
        else:
            return False

    def invalidate_cur_session(self):
        param = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": self.username,
            "password": self.password,
            "clientToken": self.clienttoken
        }
        requests.post(base_url + "/invalidate", data=json.dumps(param))
        return "Session Invalidated!"

session = McSession(login_file, username, password)
session.authenticate_new()
session.save_file()