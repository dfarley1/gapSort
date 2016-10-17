# -*- coding: utf-8 -*-
# try something like
def index(): return dict(message="hello from schedule.py")

@auth.requires_login()
def add():
    #look up all events that belong to this user
    #return them all
    form = SQLFORM(db.events, fields=['start_time', 'end_time', 'description', 'name'])
    form.vars.user_id = auth.user.id
    if form.process().accepted:
        redirect('../default/index')
    return dict(form=form)
