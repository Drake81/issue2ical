#!/usr/bin/env python
#
# gitlab to ical generator
import os
from icalendar import Calendar, Event
from icalendar import vCalAddress, vText
import pytz
from datetime import datetime
from datetime import date
from settings import CALENDAR_PATH, CALENDAR_FQDN

import gitlab
from settings import GITLAB_PERSONAL_ACCESS_TOKEN, GITLAB_URL, SSL_VERFIY, GITLAB_REPOS


def create_milestone(milestone, author, projectname):
    print("\tAdding Milestone ID {} with title: {}".format(milestone.id, milestone.title))
    ##We need at least one subcomponent for a calendar to be compliant:
    event = Event()

    # Parse Date
    dyear, dmonth, dday = milestone.due_date.split('-')

    event.add('summary', milestone.title)

    description = "{}\n\n---> {} <---\n".format(milestone.description, projectname)
    event.add('description', description)

    event.add('categories', "Milestone")

    ## We need the real eventday here
    event.add('dtstart', date(int(dyear), int(dmonth), int(dday)))
    # event.add('dtend', datetime(2016,7,12,12,0,0,tzinfo=pytz.utc))
    event.add('dtstamp', datetime.utcnow())

    ##A property with parameters. Notice that they are an attribute on the value:
    organizer = vCalAddress('{}@{}'.format(author.username, CALENDAR_FQDN))

    ##Automatic encoding is not yet implemented for parameter values, so you must use the ‘v*’ types you can import from the icalendar package (they’re defined in icalendar.prop):
    organizer.params['cn'] = vText(author.name)
    organizer.params['role'] = vText('Author')
    event['organizer'] = organizer
    # event['location'] = vText('Koeln, Deutschland')
    event['uid'] = '{}/{}@{}'.format(milestone.created_at, author.username, CALENDAR_FQDN)
    event.add('priority', 2)
    return event


def create_issue(issue, projectname):
    print("\tAdding Issue ID {} with title: {}".format(issue.id, issue.title))
    ##We need at least one subcomponent for a calendar to be compliant:
    event = Event()

    #Parse Date from issue due date
    #dyear, dmonth, dday = issue.milestone.due_date.split('-')

    event.add('summary', issue.title)

    description = "{}\n\n---> {} <---\n".format(issue.description, projectname)
    # Adding labels
    l = "Labels: "
    for label in issue.labels:
         l = l + " " + label
    description = description + l
    # Adding related Milestone
    if issue.milestone:
        description = description + "\nMilestone: " + issue.milestone.title
    event.add('description', description)

    event.add('categories', "Issue")

    ## We need the real eventday herre
    event.add('dtstart', date.today())
    #event.add('dtstart', date(int(dyear), int(dmonth), int(dday)))
    #event.add('dtend', datetime(2016,7,12,12,0,0,tzinfo=pytz.utc))
    event.add('dtstamp', datetime.utcnow())

    ##A property with parameters. Notice that they are an attribute on the value:
    organizer = vCalAddress('{}@{}'.format(issue.author.username, CALENDAR_FQDN))

    ##Automatic encoding is not yet implemented for parameter values, so you must use the ‘v*’ types you can import from the icalendar package (they’re defined in icalendar.prop):
    organizer.params['cn'] = vText(issue.author.name)
    organizer.params['role'] = vText('Author')
    event['organizer'] = organizer
    # event['location'] = vText('Koeln, Deutschland')
    event['uid'] = '{}/{}@{}'.format(issue.created_at, issue.author.username, CALENDAR_FQDN)
    event.add('priority', 5)

    # attendee = vCalAddress('MAILTO:maxm@example.com')
    # attendee.params['cn'] = vText('Max Rasmussen')
    # attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    # event.add('attendee', attendee, encode=0)
    return event




# personal access token authentication
gl = gitlab.Gitlab(GITLAB_URL, GITLAB_PERSONAL_ACCESS_TOKEN,ssl_verify=SSL_VERFIY)

# make an API request to create the gl.user object.
gl.auth()

cal = Calendar()
##Some properties are required to be compliant
cal.add('prodid', '-//Gitlab Issue Calendar//{}//'.format(CALENDAR_FQDN))
cal.add('version', '2.0')

projects = gl.projects.list(all=True)
for project in projects:
    if project.name in GITLAB_REPOS and project.open_issues_count > 0:
        print("ID:{:3} - {} - (Issues:{})".format(project.id, project.name, project.open_issues_count))

        # We need the due_date in the issue now
        #for issue in project.issues.list(all=True):
        #    if issue.state == 'opened' or issue.state == 'reopened':
        #        event = create_issue(issue, project.name)
        #        #Add the event to the calendar
        #        cal.add_component(event)

        for milestone in project.milestones.list(all=True):
            if milestone.state == 'active':
                event = create_milestone(milestone, project.owner, project.name)
                # Add the event to the calendar
                cal.add_component(event)


#Write to disk:
f = open(os.path.join(CALENDAR_PATH, 'gitlab-issues.ics'), 'wb')
f.write(cal.to_ical())
f.close()