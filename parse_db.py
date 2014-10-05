#!/usr/bin/env python

import sqlite3
conn = sqlite3.connect('sms.db')

def get_sql_table(conn, table):
    return conn.execute('SELECT * from %s' % table)

# Construct a dictionary of addresses. Here an "address" is a phone number or
# email address, used to identify different recipients.

addresses = dict()
for row in get_sql_table(conn, 'handle'):
    addresses[row[0]] = dict({
        "address": row[1],
        "country": row[2],
        "service": row[3]
    })

# Construct a dictionary of threads. Here each "thread" corresponds to an
# entry in the 'chat' table, a distinct message thread. Each thread has two
# attributes: participants and messages.

threads = dict()
for row in get_sql_table(conn, 'chat'):
    threads[row[0]] = dict({
        "addresses": set(),
        "messages": set()
    })

# Use the 'chat_handle_join' table to populate the participants field of each
# thread

for row in get_sql_table(conn, 'chat_handle_join'):
    chat_id   = row[0]
    handle_id = row[1]
    threads[chat_id]["addresses"].add(handle_id)

# Use the 'chat_message_join' table to populate the messages field

for row in get_sql_table(conn, 'chat_message_join'):
    chat_id = row[0]
    msg_id  = row[1]
    threads[chat_id]["messages"].add(msg_id)
    
print threads