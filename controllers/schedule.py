# -*- coding: utf-8 -*-
# try something like
import datetime
from gluon import DAL, Field
from collections import namedtuple

def index(): return dict(message="hello from schedule.py")

@auth.requires_login()
def add():
    #look up all events that belong to this user
    #return them all
    record = db.events(request.args(0)) or None

    form = SQLFORM(db.events, record, deleteable=True, fields=['start_time', 'end_time', 'description', 'name'])
    form.vars.user_id = auth.user.id
    if form.process().accepted:
        if record:
            redirect('../../default/index')
        redirect('../default/index')
    return dict(form=form)

@auth.requires_login()
def myschedule():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # get all events for this user
    events = db(db.events.user_id == auth.user.id).select();
    weekdays   = ['Sunday', 
              'Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday']
    return dict(date=date, events=events, weekdays=weekdays)

@auth.requires_login()
def groupschedule():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # what group is this?
    group_id = int(request.args[0]);
    #get this groups gaps
    gaps = db(db.gaps.group_id == group_id).select();
    # get user_ids for all people in this group
    users = db(group_id == db.user_groups.group_id).select(db.user_groups.user_id)
    # add each users events to the events list
    list_of_events = [];
    for user in users:
        one_users_events = db(db.events.user_id == user.user_id).select()
        list_of_events.append(one_users_events);
    weekdays   = ['Sunday', 
              'Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday']
    return dict(date=date, weekdays=weekdays, gaps=gaps, users=users, list_of_events=list_of_events)
