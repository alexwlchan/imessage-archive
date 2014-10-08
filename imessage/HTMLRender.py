#!/usr/bin/env python

import datetime
from dates import imessage_date_obj, duration, html_string

SECONDS_TO_WAIT = 300

def process_message(prev, current, next):
    """Returns a message with some extra attributes."""
    if current == {}: return {}
    
    # Determine whether to show the date
    # The date is shown above a message if the time between it and the previous
    # message is more than SECONDS_TO_WAIT
    if prev is not None:
        delay = (duration(current["date"], prev["date"]) > SECONDS_TO_WAIT)
        current["show_date"] = delay
        current["html_date"] = html_string(current["date"])
    else:
        current["show_date"] = True
        current["html_date"] = html_string(current["date"])
    
    # Determine whether to show a "Conversation with X" marker (for conversations with mixed formats)
    if prev is not None:
        if current["handle"] != prev["handle"]:
            current["show_handle"] = True
            current["html_handle"] = ''.join([
                '<div class="handle_str">',
                'Conversation with ',
                '<span class="handle">{0}</span>'.format(current["handle"]),
                '</div>'
            ])
        else:
            current["show_handle"] = False
    
    return current

def handle_str(handles):
    if len(handles) == 1:
        return handles[0]
    else:
        return ', '.join(handles[:-1]) + ' and ' + handles[-1]