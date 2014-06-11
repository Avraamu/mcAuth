import requests
import simplejson as json
import os.path
import base64

base_url = "https://authserver.mojang.com"
login_file = "testrun.json"     # ~/.minecraft/launcher_profiles.json
cred_file = "cred_file.json"
clienttoken = "7660950e-7e03-4188-b6c1-8de5b640ced5"


def load_cred(cred_file):
    if not os.path.exists(cred_file):
        save_cred(cred_file)
    f_obj = open(cred_file, "r")
    credentials = json.loads(base64.b64decode(f_obj.read()))
    f_obj.close()
    return credentials

def save_cred(cred_file, credentials):
    f_obj = open(cred_file, "w")
    f_obj.write(base64.b64encode(json.dumps(credentials)))
    f_obj.close()

def load_file(file_name):     # load the login file
    if not os.path.exists(file_name):
        f_obj_tmp = open(file_name, "w")
        f_obj_tmp.write(" ")
        f_obj_tmp.close()
    f_obj = open(file_name, "r")
    file_c = json.loads(f_obj.read())
    f_obj.close()
    return file_c

def save_file(file_name, file_c, credentials):   # save login file
    param = {           #Formatted according to http://wiki.vg/Authentication
        "profiles": {
            "Minecraft": {
                "name": file_c["selectedProfile"]["name"],
                "lastVersionId": "1.7.9",
                "playerUUID": file_c["clientToken"]
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
    print "Received: " + str(file_text)
    print "Successfully logged in with clienttoken: " + str(file_text["clientToken"])
    return file_text

def validate_cur_session(file_c, credentials):
    param = {
        "accessToken": file_c["authenticationDatabase"][credentials["userid"]]["accessToken"]
    }
    req = requests.post(base_url + "/validate", data=json.dumps(param))
    if req.text == "":
        return True
    else:
        return False

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


credentials = load_cred(cred_file)
file_c = load_file(login_file)

print file_c
if validate_cur_session(file_c, credentials) == False:
    print "Session invalid, invalidating..."
    invalidate_cur_session(file_c, credentials)
    print "Creating new session..."
    file_c = authenticate_new(credentials)
    print "Created new session, saving..."
    save_file(login_file, file_c, credentials)
    print "Success!"
else:
    print "Session valid!"

"""
credentials = {}
credentials["username"] = "philip.groet@gmail.com"
credentials["password"] = "?9,U]%ZTmDnKOv27.q{oJq!9|"
credentials["userid"] = "74e783c33ec044cf854958b137695625"
print credentials
save_cred(cred_file, credentials)
"""