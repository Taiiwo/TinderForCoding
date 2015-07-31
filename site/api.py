import pymongo
import hashlib
import json

def register(req, user, passw, wd, be, fe, mad):
    users = getColl('users')
    userData = {
        "user": user,
        "passw": sha512(passw),
        "skills": {
            "wd": wd,
            "be": be,
            "fe": fe,
            "ma": mad
        },
        "messages": []
    }
    if users.find({"user": user}):
        return users.find({"user": user})
    elif len(user) < 140 and len(passw) > 6 and len(passw) < 140:
        users.insert(userData)
        return 1
    else:
        return "error"

def submitIdea(req, projectName, projectDesc, wdS, beS, feS, maS, wdN, beN, feN, maN):
    projects = getColl('projects')
    project = {
        "projectName": projectName,
        "projectDesc": projectDesc,
        "devs": {
            "wdN": wdN,
            "wdS": wdS,
            "wdA": 0,
            "beN": beN,
            "beS": beS,
            "beA": 0,
            "feN": feN,
            "feS": feS,
            "feA": 0,
            "maN": maN,
            "maS": maS
            "maA": 0,
        },
        "devsApplied": {}
    }
    if len(projectName) < 140 and len(projectDesc) < 512:
        projects.insert(project)
        return 1
    else:
        return "error"

def login(req, user, passw):
    db = getColl('users')
    userD = db.find({"user": user})
    if userD['passw'] == sha512(passw):
        # User logged in. Gibbe (session) cookies
        return json.dumps({
            "session": sha512(userD['_id'] + userD['passw']),
            "userID": userD['_id'],
            "details": userD
        })

### Here starts the auth-only functions. Make sure you check their session cookies!

def getProjects(req, userID, session):
    # get user deets
    db = getColl('users')
    user = db.find({'_id': userID})
    # check if the session is legit
    if not auth(userID, session):)
        return "Access Denied"
    # user is who they say they are. Continue to find them projects.
    # so it turns out that mongoDB uses JS to process where clauses, so we might aswell do it here
    # get all records in the DB
    projects = getColl('projects').find({})
    # sort through them
    appropriateProjects = []
    for project in projects:
        skills = 0
        for skill in user['skills']:
            # if the user has a skill level higher than that of required
            # level for the project and the project is not full
            if user['skills'][skill] >= project['devs'][skill + 'S'] and \
                    project['devs'][skill + "A"] < project['devs'][skill + 'N']:
                appropriateProjects.append(project)
                break
    # return a json object for the front end to parse
    return json.loads(appropriateProjects)

def selectProject(req, userID, session, projectID, position):
    if not auth(userID, session):
        return "access denied"
    db = getColl('projects')
    project = db.find({"_id": projectID})
    devs = project['devs']
    # add a developer to the project
    devs.update({
        position + "A": devs[position + 'A'] + 1
    })
    project['devsApplied'].update({userID: position})
    # Now check if there are enough devs to get started:
    user = getColls('users').find({'_id': userID})
    skills = 0
    for skill in user['skills']:
        if project['devs'][skill + 'A'] >= project['devs'][skill + 'N']:
            skills += 1
    if skills == len(user['skills']):
        # Do stuff to start the project.
        # maybe send messages to the users. We could do that.
        for user in project['devsApplied']:
            dev = getColls('users').find({'_id': userID})
            dev.messages.insert("You have been chosen to work on " + project['projectName'])
        # We still need a way for them to be able to contact eachother. A cheap way would be to
        # send them to an tiny chat or something with the ID of the project.

### Here ends the auth-only functions. Make sure you check their session cookies!

def sha512(string):
    return hashlib.sha512(string).hexdigest()

def getColl(name):
    client = pymongo.MongoClient('localhost', 27017)
    db = client.coder8
    return db[name]

def auth(userID, session):
    # get user deets
    db = getColl('users')
    user = db.find({'_id': userID})
    # check if the session is legit
    if not session == sha512(userD['_id'] + userD['passw']):
        return False
