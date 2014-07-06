import requests
import simplejson as json
import base64
global debug

base_url = "https://authserver.mojang.com"
login_file = "testrun.json"     # ~/.minecraft/launcher_profiles.json
cred_file = "cred_file.txt"
debug = True
#clienttoken = "7660950e-7e03-4188-b6c1-8de5b640ced5"


def load_cred(cred_file):
    f_obj = open(cred_file, "r")
    credentials = json.loads(base64.b64decode(f_obj.read()))
    f_obj.close()
    return credentials


def save_cred(cred_file, credentials):
    f_obj = open(cred_file, "w")
    print(json.dumps(credentials))
    f_obj.write(base64.b64encode(json.dumps(credentials)))
    f_obj.close()


def ask_credentials():
    credentials = {}
    credentials["username"] = raw_input("Enter username: ")
    credentials["password"] = raw_input("Enter password: ")
    credentials["userid"] = "useridplaceholder"
    return credentials


def load_file(file_name):     # load the login file
    f_obj = open(file_name, "r")
    file_c = json.loads(f_obj.read())
    f_obj.close()
    return file_c


def output_to_file(file_name, file_c, credentials):   # save login file
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
    if debug:
        print "Successfully converted and saved login_file"
    return True


def org_to_file(login_file, file_c):
    f_obj = open(login_file, "w")
    f_obj.write(json.dumps(file_c))
    f_obj.close()


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
    file_c_tmp = file_c_tmp.text
    file_text = json.loads(file_c_tmp)
    #    if file_text["errorMessage"]:
    #        print "Failed with error: %s" % file_text["errorMessage"]
    if debug:
        print("Received: " + str(file_text))
    return file_text


def validate_cur_session(file_c, credentials):
    param = {
        "accessToken": file_c["authenticationDatabase"][credentials["userid"]]["accessToken"],
        "clientToken": file_c["clientToken"]
    }
    req = requests.post(base_url + "/refresh", data=json.dumps(param))
    if debug:
        print("Received: " + req.text)
    reqs = json.loads(req.text)
    file_c["authenticationDatabase"][credentials["userid"]]["accessToken"] = reqs["accessToken"]
    if debug:
        print "Session valid!"
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

if debug:
    print "Debugging enabled!"

try:
    credentials = load_cred(cred_file)
    if debug:
        print "Loaded credentials"
except:
    if debug:
        print "credential file error, making new"
    credentials = ask_credentials()
    save_cred(cred_file, credentials)

"""
file_c = load_file(login_file)
file_c_tmp = validate_cur_session(file_c, credentials)
org_to_file(login_file, file_c_tmp)
"""
try:
    file_c = load_file(login_file)
    try:
        file_c = validate_cur_session(file_c, credentials)
        org_to_file(login_file, file_c)
    except:
        if debug:
            print "Error refreshing session! Making new session"
        file_c = authenticate_new(credentials)
        output_to_file(login_file, file_c)
except:
    if debug:
        print "Error login file, making new session"
    file_c = authenticate_new(credentials)
    credentials["userid"] = file_c["selectedProfile"]["id"]
    save_cred(cred_file, credentials)
    output_to_file(login_file, file_c, credentials)
    if debug:
        print file_c


