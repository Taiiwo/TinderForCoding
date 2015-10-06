import pymongo
import hashlib
import json
from bson.objectid import ObjectId
from bson import json_util

roles = {
    "wd": "Website Development",
    "be": "Back-end Programming",
    "fe": "Front-end Programming",
    "ma": "Mobile App Development"
}

def register(req, user, passw, skills):
    skills = json.loads(skills)
    users = getColl('users')
    userData = {
        "user": user,
        "passw": sha512(passw),
        "skills": skills,
        "messages": []
    }
    if users.find({"user": user}).count() > 0:
        return "userTaken"
    elif len(user) < 140 and len(passw) >= 6 and len(passw) < 140:
        return users.insert(userData)
    else:
        return "error"

def submitIdea(req, projectName, projectDesc, ideaRoles):
    ideaRoles = json.loads(ideaRoles)
    projects = getColl('projects')
    project = {
        "projectName": projectName,
        "projectDesc": projectDesc,
        "devs": {},
        "devsApplied": {}
    }
    for role in roles:
        project['devs'][role] = {}
        project['devs'][role]['N'] = ideaRoles[role]['N']
        project['devs'][role]['S'] = ideaRoles[role]['S']
        project['devs'][role]['A'] = 0
    if len(projectName) < 140 and len(projectDesc) < 512:
        projects.insert(project)
        return 1
    else:
        return "error"

def login(req, user, passw):
    db = getColl('users')
    userD = db.find_one({"user": user})
    if userD['passw'] == sha512(passw):
        # User logged in. Gibbe (session) cookies
        userID = str(userD['_id'])
        del userD['_id']
        del userD['passw']
        #userD['_id'] = str(userD['_id'])
        #return userD['_id']
        return json.dumps({
            "session": sha512(str(userID) + sha512(passw)),
            "userID": userID,
            "details": userD
        })
    else:
        return False

### Here starts the auth-only functions. Make sure you check their session cookies!

def getProjects(req, userID, session):
    # get user deets
    db = getColl('users')
    user = db.find_one({'_id': ObjectId(userID)})
    # check if the session is legit
    if not auth(userID, session):
        return "Access Denied"
    # user is who they say they are. Continue to find them projects.
    # so it turns out that mongoDB uses JS to process where clauses, so we might aswell do it here
    # get all records in the DB
    projects = getColl('projects').find({})
    # sort through them
    appropriateProjects = {}
    for project in projects:
        skills = 0
        #return user
        for skill in user['skills']:
            # return str(project['devs'][skill + 'N']) + " >= " + str(0)
            # if the user has a skill level higher than that of required
            # level for the project and the project is not full
            if int(user['skills'][skill]) >= int(project['devs'][skill]['S']) and \
                    int(project['devs'][skill]["A"]) < int(project['devs'][skill]['N'])\
                    and int(project['devs'][skill]['N']) > 0:
                skills += 1
        if skills > 0:
            appropriateProjects[str(project['_id'])] = project
    # return a json object for the front end to parse
    del user['passw']
    return json.dumps({
        "projects": appropriateProjects,
        "user": user
    }, default=json_util.default)

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
    user = db.find_one({'_id': ObjectId(userID)})
    # check if the session is legit
    if user and session == sha512(str(user['_id']) + user['passw']):
        return True
    else:
        return False
