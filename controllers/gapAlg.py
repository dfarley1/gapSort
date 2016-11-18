#gapAlg
#gap finding algorithm

import datetime
from gluon import DAL, Field
from collections import namedtuple

#indexes in the tuples of the start time and the end time
START_TIME = 0
END_TIME = 1

def gaps():
    """gaps()

    Removes the elements in db.gaps associated with group HARD_CODED
    Finds gaps in the users events and then places them in db.gaps
    With the correct group_id

    **NOTES**: currently does not have a view to see them on the webpage,
    also currently the group is hard-coded to group_id=1 and finding gaps in
    date range 10-5-16 -> 10-19-15. Will want to change this to prompt user
    for what information they want"""


    #clear the gaps in the group id
    print 'begin'
    try:
        #try to get the group id from the url
        group = int(request.args(0))
    except:
        #if not valid url, throw 404 error, this page does not exist
        print 'invalid'
        redirect('/gapSort/404')

    db(db.gaps.group_id == group).delete()
    
    #retrieve all events associated with users that are in the group
    events = db.executesql("""SELECT event.start_time as start_time, event.end_time as end_time
        FROM events as event 
        WHERE
            event.user_id IN (SELECT user_id FROM user_groups WHERE group_id=%d)
        ORDER BY event.end_time DESC
        """ %group)

    #create a list to store all temporary gaps in
    temp_gaps = []

    #hard_coded start and end date

    #SETTING UP GAPS AS SINGLE DAYS INSTEAD OF ONE WHOLE BLOCK
    now = datetime.datetime.now()
    gap_start = now.replace(hour=0, minute=0, second=0)
    #loop through 14 days
    for delta in range (0,14):
        gap_end = gap_start + datetime.timedelta(days=1)
        #add the gap to temp_gaps
        temp_gaps.append([gap_start,gap_end])
        #resett the start gap time
        gap_start = gap_end

    for gap in temp_gaps:
        print "%s %s" %(str(gap[START_TIME]),str(gap[END_TIME]))

    #if there are no events, all is well, move on
    if not events:
        for gap in temp_gaps:
            db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)
        redirect('../../schedule/groupschedule/%d' %group)

    event = events.pop(0)
    gap = temp_gaps.pop(0)
    

    #loop through until all events are accounted for
    while True:
        print "(%s,%s) (%s,%s)" %(str(gap[START_TIME]),str(gap[END_TIME]),str(event[START_TIME]),str(event[END_TIME]))
        #if the gap starts after the event
        if gap[START_TIME] > event[END_TIME]:
            print 'gap after event'
            if events:
                event = events.pop(0)
                continue
            break

        #if the gap ends before the event
        if gap[END_TIME] < event[START_TIME]:
            #insert the gap into the database!!
            print 'gap before event'
            db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)
            if temp_gaps:
                gap = temp_gaps.pop(0)
                print gap
                continue
            break

        #if they overlap
        else:
            #if the event falls within the gap
            if (gap[START_TIME] < event[START_TIME]) and (gap[END_TIME] > event[END_TIME]):
                #create two new gaps
                print 'event in the middle'
                gap1 = (gap[START_TIME],event[START_TIME])
                gap2 = (event[END_TIME],gap[END_TIME])

                #insert the second gap onto stack
                temp_gaps.insert(0,gap2)

                #loop back on the first event
                gap = gap1

                if events:
                    event = events.pop(0)
                    continue
                break

            #if the event begins  after the gap and end before the gap does
            if gap[START_TIME] < event[START_TIME]:
                print 'event last'
                #reset the gap to the accurate gap
                gap = (gap[START_TIME],event[START_TIME])

                if events:
                    event = events.pop(0)
                    continue
                break

            #if the event begins after the gap begins and ends after the gap
            else:
                #reset the gap to the accurate gap
                print 'event last'
                gap = (event[END_TIME],gap[END_TIME])
                if events:
                    event = events.pop(0)
                    continue
                break

    #insert the gap we are looking at once done
    db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)

    #insert the rest of temp_gaps into the database.
    for gap in temp_gaps:
        db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)

    #set random message
    redirect('../../schedule/groupschedule/%d' %group)
