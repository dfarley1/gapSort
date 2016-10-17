# -*- coding: utf-8 -*-
# try something like

def index():
    return dict(message="hello from group.py")

@auth.requires_login()
def name():
    form = SQLFORM(db.groups, fields=['name'])
    form.vars.manager = auth.user.id
    if form.process(onvalidation=exists).accepted:
        #ID = db.groups.insert(manager = auth.user.id)
        db.user_groups.insert(user_id = auth.user.id, group_id = form.vars.id)
        session.groupName = form.vars.name  #saving the groupName for the next page
        redirect('create')
        print "This is a new group"
    return dict(form=form)


def create():
    #getting the ID of the group name
    rows = db().select(db.groups.ALL)
    for row in rows:
        if(row.name == session.groupName):
            groupID = row.id

    form=FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    if form.process().accepted:
       session.flash = 'record inserted'
       insertMember(form,groupID)
    users = []
    users = displayGroup(groupID)
    return dict(form=form, users = users)

def insertMember(form,groupID):
    email = form.vars.email   #getting the email from the form
    #finds the users email
    rows = db().select(db.auth_user.ALL)
    for row in rows:
        if(row.email == email):
            print "its a match"
            print row.first_name
            db.user_groups.insert(user_id = row.id, group_id = groupID) #inserts the user into the group
    return dict()


#this function finds if a group is already exists by that manager
def exists(form):
    Name = form.vars.name
    manager = auth.user.id
    rows = db().select(db.groups.ALL)
    for row in rows:
        if(row.name == Name and row.manager == manager):
            return True
    return False

def displayGroup(groupID):
    #NAME = db.groups(db.groups.group_id == groupID)
    print "THESE ARE THE GROUP MEMEBERS"
    names = db(db.user_groups.group_id == groupID).select()
    users = []
    for name in names:
        userName =  db.auth_user(name.user_id)
        print userName.first_name 
        users.append(userName)
    
    #UserID = db().select(db.auth_user.ALL)
    #for ID in UserID:
        #if(UserID == groupID):
    return users  

def user(): return dict(form=auth())






#select id form users where email = email