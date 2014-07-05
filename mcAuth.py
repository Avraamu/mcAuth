import requests
import simplejson as json
import os.path

base_url = "https://authserver.mojang.com"
login_file = "testrun.json"     # ~/.minecraft/launcher_profiles.json
cred_file = "cred_file.txt"
clienttoken = "7660950e-7e03-4188-b6c1-8de5b640ced5"
authtries = 0


def load_cred(cred_file):
    f_obj = open(cred_file, "r")
    credentials = json.loads(f_obj.read())
    f_obj.close()
    return credentials


def save_cred(cred_file, credentials):
    f_obj = open(cred_file, "w")
    print(json.dumps(credentials))
    f_obj.write(json.dumps(credentials))
    f_obj.close()


def ask_credentials():
    credentials = {}
    credentials["username"] = input("Enter username: ")
    credentials["password"] = input("Enter password: ")
    credentials["userid"] = "useridplaceholder"
    return credentials


def load_file(file_name):     # load the login file
    f_obj = open(file_name, "r")
    file_c = json.loads(f_obj.read())
    f_obj.close()
    return file_c


def save_file(file_name, file_c, credentials):   # save login file
    param = {                                                      #Formatted according to http://wiki.vg/Authentication
        "profiles": {
            file_c["selectedProfile"]["name"]: {
                "name": file_c["selectedProfile"]["name"],
                "playerUUID": file_c["selectedProfile"]["id"]
            }
        },
        "selectedProfile": file_c["selectedProfile"]["name"],
        "clientToken": file_c["clientToken"],
        "authenticationDatabase": {
            file_c["selectedProfile"]["id"]: {
                "username": credentials["username"],
                "accessToken": file_c["accessToken"],
                "userid": file_c["selectedProfile"]["id"],
                "uuid": file_c["clientToken"],
                "displayName": file_c["selectedProfile"]["name"]
            }
        }
    }
    f_obj = open(file_name, "w")
    f_obj.write(json.dumps(param))
    f_obj.close()
    return "File %s saved!" % file_name


def authenticate_new(credentials):
    param = {
        "agent": {
            "name": "Minecraft",
            "version": 1
        },
        "username": credentials["username"],
        "password": credentials["password"],
    }
    file_c_tmp = requests.post(base_url + "/authenticate", data=json.dumps(param))
    file_c_tmps = file_c_tmp.text
    file_text = json.loads(file_c_tmps)
    #    if file_text["errorMessage"]:
    #        print "Failed with error: %s" % file_text["errorMessage"]
    print("Received: " + str(file_text))
    return file_text


def validate_cur_session(file_c, credentials):
    param = {
        "accessToken": file_c["authenticationDatabase"][credentials["userid"]]["accessToken"],
        "clientToken": file_c["clientToken"]
    }
    req = requests.post(base_url + "/refresh", data=json.dumps(param))
    print(req.text)
    file_c["authenticationDatabase"][credentials["userid"]]["accessToken"] = req.text["accessToken"]
    return file_c


def invalidate_cur_session(file_c, credentials):
    param = {
        "accessToken": file_c["authenticationDatabase"][credentials["userid"]]["accessToken"],
        "clientToken": file_c["clientToken"]
    }
    req = requests.post(base_url + "/invalidate", data=json.dumps(param))
    if req.text == "":
        return "Session Invalidated!"
    else:
        return "Failed"


try:
    file_c = load_cred(cred_file)
    print "Credentials Successfully loaded!"
except:
    print "Error on loading credentials!"
    credentials = ask_credentials()

try:
    load_file(login_file)
    print "Success loading file"
except:
    f_obj = open(login_file, "w")
    f_obj.write(authenticate_new(credentials))

validate_cur_session(file_c, credentials)
