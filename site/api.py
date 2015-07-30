import pymongo
import hashlib
import json

def register(req, user, passw, wd, be, fe, mad):
    client = pymongo.MongoClient('localhost', 27017)
    db = client.coder8
    users = db.users
    data = {
        "user": user,
        "passw": sha512(passw),
        "skills": {
            "wd": wd,
            "be": be,
            "fe": fe,
            "mad": mad
        }
    }
    if users.find({"user": user}):
        return "userTaken"
    elif len(user) < 140 and len(passw) > 6 and len(passw) < 140:
        users.insert(data)
        return 1
    else:
        return "error"
def sha512(string):
    return hashlib.sha512(string).hexdigest()
