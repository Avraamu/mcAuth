import requests
import simplejson as json
import os.path
import base64

base_url = "https://authserver.mojang.com"
login_file = "testrun.json"     # ~/.minecraft/launcher_profiles.json
cred_file = "cred_file.txt"
clienttoken = "7660950e-7e03-4188-b6c1-8de5b640ced5"
authtries = 0

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

def authenticate_new(credentials, authtries):
    authtries += 1
    if authtries > 5:
        return "Failed!"
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
    try:
        if file_text["errorMessage"] == "Invalid credentials. Invalid username or password.":
            credentials = {}
            credentials["username"] = raw_input("Enter username: ")
            credentials["password"] = raw_input("Enter password: ")
            credentials["userid"] = "placeholder"
            save_cred(cred_file, credentials)
            authenticate_new(credentials, authtries)
    except:
        pass
    print "Successfully logged in with clienttoken: " + str(file_text["clientToken"])
    return file_text

def validate_cur_session(file_c, credentials):
    param = {
        "accessToken": file_c["authenticationDatabase"][credentials["userid"]]["accessToken"],
        "clientToken": file_c["clientToken"]
    }
    req = requests.post(base_url + "/refresh", data=json.dumps(param))
    print req.text
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
    credentials = load_cred(cred_file)
except:
    print "Error loading credential file!"
    credentials = {}
    credentials["username"] = raw_input("Enter username: ")
    credentials["password"] = raw_input("Enter password: ")
    credentials["userid"] = "placeholder"
    save_cred(cred_file, credentials)
    print "Saved! Retrying to load..."
    credentials = load_cred(cred_file)
    print "Success!"



file_c = load_file(login_file)
print file_c
print credentials
try:
    file_c = validate_cur_session(file_c, credentials)
    print "Session valid!"
except:
    print "Unable to refresh session, creating new session..."
    file_c = authenticate_new(credentials, authtries)
    print "Saving " + login_file
    save_file(login_file, file_c, credentials)

"""
try:
    file_c = load_file(login_file)
    file_c = validate_cur_session(file_c, credentials)
    print "Session valid!"

except:
    print "Session invalid, invalidating..."
    invalidate_cur_session(file_c, credentials)
    print "Creating new session..."
    file_c = authenticate_new(credentials, authtries)
    print "Created new session, saving..."
    save_file(login_file, file_c, credentials)
    print "Success!"
"""
"""
except:
    print "Error on loading %s" % login_file
    print "Creating new session..."
    file_c = authenticate_new(credentials, authtries)
    print "Created new session, saving..."
    credentials["userid"] = file_c["selectedProfile"]["id"]
    save_file(login_file, file_c, credentials)
    save_cred(cred_file, credentials)
    print "Success!"
"""
"""
credentials = {}
credentials["username"] = "philip.groet@gmail.com"
credentials["password"] = "(Fv!|vMe{TSv*5^z%ejYF%NZ5"
credentials["userid"] = "placeholder"
print credentials
save_cred(cred_file, credentials)
"""