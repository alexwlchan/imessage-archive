#!/usr/bin/env python

import os
import json
import sqlite3
conn = sqlite3.connect('sms.db')

def get_sql_table(conn, table):
    return conn.execute('SELECT * from %s' % table)

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

# Construct a dictionary of addresses. Here an "address" is a phone number or
# email address, used to identify different recipients.
addresses = dict()
for row in get_sql_table(conn, 'handle'):
    addresses[row[0]] = dict({
        "address": row[1],
        "country": row[2],
        "service": row[3]
    })

# Construct a dictionary of messages.
messages = dict()
for row in get_sql_table(conn, 'message'):
    messages[row[0]] = dict({
        "text":        row[1],
        "address_id":  row[5],
        "subject":     row[6],
        "country":     row[7],
        "service":     row[11],
        "date":        row[15],
        "from_me":     bool(row[21]),
        "attachments": list()
    })

# Construct a dictionary of distinct message threads. Each thread has two
# attributes: participants and messages.
threads = dict()
for row in get_sql_table(conn, 'chat'):
    threads[row[0]] = dict({
        "address_ids": set(),
        "messages":    list()
    })

# Use the 'chat_handle_join' table to populate the participants field
for row in get_sql_table(conn, 'chat_handle_join'):
    chat_id    = row[0]
    address_id = row[1]
    threads[chat_id]["address_ids"].add(address_id)

# Use the 'chat_message_join' table to populate the messages field
for row in get_sql_table(conn, 'chat_message_join'):
    chat_id = row[0]
    msg_id  = row[1]
    threads[chat_id]["messages"].append(messages.pop(msg_id, {}))

# Export the threads to JSON files
if not os.path.isdir('threads'):
    os.mkdir('threads')
for t in threads:
    with open(os.path.join('threads', 'thread_%d.json' % t), 'w') as ff:
        ff.write(json.dumps(threads[t], default=set_default))