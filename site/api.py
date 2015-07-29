import pymongo
import hashlib

def register(req, email, passw, wd, be, fe, mad):
   client = MongoClient('localhost', 27017)
   db = client.coder8
   users = db.users
   data = {
          "email": email,
          "passw": sha512(passw),
          
          }
    return "%s, %s, %s, %s, %s, %s" % (email, passw, wd, be, fe, mad)

def sha512(string):
    return hashlib.sha512(string).hexdigest()
