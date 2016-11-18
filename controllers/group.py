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
        groupID = form.vars.id
        db.user_groups.insert(user_id = auth.user.id, group_id = groupID)
        session.groupName = form.vars.name  #saving the groupName for the next page
        redirect(URL('edit', args=(groupID)))
        print "This is a new group"

    # groupNames = db.executesql("""SELECT name FROM groups
    #                             WHERE manager = ('%s')""" %(auth.user.id))
    groupNames = db(db.groups.manager == auth.user.id).select()
    
    return dict(form=form, groupNames=groupNames)

#creates a group and allows you to add users to the group
def create():
    #getting the ID of the group name
    groupID = request.args(0)
    form=FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    
    if form.process().accepted:
       session.flash = 'record inserted'
       insertUser(form,groupID)
    users = []
    users = displayGroup(groupID)
    return dict(form=form, users = users, groupID = groupID)

#allows the manager to edit the group
def edit():
    groupID = request.args(0)
    editNameForm = SQLFORM(db.groups, 
        groupID, 
        fields=['name', 'gap_length'], 
        labels={'name':'Group Name:', 'gap_length':'Minimum gap length (minutes):'},
        showid=False, 
        _class='editName')
    addUserForm = FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    
    if editNameForm.process().accepted:
        session.flash = 'record updated'
        db.executesql("""UPDATE groups
                        SET name = '%s'
                        WHERE id = '%s' """ %(editNameForm.vars.name, groupID))
    if addUserForm.process().accepted:
       session.flash = 'record inserted'
       insertUser(addUserForm,groupID)
    users = []
    users = displayGroup(groupID) 

    return dict(editNameForm = editNameForm, addUserForm = addUserForm , users = users, groupID=groupID)

#deletes a group from the database
def deleteGroup():
    groupID = request.args(0)
    print groupID
    db.executesql("""DELETE FROM groups
                    WHERE id = '%s' """ %(groupID))
    db.executesql("""DELETE FROM user_groups
                    WHERE group_id = '%s' """ %(groupID))
    redirect(URL('myGroups'))
    dict()

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
    names = db(db.user_groups.group_id == groupID).select()
    users = []
    for name in names:
        userName =  db.auth_user(name.user_id)
        users.append(userName)
    return users  

@auth.requires_login()
def myGroups():
    user_groups = db(db.user_groups.user_id == auth.user.id).select()  
    groups = []
    for user_group in user_groups:
        groups.append(db.groups(user_group.group_id))
    
    return dict(groups = groups)

def deleteUserFromGroup():
    print "Group ID and user email"
    groupID  = request.args(0)
    userEmail = request.args(1)
    print userEmail
    print groupID
    user = db(db.auth_user.email == userEmail).select()
    userID = user[0].id
    db.executesql("""DELETE FROM user_groups
                    WHERE user_id = '%s' AND group_id = '%s'""" %(userID,groupID))
    
    redirect(URL('edit', args=(groupID)))
    return

def user(): return dict(form=auth())


#select id form users where email = email
