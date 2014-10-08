#!/usr/bin/env python

import datetime

DATE_FORMAT = "%Y-%m-%d %X"

def imessage_date_str(date_obj):
    """The 'date' fields count seconds from the first second of 1 Jan 2001, the
    first time which can be represented with NSDate. We turn this into a more
    human-friendly string.
    """
    startdate = datetime.datetime(2001, 01, 01, 00, 00, 00)
    enddate   = startdate + datetime.timedelta(seconds=date_obj)
    return enddate.strftime(DATE_FORMAT)

def imessage_date_obj(date_str):
    """Converts a string date into a datetime object."""
    return datetime.datetime.strptime(date_str, DATE_FORMAT)

def duration(date_str1, date_str2):
    diff = imessage_date_obj(date_str1) - imessage_date_obj(date_str2)
    return abs(diff.total_seconds())

def html_string(date_str):
    """Return a string suitable for printing in the rendered output."""
    date = imessage_date_obj(date_str)
    return ''.join([
        '<div class="msg_date_str">',
        '<span class="msg_day">{day}</span> '.format(day = ' '.join([
                      date.strftime("%a"),
                      str(int(date.strftime("%d"))),
                      date.strftime("%b %Y")
                  ])),
        '<span class="msg_time">{time}</span>'.format(time = date.strftime("%H:%M")),
        '</div>'
    ])