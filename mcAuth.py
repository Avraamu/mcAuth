import requests
import simplejson as json
import os.path

base_url = "https://authserver.mojang.com"
login_file = "testrun.json"     # ~/.minecraft/launcher_profiles.json
cred_file = "cred_file.json"
clienttoken = "7660950e-7e03-4188-b6c1-8de5b640ced5"


def load_cred(cred_file):
    if not os.path.exists(cred_file):
        f_obj_tmp = open(cred_file, "w")
        f_obj_tmp.write(" ")
        f_obj_tmp.close()
    f_obj = open(cred_file, "r")
    credentials = json.loads(f_obj.read())
    f_obj.close()
    return credentials

def load_file(file_name):     # load the login file
    if not os.path.exists(file_name):
        f_obj_tmp = open(file_name, "w")
        f_obj_tmp.write(" ")
        f_obj_tmp.close()
    f_obj = open(file_name, "r")
    file_c = f_obj.read()
    f_obj.close()
    return file_c

def save_file(file_name, file_c, clienttoken, username):   # save login file
    param = {           #Formatted according to http://wiki.vg/Authentication
        "profiles": {
            "Minecraft": {
                "name": file_c["selectedProfile"]["name"],
                "lastVersionId": "1.7.9",
                "playerUUID": clienttoken
            }
        },
        "selectedProfile": file_c["selectedProfile"]["name"],
        "clientToken": clienttoken,
        "authenticationDatabase": {
            file_c["selectedProfile"]["id"]: {
                "username": username,
                "accessToken": file_c["accessToken"],
                "userid": file_c["selectedProfile"]["id"],
                "uuid": clienttoken,
                "displayName": file_c["selectedProfile"]["name"]
            }
        }
    }
    f_obj = open(file_name, "w")
    f_obj.write(json.dumps(param))
    f_obj.close()
    return "File %s saved!" % file_name

def authenticate_new(username, password, clienttoken):
    param = {
        "agent": {
            "name": "Minecraft",
            "version": 1
        },
        "username": username,
        "password": password,
        "clientToken": clienttoken
    }
    file_c_tmp = requests.post(base_url + "/authenticate", data=json.dumps(param))
    file_c_tmps = file_c_tmp.text
    file_text = json.loads(file_c_tmps)
#    if file_text["errorMessage"]:
#        print "Failed with error: %s" % file_text["errorMessage"]
    print file_text
    return file_text

def validate_cur_session(file_c):
    param = {
        "accessToken": file_c["accessToken"]
    }
    req = requests.post(base_url + "/validate", data=json.dumps(param))
    if req.text == "":
        return True
    else:
        return False

def invalidate_cur_session(username, clienttoken, file_c):
    param = {
        "accessToken": file_c["accessToken"],
        "clientToken": clienttoken
    }
    req = requests.post(base_url + "/invalidate", data=json.dumps(param))
    if req.text == "":
        return "Session Invalidated!"
    else:
        return "Failed"

credentials = load_cred(cred_file)
file_c = authenticate_new(credentials["username"], credentials["password"], "clienttoken")
print save_file(login_file, file_c, clienttoken, credentials["username"])