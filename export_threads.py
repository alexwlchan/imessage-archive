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
# Sort out the chats.
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

pprint(dict(threads))