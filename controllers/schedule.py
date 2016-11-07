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

    form = SQLFORM(db.events, record, deleteable=True, fields=['start_time', 'end_time', 'description', 'name'],showid=False)
    
    form.vars.user_id = auth.user.id
    #does this event span multiple days?
    if form.process().accepted:
        start_time = form.vars.start_time + datetime.timedelta(days=1)
        end_time = form.vars.end_time
        escape = 0
        while start_time.date() <= end_time.date() or escape > 10:
            db.events.insert(user_id = auth.user.id, start_time = start_time, end_time = end_time, description=form.vars.description, name=form.vars.description)
            start_time = start_time + datetime.timedelta(days=1)
            escape += 1
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
    group_id = int(request.args[0])
    #get this groups gaps
    group = db(db.groups.id == group_id).select()[0]

    gaps = db(db.gaps.group_id == group_id).select()

    # get user_ids for all people in this group
    users = db(group_id == db.user_groups.group_id).select(db.user_groups.user_id)
    # maintain a list of all the usernames
    list_of_usernames = []
    # add each users events to the events list
    list_of_events = []
    #populate a 2d list of everybody's events and another list of just usernames
    for user in users:
        one_users_events = db(db.events.user_id == user.user_id).select()
        list_of_events.append(one_users_events)
        username = db(db.auth_user.id == user.user_id).select()
        list_of_usernames.append(username)
    # a list of week days could come in handy
    weekdays   = ['Sunday',
              'Monday',
              'Tuesday',
              'Wednesday',
              'Thursday',
              'Friday',
              'Saturday']
    return dict(date=date, weekdays=weekdays, gaps=gaps, users=users, list_of_events=list_of_events, list_of_usernames=list_of_usernames, group=group)
