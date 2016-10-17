#gapAlg
#gap finding algorithm

import datetime
from gluon import DAL, Field
from collections import namedtuple

GROUP = 1

@auth.requires_login()
def gaps():
	"""main gap finding alg"""

	#clear the gaps in the group id
	db(db.gaps.group_id == GROUP).delete()
	
	#retrieve all events associated with users that are in the group
	events = db.executesql("""SELECT event.start_time as start_time, event.end_time as end_time
		FROM events as event 
		WHERE
			event.user_id IN (SELECT user_id FROM user_groups WHERE group_id=%d)
		ORDER BY event.end_time
		""" %GROUP)

	if not events:
		return dict(message='no events')

	#create a list to store all temporary gaps in
	temp_gaps = []

	gap_start = datetime.datetime(2016,10,05)
	gap_end = datetime.datetime(2016,10,19)

	temp_gaps.append((gap_start,gap_end))

	msg = events

	event = events.pop()
	gap = temp_gaps.pop()

	while True:
		#if the gap starts after the event
		if gap[0] > event[1]:
			if events:
				event = events.pop()
				continue
			break

		#if the gap ends before the event
		if gap[1] < event[0]:
			#insert the gap into the database!!
			db.gaps.insert(start_time=gap[0],end_time=gap[1],group_id=GROUP)
			if gaps:
				gap = gaps.pop()
				continue
			break

		#if they overlap
		else:
			#if the event falls within the gap
			if (gap[0] < event[1]) and (gap[1] >event[0]):
				#create two new gaps
				gap1 = (gap[0],event[0])
				gap2 = (gap[1],event[1])

				temp_gaps.insert(0,gap2)
				gap = gap1

				if events:
					event = events.pop()
					continue
				break

			if gap[0] < event[0]:
				gap[1] = event[0]
			else:
				gap[0] = event[1]

	#insert the rest of temp_gaps into the database.
	for gap in temp_gaps:
		db.gaps.insert(start_time=gap[0],end_time=gap[1],group_id=GROUP)

	#set random message
	return dict(message=msg)