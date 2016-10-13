# -*- coding: utf-8 -*-
# try something like
import datetime

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

def myschedule():
    date = datetime.date.today()
    events = db(db.events.user_id == auth.user.id).select();
    weekdays = week   = ['Sunday', 
              'Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday']
    return dict(date=date, events=events, weekdays=weekdays)
