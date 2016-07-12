#!/usr/bin/env python
#
# Copyright (C) 2016 Martin Stoffers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
# veröffentlichten Version, weiterverbreiten und/oder modifizieren.

# Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
# OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License für weitere Details.
#
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.


import os

from icalendar import Calendar, Event
from icalendar import vCalAddress, vText
from datetime import datetime
from datetime import date
from settings import CALENDAR_PATH, CALENDAR_FQDN

import gitlab
from settings import GITLAB_PERSONAL_ACCESS_TOKEN, GITLAB_URL, SSL_VERFIY, GITLAB_REPOS


def create_milestone(milestone, author, projectname):
    print("\tAdding Milestone ID {} with title: {}".format(milestone.id, milestone.title))
    event = Event()

    # Parse due date
    dyear, dmonth, dday = milestone.due_date.split('-')

    event['uid'] = '{}/{}@{}'.format(milestone.created_at, author.username, CALENDAR_FQDN)

    event.add('summary', milestone.title)
    description = "{}\n\n---> {} <---\n".format(milestone.description, projectname)
    event.add('description', description)


    event.add('dtstart', date(int(dyear), int(dmonth), int(dday)))
    # event.add('dtend', datetime(2016,7,12,12,0,0,tzinfo=pytz.utc))
    event.add('dtstamp', datetime.utcnow())

    # event['location'] = vText('Koeln, Deutschland')
    event.add('categories', "Milestone")
    event.add('priority', 2)

    organizer = vCalAddress('{}@{}'.format(author.username, CALENDAR_FQDN))
    organizer.params['cn'] = vText(author.name)
    organizer.params['role'] = vText('Author')
    event['organizer'] = organizer
    return event


def create_issue(issue, projectname):
    print("\tAdding Issue ID {} with title: {}".format(issue.id, issue.title))
    event = Event()

    #Parse due date
    dyear, dmonth, dday = issue.due_date.split('-')

    event['uid'] = '{}/{}@{}'.format(issue.created_at, issue.author.username, CALENDAR_FQDN)

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

    event.add('dtstart', date(int(dyear), int(dmonth), int(dday)))
    #event.add('dtend', datetime(2016,7,12,12,0,0,tzinfo=pytz.utc))
    event.add('dtstamp', datetime.utcnow())

    # event['location'] = vText('Koeln, Deutschland')
    event.add('categories', "Issue")
    event.add('priority', 5)

    organizer = vCalAddress('{}@{}'.format(issue.author.username, CALENDAR_FQDN))
    organizer.params['cn'] = vText(issue.author.name)
    organizer.params['role'] = vText('Author')
    event['organizer'] = organizer

    # attendee = vCalAddress('MAILTO:fooo@example.com')
    # attendee.params['cn'] = vText('foo Bar')
    # attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    # event.add('attendee', attendee, encode=0)
    return event


def create_Calendar():
    cal = Calendar()
    ##Some properties are required to be compliant
    cal.add('prodid', '-//Gitlab Issue Calendar//{}//'.format(CALENDAR_FQDN))
    cal.add('version', '2.0')
    return cal


def write_Calendar(cal):
    # Write to disk:
    with open(os.path.join(CALENDAR_PATH, 'calendar.ics'), 'wb') as f:
        f.write(cal.to_ical())


def create_events_from_project(project, cal):
    if project.name in GITLAB_REPOS and project.open_issues_count > 0:
        print("ID:{:3} - {} - (Issues:{})".format(project.id, project.name, project.open_issues_count))

        # We need the due_date in the issue now
        for issue in project.issues.list(all=True):
            if (issue.state == 'opened' or issue.state == 'reopened') and issue.due_date is not None:
                event = create_issue(issue, project.name)
                # Add the event to the calendar
                cal.add_component(event)

        for milestone in project.milestones.list(all=True):
            if milestone.state == 'active':
                event = create_milestone(milestone, project.owner, project.name)
                # Add the event to the calendar
                cal.add_component(event)


if __name__ == "__main__":
    # personal access token authentication
    gl = gitlab.Gitlab(GITLAB_URL, GITLAB_PERSONAL_ACCESS_TOKEN, ssl_verify=SSL_VERFIY)
    gl.auth()
    cal = create_Calendar()

    for project in gl.projects.list(all=True):
        create_events_from_project(project, cal)
