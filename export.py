#!/usr/bin/python

from collections import defaultdict, namedtuple
import sqlite3

from pprint import pprint

#------------------------------------------------------------------------------
# Set up the Connection object
#------------------------------------------------------------------------------
conn = sqlite3.connect("chat.db")

# When we execute a SQL query, the rows are returned as tuples. Setting our
# row_factory to the sqlite3.Row class means we can access fields in these
# tuples by name as well as index, which is much more convenient. See:
# https://docs.python.org/2/library/sqlite3.html#sqlite3.Connection.row_factory
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

#------------------------------------------------------------------------------
# Functions for turning chunks of the Messages database into a more human-
# readable format
#------------------------------------------------------------------------------
def get_handle(handle_id, cursor=cursor):
    query = cursor.execute("""SELECT id
                                FROM handle
                               WHERE ROWID = ?""", (handle_id,)).fetchall()

    return query[0]["id"]

def get_message(message_id, cursor=cursor):
    message = cursor.execute("""SELECT ROWID, guid, text, handle_id, subject,
                                       date, is_from_me
                                  FROM message
                                 WHERE ROWID = ?""", (message_id,))
    return str(message.next())

#------------------------------------------------------------------------------
# Sort out the threads.
#------------------------------------------------------------------------------
# The database may contain two chats for each thread: one for SMS messages and
# one for iMessages. Both chats will have the same 'chat_identifier' value, so
# use this to tie the chats together.
#
# The threads dict is indexed by 'chat_identifier', and the values are dicts of
# ROWID/guid of the chats.
threads = defaultdict(dict)

for row in cursor.execute("SELECT ROWID, guid, chat_identifier FROM chat"):
    threads[row['chat_identifier']][row['ROWID']] = row['guid']

#------------------------------------------------------------------------------
# For each thread, get a list of associated handles.
#------------------------------------------------------------------------------
for chats in threads.itervalues():
    handle_ids = set()
    handles2 = []

    for chat_id in chats:
        for handle in cursor.execute("""SELECT handle_id
                                          FROM chat_handle_join
                                         WHERE chat_id = ?""", (chat_id,)):
            handle_ids.add(handle["handle_id"])

    handles = [get_handle(id) for id in handle_ids]

#------------------------------------------------------------------------------
# For each thread, get a list of associated messages.
#------------------------------------------------------------------------------
for chats in threads.itervalues():
    message_ids = set()

    for chat_id in chats:
        for message in cursor.execute("""SELECT message_id
                                           FROM chat_message_join
                                          WHERE chat_id = ?""", (chat_id,)):
            message_ids.add(message["message_id"])

    messages = [get_message(id) for id in message_ids]
