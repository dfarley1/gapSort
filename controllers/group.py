# -*- coding: utf-8 -*-
# try something like

def index():
    return dict(message="hello from group.py")

#Name the group
@auth.requires_login()
def name():
    manager = auth.user.id
    form = SQLFORM(db.groups, fields=['name'])
    form.vars.manager = manager
    if form.process(onvalidation=exists).accepted:
        group_id = form.vars.id
        db.user_groups.insert(user_id = manager, group_id = group_id)
        session.groupName = form.vars.name  #saving the groupName for the next page
        redirect(URL('edit', args=(group_id)))
        print "This is a new group"
    group_names = db(db.groups.manager == manager).select()  
    return dict(form=form, group_names=group_names)

#creates a group and allows you to add users to the group
def create():
    #getting the ID of the group name
    group_id = request.args(0)
    form=FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    
    if form.process().accepted:
       session.flash = 'record inserted'
       insert_user(form,group_id)
    users = []
    users = displayGroup(group_id)
    return dict(form=form, users = users, group_id = group_id)

#allows the manager to edit the group
def edit():
    group_id = request.args(0)
    edit_name_form = SQLFORM(db.groups, 
        group_id, 
        fields=['name', 'gap_length'], 
        labels={'name':'Group Name:', 'gap_length':'Minimum gap length (minutes):'},
        showid=False, 
        _class='editName')
    add_user_form = FORM('Email address: ', INPUT(_name='email'), INPUT(_type = 'submit'))
    
    if edit_name_form.process().accepted:
        session.flash = 'record updated'
        db.executesql("""UPDATE groups
                        SET name = '%s'
                        WHERE id = '%s' """ %(edit_name_form.vars.name, group_id))
    if add_user_form.process().accepted:
       session.flash = 'record inserted'
       insert_user(add_user_form,group_id)
    users = []
    users = display_group(group_id) 
    manager_id = auth.user.id
    return dict(edit_name_form = edit_name_form, add_user_form = add_user_form , users = users, 
                group_id=group_id, manager_id = manager_id)

#deletes a group from the database
def delete_group():
    group_id = request.args(0)
    print group_id
    db.executesql("""DELETE FROM groups
                    WHERE id = '%s' """ %(group_id))
    db.executesql("""DELETE FROM user_groups
                    WHERE group_id = '%s' """ %(group_id))
    redirect(URL('my_groups'))
    dict()

#inserts a user into a given group
def insert_user(form,group_id):
    email = form.vars.email   #getting the email from the form
    print email
    #finds the users email
    rows = db().select(db.auth_user.ALL)
    for row in rows:
        if(row.email == email):
            print "its a match"
            print row.first_name
            db.user_groups.insert(user_id = row.id, group_id = group_id) #inserts the user into the group
    return dict()



#this function finds if a group is already exists by that manager
def exists(form):
    name = form.vars.name
    manager = auth.user.id
    rows = db().select(db.groups.ALL)
    for row in rows:
        if(row.name == name and row.manager == manager):
            return True
    return False

#displays the memebers in a given group id
def display_group(group_id):
    names = db(db.user_groups.group_id == group_id).select()
    users = []
    for name in names:
        user_name =  db.auth_user(name.user_id)
        users.append(user_name)
    return users  

@auth.requires_login()
def my_groups():
    user_groups = db(db.user_groups.user_id == auth.user.id).select()  
    groups = []
    for user_group in user_groups:
        groups.append(db.groups(user_group.group_id))
    return dict(groups = groups)

def delete_user_from_group():
    group_id  = request.args(0)
    user_email = request.args(1)
    print user_email
    print group_id
    user = db(db.auth_user.email == user_email).select()
    user_id = user[0].id
    db.executesql("""DELETE FROM user_groups
                    WHERE user_id = '%s' AND group_id = '%s'""" %(user_id,group_id))
    
    redirect(URL('edit', args=(group_id)))
    return dict()

#inserts a user from the side list
def insert():
    print "I got into here"
    user_id = request.args(0)
    group_id = request.args(1)
    print user_id
    print group_id
    db.executesql("""INSERT INTO user_groups (user_id, group_id)
                    VALUES ('%s','%s')""" %(user_id,group_id))
    return dict()

def all_users():
    group_id = request.args(0)
    manager_id = request.args(1)
    users = db().select(db.auth_user.ALL)
    return dict(group_id = group_id, manager_id = manager_id ,users = users)

def user(): return dict(form=auth())
