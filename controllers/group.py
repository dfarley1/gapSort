# -*- coding: utf-8 -*-
# try something like

def index():
    return dict(message="hello from group.py")

#Name the group
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

#creates a group and allows you to add users to the group
def create():
    #getting the ID of the group name
    rows = db().select(db.groups.ALL)
    for row in rows:
        if(row.name == session.groupName):
            groupID = row.id

    form=FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    
    if form.process(onvalidation=isUser).accepted:
       session.flash = 'record inserted'
       insertUser(form,groupID)
    users = []
    users = displayGroup(groupID)
    return dict(form=form, users = users)

#allows the manager to edit the group
def edit():
    print "this is the group"
    groupID = request.args(0)
    editNameForm = SQLFORM(db.groups, groupID, fields=['name'])
    addUserForm = FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    if editNameForm.process().accepted:
        session.flash = 'record updated'
        db.executesql("""UPDATE groups
                        SET name = '%s'
                        WHERE id = '%s' """ %(form.vars.name, groupID))
    if addUserForm.process(onvalidation=isUser).accepted:
       session.flash = 'record inserted'
       insertUser(addUserForm,groupID)
    users = []
    users = displayGroup(groupID) 

    # users = []
    # membersID = db.executesql("""SELECT id
    #                         FROM user_groups
    #                         WHERE (group_id = '%s') """ %(groupID))
    # for ID in membersID:
    #     userSQl = db.executesql("""SELECT id
    #                         FROM auth_user
    #                         where (id = '%s') """ %(ID.user_id))
    #     users.append(userSQl)

    return dict(editNameForm = editNameForm, addUserForm = addUserForm ,users = users)

def isUser(form):
    member = db.executesql("""SELECT id
                            FROM auth_user
                            WHERE (email = '%s')""" %(form.vars.name))
    # if member:
    #     form.errors.email = 'not a user'

#inserts a user into a given group
def insertUser(form,groupID):
    email = form.vars.email   #getting the email from the form
    print email
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

#displays the memebers in a given group id
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

@auth.requires_login()
def myGroups():
    user_groups = db(db.user_groups.user_id == auth.user.id).select()  
    groups = []
    for user_group in user_groups:
        groups.append(db.groups(user_group.group_id))
    
    return dict(groups = groups)

def deleteUserFromGroup():
    # isManager = db.executesql("""SELECT id 
    #                         FROM groups
    #                         WHERE manager = '%s' AND id = '%s' == """%(userID,groupID))
    # if isManager:
    #     print "THIS is the manager"
    # else:
    # db.executesql("""DELETE FROM user_groups
    #                 WHERE  user_id = '%s' AND group_id = '%s'""" %(userID,groupID))
    print "got into here"
    redirect('edit')
def user(): return dict(form=auth())


#select id form users where email = email
