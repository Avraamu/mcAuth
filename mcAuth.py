import requests
import simplejson as json
import os.path

base_url = "https://authserver.mojang.com"


class McSession(object):
    def __init__(self, file, username, password):
        self.file = file
        self.username = username
        self.password = password
        self.clienttoken = ""
        self.file_c = {}

    def load_file(self):
        if not os.path.exists(self.file):
            f_obj_tmp = open(self.file, "w")
            f_obj_tmp.write(" ")
            f_obj_tmp.close()
        f_obj = open(self.file, "r")
        file_c = f_obj.read()
        f_obj.close()
        return file_c

    def save_file(self):
        f_obj = open(self.file, "w")
        f_obj.write(McSession.load_file())
        f_obj.close()
        return "File %s saved!" % self.file

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
        req = requests.post(base_url + "/authenticate", data=json.dumps(param))
        return req

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

session = McSession("testrun.txt", "username", "password")
session.authenticate_new()
session.save_file()