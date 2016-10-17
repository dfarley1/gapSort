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
    form = SQLFORM(db.events, fields=['start_time', 'end_time', 'description', 'name'])
    form.vars.user_id = auth.user.id
    if form.process().accepted:
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
    # get all events for this user
    events = db(db.events.user_id == auth.user.id).select();
    gaps = db(db.gaps.group_id == 1).select();
    weekdays   = ['Sunday', 
              'Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday']
    return dict(date=date, events=events, weekdays=weekdays, gaps=gaps)

    
def findGaps():
    print "\n\n\n\n\n"

    #TODO: edit start/end times
    start_time = datetime.datetime(2016,10,13,12,00,00)
    end_time = datetime.datetime(2016,10,13,12,30,00)
    user_id = auth.user_id
    
    #get current user's usergroups
    #userGroups = db.user_groups
    #userGroup_id = userGroups.user_id
    #q = userGroup_id == auth.user_id
    #s = db(q)
    s = db(db.user_groups.user_id == auth.user_id)
    rows = s.select()
    for row in rows:
        print row.user_id, row.group_id
    group = rows[0].group_id
    print group
    
    #print events from group
    events = db(db.events.group_id == group).select()
    for event in events:
        if (event.start_time >= start_time) and (event.end_time <= end_time):
            print event.start_time, "\n", event.end_time, "\n\n\n"
    
    
    #main loop
    print "\n\nGaps:"
    time_iter = start_time
    gaps = []
    Gaptype = namedtuple('datetime', ['start', 'end'])
    while time_iter <= end_time:
        #build new gap starting at time_iter
        gap = Gaptype(start=time_iter, end=time_iter)
        
        #find the nearest start point of an event
        nearest_start = end_time
        for event in events:
            if (event.start_time > nearest_start):
                nearest_start = event.start_time
            
        #assign as end of a gap
        gap.end = nearest_start
        print gap.start, "\n", gap.end
    
        #move iter up to that start point
        time_iter = nearest_start
        
        #find... what?  not just nearest end point
        
    
    
    
    
    
    return dict(start_time=start_time, end_time=end_time)
