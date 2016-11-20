# -*- coding: utf-8 -*-
# try something like
import datetime
from gluon import DAL, Field
from collections import namedtuple
from gluon.serializers import json
from datetime import timedelta


def index(): return dict(message="hello from schedule.py")

@auth.requires_login()
def add():
    # if present, grab event id from URL
    record = db.events(request.args(0)) or None

    # Create a form to add an event to the database
    form = SQLFORM(db.events, record, deleteable=True, fields=['start_time', 'end_time', 'description', 'name'],showid=False)

    #autofill the user_id since users won't know their own user id
    form.vars.user_id = auth.user.id

    #process the form once it is submitted
    if form.process().accepted:
        #take down the starting and ending times of this event
        #first day already got stored when the form was accepted so start one day later
        start_time = form.vars.start_time + datetime.timedelta(days=1)
        end_time = form.vars.end_time
        #does this event span multiple days?
        #num_days = (end_time - start_time).days()
        which_day = 1
        while start_time.date() <= end_time.date():
            #is this the last day?
            if start_time.date() == end_time.date():
                starts_at_midnight = start_time.replace(hour=0, minute=0,second=0)
                db.events.insert(user_id = auth.user.id, start_time = starts_at_midnight, end_time = end_time, description=form.vars.description, name=form.vars.description)
                start_time = start_time + datetime.timedelta(days=1)
            else:
                starts_at_midnight = start_time.replace(hour=0, minute=0,second=0)
                midnight_tomorrow = (start_time + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0)
                db.events.insert(user_id = auth.user.id, start_time = starts_at_midnight, end_time = midnight_tomorrow, description=form.vars.description, name=form.vars.description)
                start_time = start_time + datetime.timedelta(days=1)
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

    gaps_db = db(db.gaps.group_id == group_id).select()

    #Remove gaps tha are shorter than the minimum gap length
    min_length = timedelta(minutes = group.gap_length)
    print min_length
    gaps = []
    for gap in gaps_db:
        print "gap length is ", (gap.end_time - gap.start_time), "min is ", min_length
        if (gap.end_time - gap.start_time) >= min_length:
            print "adding ", gap
            gaps.append(gap)
    print "\n\n\n", gaps, "\n\n"

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

    #Create form for changing the minimum gap length
    record = db.groups(request.args[0])
    form = SQLFORM(db.groups, record, showid=False, fields=['gap_length'], labels={'gap_length':'Minimum gap length (minutes): '})
    form.process()

    return dict(date=date, weekdays=weekdays, json_weekdays=json(weekdays), gaps=gaps,
        users=users, list_of_events=list_of_events,
        list_of_usernames=list_of_usernames, group=group,
        form=form)

def day():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # what group is this?
    group_id = 1 #int(request.args[0])
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

    db.define_table('gap_length',
        Field('gap_length', requires=IS_IN_SET(
            ['15 minutes', '30 minutes', '1 hour', '2 hours', '4 hours'])))
    form = SQLFORM(db.gap_length)
    form.element('form')['_onsubmit']='$('#gapsModal').modal('show');'

    #if form.process(formname='test').accepted:
    #    response.flash = 'form accepted'
    #elif form.errors:
    #    response.flash = 'form has errors'
    #else:
    #    response.flash = 'please fill out the form'

    return dict(date=date, weekdays=weekdays, json_weekdays=json(weekdays), gaps=gaps,
        users=users, list_of_events=list_of_events,
        list_of_usernames=list_of_usernames, group=group,
        form=form)

<<<<<<< HEAD
def week():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # what group is this?
    group_id = 1 #int(request.args[0])
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

    db.define_table('gap_length',
        Field('gap_length', requires=IS_IN_SET(
            ['15 minutes', '30 minutes', '1 hour', '2 hours', '4 hours'])))
    form = SQLFORM(db.gap_length)
    form.element('form')['_onsubmit']='$('#gapsModal').modal('show');'

    #if form.process(formname='test').accepted:
    #    response.flash = 'form accepted'
    #elif form.errors:
    #    response.flash = 'form has errors'
    #else:
    #    response.flash = 'please fill out the form'

    return dict(date=date, weekdays=weekdays, gaps=gaps,
        users=users, list_of_events=list_of_events,
        list_of_usernames=list_of_usernames, group=group)
=======
@auth.requires_login()
def groupday():

    #retreive the required inputs, if they don't exists send 404
    try:
        group = int(request.args[0])
        date_string = request.args[1]
    except:
        redirect('gapSort/404')

    #transfer the day into the appropriate format (datetime)
    month = int(date_string[0:2])
    day = int(date_string[2:4])
    year = int(date_string[4:])

    #figure out the beginning and end times of the day
    start_date = datetime.datetime(year,month,day,0,0)
    end_date = datetime.datetime(year,month,day,23,59)

    print str(start_date)

    #select all gaps that are on the given day
    temp_gaps = db.executesql("""
        SELECT gap.start_time, gap.end_time
        FROM gaps as gap
        WHERE gap.group_id = %s
        ORDER BY gap.start_time ASC
        """ %(group))

    #find only gaps from the given day.
    gaps = []
    for gap in temp_gaps:
        print gap
        if gap[0] >= start_date and gap[0] <= end_date:
            gaps.append(gap)
            print str(gap)

    #return
    return dict(gaps = gaps, group = group, date = date_string)
>>>>>>> e0e8470c731e370f977cbede582d49ae1717d209
