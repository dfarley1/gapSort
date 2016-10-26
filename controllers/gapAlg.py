#gapAlg
#gap finding algorithm

import datetime
from gluon import DAL, Field
from collections import namedtuple

#group that is hard coded in
HARD_CODED = 1

#indexes in the tuples of start and end time
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

    if request.args(0):
        group = request.args(0)
    else:
        group = HARD_CODED

    db(db.gaps.group_id == group).delete()
    
    #retrieve all events associated with users that are in the group
    events = db.executesql("""SELECT event.start_time as start_time, event.end_time as end_time
        FROM events as event 
        WHERE
            event.user_id IN (SELECT user_id FROM user_groups WHERE group_id=%d)
        ORDER BY event.end_time DESC
        """ %group)

    if not events:
        return dict(message='no events')

    #create a list to store all temporary gaps in
    temp_gaps = []

    #hard_coded start and end date
    gap_start = datetime.datetime.now()
    gap_end = gap_start + datetime.timedelta(days=14)

    temp_gaps.append((gap_start,gap_end))

    event = events.pop()
    gap = temp_gaps.pop()

    #loop through until all events are accounted for
    while True:
        print "gap: %s,%s event: %s,%s" %(gap[START_TIME],gap[END_TIME],event[START_TIME],event[END_TIME])
        #if the gap starts after the event
        if gap[START_TIME] > event[END_TIME]:
            print 'gap after event'
            if events:
                event = events.pop()
                continue
            break

        #if the gap ends before the event
        if gap[END_TIME] < event[START_TIME]:
            print 'gap before event'
            #insert the gap into the database!!
            db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)
            if temp_gaps:
                gap = temp_gaps.pop()
                continue
            break

        #if they overlap
        else:
            print 'event in gap'
            #if the event falls within the gap
            if (gap[START_TIME] < event[END_TIME]) and (gap[END_TIME] > event[START_TIME]):
                #create two new gaps
                gap1 = (gap[START_TIME],event[START_TIME])
                gap2 = (event[END_TIME],gap[END_TIME])

                #insert the second gap onto stack
                temp_gaps.insert(0,gap2)

                #loop back on the first event
                gap = gap1

                if events:
                    event = events.pop()
                    continue
                break

            #if the event begins before the gap and end before the gap does
            if gap[START_TIME] < event[START_TIME]:
                print 'event first overlap'
                #reset the gap to the accurate gap
                gap = (gap[START_TIME],event[START_TIME])

                if events:
                    event = events.pop()
                    continue
                break

            #if the event begins after the gap begins and ends after the gap
            else:
                print 'gap first overlap'
                #reset the gap to the accurate gap
                gap = (event[END_TIME],gap[END_TIME])
                if events:
                    event = events.pop()
                    continue
                break

    #insert the gap we are looking at once done
    db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)

    #insert the rest of temp_gaps into the database.
    for gap in temp_gaps:
        db.gaps.insert(start_time=gap[START_TIME],end_time=gap[END_TIME],group_id=group)

    #set random message
    redirect('../schedule/groupschedule/%d' %group)
