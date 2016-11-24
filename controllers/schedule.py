# -*- coding: utf-8 -*-
# try something like
import datetime
from gluon import DAL, Field
from collections import namedtuple
from datetime import timedelta


def index():
    return dict(message="hello from schedule.py")


@auth.requires_login()
def add():
    # if present, grab event id from URL
    record = db.events(request.args(0)) or None

    # Create a form to add an event to the database
    form = SQLFORM(db.events, record, deleteable=True,
                   fields=['start_time', 'end_time', 'description', 'name'],
                   showid=False)

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
                db.events.insert(user_id = auth.user.id,
                                 start_time = starts_at_midnight,
                                 end_time = end_time,
                                 description=form.vars.description,
                                 name=form.vars.description)
                start_time = start_time + datetime.timedelta(days=1)
            else:
                starts_at_midnight = start_time.replace(hour=0, minute=0,second=0)
                midnight_tomorrow = (start_time + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0)
                db.events.insert(user_id = auth.user.id,
                                 start_time = starts_at_midnight,
                                 end_time = midnight_tomorrow,
                                 description=form.vars.description,
                                 name=form.vars.description)
                start_time = start_time + datetime.timedelta(days=1)

        if record:
            redirect('../../default/index')
        redirect('../default/index')

    return dict(form=form)

@auth.requires_login()
def my_schedule():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # get all events for this user
    events = db(db.events.user_id == auth.user.id).select();

    weekdays = ['Monday',
              'Tuesday',
              'Wednesday',
              'Thursday',
              'Friday',
              'Saturday',
              'Sunday']

    return dict(date=date, events=events, weekdays=weekdays)

@auth.requires_login()
def group_schedule():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # what group is this?
    group_id = int(request.args[0])
    #get this groups gaps
    group = db(db.groups.id == group_id).select()[0]

    gaps_db = db(db.gaps.group_id == group_id).select()

    #Remove gaps tha are shorter than the minimum gap length
    min_length = timedelta(minutes = group.gap_length)
    #print min_length
    gaps = []
    for gap in gaps_db:
        #print "gap length is ", (gap.end_time - gap.start_time), "min is ", min_length
        if (gap.end_time - gap.start_time) >= min_length:
            #print "adding ", gap
            gaps.append(gap)
    #print "\n\n\n", gaps, "\n\n"

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

    weekdays = ['Monday',
              'Tuesday',
              'Wednesday',
              'Thursday',
              'Friday',
              'Saturday',
              'Sunday']

    #Create form for changing the minimum gap length
    record = db.groups(request.args[0])
    form = SQLFORM(db.groups,
                   record,
                   showid=False,
                   fields=['gap_length'],
                   labels={'gap_length':'Minimum gap length (minutes): '})
    form.process()

    return dict(date=date, weekdays=weekdays, gaps=gaps,
        users=users, list_of_events=list_of_events,
        list_of_usernames=list_of_usernames, group=group,
        form=form, group_id=group_id)


def week():
    # get todays date so we know where the calendar should start
    date = datetime.date.today()
    # what group is this?
    group_id = int(request.args[0])
    #should we fast-forward or rewind a week?
    fast_forward = int(request.args[1])
    date = date + datetime.timedelta(days=fast_forward)
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
    weekdays   = ['Monday',
              'Tuesday',
              'Wednesday',
              'Thursday',
              'Friday',
              'Saturday',
              'Sunday',]

    return dict(date=date, weekdays=weekdays, gaps=gaps,
        users=users, list_of_events=list_of_events,
        list_of_usernames=list_of_usernames, group=group,
         fast_forward=fast_forward, group_id=group_id)

@auth.requires_login()
def group_day():
    """ group_day()

    displays the gaps for the given group and the given day.

    INPUTS:
        args[0] [INTEGER]: group_id, will error if not int
        args[1] [STRING]: the given date **NOTE TO SELF, does not error properly if passed not an accruate date. oops

    """

    #retreive the required inputs, if they don't exists send 404
    try:
        group = int(request.args[0])
        date_string = request.args[1]
    except:
        redirect('../../404')

    #transfer the day into the appropriate format (datetime)
    month = int(date_string[0:2])
    day = int(date_string[2:4])
    year = int(date_string[4:])

    #find group name
    group_name = db(group == db.groups.id).select()[0].name

    #figure out the beginning and end times of the day
    start_date = datetime.datetime(year,month,day,0,0)
    end_date = datetime.datetime(year,month,day,23,59)

    #select all gaps that are on the given day
    temp_gaps = db.executesql("""
        SELECT gap.start_time, gap.end_time
        FROM gaps as gap
        WHERE gap.group_id = %d
        ORDER BY gap.start_time ASC
        """ %(group))

    #find only gaps from the given day.
    gaps = []
    for gap in temp_gaps:
        print gap
        if gap[0] >= start_date and gap[0] <= end_date:
            gaps.append(gap)
            print str(gap)

    #determine yesterday and the next day
    prev_date = (start_date - datetime.timedelta(days=1)).date().strftime('%m%d%Y')
    next_date = (end_date + datetime.timedelta(minutes=1)).date().strftime('%m%d%Y')

    #TESTING

    #return
    return dict(gaps = gaps, group = group, group_name = group_name,
        date = date_string, prev_date = prev_date, next_date = next_date)


@auth.requires_login()
def user_day():
    """
    user_day()


    INPUTS:
        args[0] (INTEGER): user_id of the user in question
    """
    try:
        user = int(request.args[0])
        date_string = request.args[1]
    except:
        redirect('../../404')

    #transfer the day into the appropriate format (datetime)
    month = int(date_string[0:2])
    day = int(date_string[2:4])
    year = int(date_string[4:])

    #figure out the beginning and end times of the day
    start_date = datetime.datetime(year,month,day,0,0)
    end_date = datetime.datetime(year,month,day,23,59)

    #determine yesterday and the next day
    prev_date = (start_date - datetime.timedelta(days=1)).date().strftime('%m%d%Y')
    next_date = (end_date + datetime.timedelta(minutes=1)).date().strftime('%m%d%Y')

    #pull all the users events
    temp_events = db.executesql("""
        SELECT event.start_time as start_time, event.end_time as end_time, event.id as id, event.name as name
        FROM events as event
        WHERE event.user_id = %d
        ORDER by start_time ASC
        """ %(user))

    #loop through to determine what events are on the given day
    events = []
    previous_event_end_time = start_date
    previous_event_index = 0
    events_index = 0
    for event in temp_events:
        #if the events start time falls in the correct window, we will insert it on today
        if event[0] >= start_date and event[0] <= end_date:

            #create a new list object with the start_time, end_time, and event_id
            insert_event = [event[0],event[1],event[2]]

             #if there is a name append it to this list, if not append a blank name
            if event[3]:
                insert_event.append(event[3])
            else:
                insert_event.append("")


            #keep an index of how far in the event is incremented
            if event[0]<=previous_event_end_time:
                print "overlap"
                print previous_event_index
                previous_event_index+=1
                insert_event.append(previous_event_index)
                insert_event.append(0)

            #determine the total number of events and reset that value for all events in the overlap sequence
            elif previous_event_index!=0:
                print 'changing event totals %d' %previous_event_index
                for i in range(0,previous_event_index):
                    print i
                    events[len(events)-i][5] = previous_event_index+1
                insert_event.append(0)
                insert_event.append(0)
                previous_event_index = 0

            #if previous event indec was 0 and still should be zero, just append zeros.
            else:
                insert_event.append(0)
                insert_event.append(0)

            #set the previous_end_time to compare too
            previous_event_end_time = event[1]

            #append the new event to the events list
            events.append(insert_event)

        elif event[0] >= end_date:
            #since sorted in ascending order we can move on now
            break

    #do one last check for checking the total number of overlap
    if previous_event_index!=0:
        print 'changing event totals %d' %previous_event_index
        print 'length %d' %len(events)
        for i in range(1,previous_event_index+2):
            print i
            print events[len(events)-i][5]
            events[len(events)-i][5] = previous_event_index+1

    #return
    return dict(user=user, date = date_string,
        events= events, prev_date=prev_date, next_date=next_date)