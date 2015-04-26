#!/usr/bin/python
# -*- encoding: utf8 -*-

from collections import defaultdict
import datetime
import json
import sqlite3

from pprint import pprint
import sys

#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------
def imessage_date(date_int):
    """The iMessage database stores dates as an integer, which counts the
    number of seconds since 1 Jan 2001. This function converts this number
    to a datetime object.
    """
    start = datetime.datetime(2001, 1, 1)
    diff = datetime.timedelta(seconds=int(date_int))
    return start + diff

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
# Get a list of handles and their human-readable ids.
#------------------------------------------------------------------------------
# We store them as a dict, indexed by their ROWID in the 'handle' table.
# Although this isn't particularly memory efficient, it saves us making a
# database query every time we encounter a handle_id.
handles = dict()

for row in cursor.execute("""SELECT ROWID, id FROM handle"""):
    handles[row["ROWID"]] = row["id"]

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
# Get the messages associated with each thread.
#------------------------------------------------------------------------------
def get_message(message_id, cursor=cursor):
    """This takes a ROWID for the 'message' table, looks up the row and returns
    a dict with relevant information about the message.
    """
    query = cursor.execute("""SELECT ROWID, guid, text, handle_id, subject,
                                     type, date, is_from_me, item_type
                                FROM message
                               WHERE ROWID = ?""", (message_id,)).fetchone()
    data = dict(query)

    # TODO: find out what the item_type field means, and which values I
    # really can dismiss

    # If the item_type is 2, then it's a rename of a group chat so we can
    # throw it away
    if data["item_type"] == 2:
        return {}

    # If the item type is 5, then it's an audio message. I don't have a way to
    # extract audio messages yet, so just drop a placeholder string in the
    # text field.
    # TODO: How can I get the contents of audio messages?
    if data["item_type"] == 5:
        data["text"] = "«AUDIO MESSAGE»"

    # Update the date to a more human-readable format
    data["date"] = str(imessage_date(data["date"]))

    # If no subject is specified in the message, then just delete this field
    if data["subject"] is None:
        del data["subject"]

    # If we know the message is from me, set the "Sender" field to "Me".
    # Otherwise, replace it with the handle of the sender.
    if data["is_from_me"]:
        data["sender"] = "Me"
    else:
        data["sender"] = handles[data.pop("handle_id")]

    del data["ROWID"]

    return data

for thread_id, chats in threads.iteritems():
    message_ids = set()

    for chat_id in chats:
        query = cursor.execute("""SELECT message_id
                                    FROM chat_message_join
                                   WHERE chat_id = ?""", (chat_id,)).fetchall()
        message_ids.update([q["message_id"] for q in query])

    messages = list()

    for mid in message_ids:
        messages.append(get_message(mid))

    with open("handles/%s.json" % thread_id, 'w') as f:
        json.dump(messages, f, indent=2)

    # print len(message_ids)

    # message_ids = set()
    #
    # for chat_id in chats:
    #     for message in cursor.execute("""SELECT message_id
    #                                        FROM chat_message_join
    #                                       WHERE chat_id = ?""", (chat_id,)):
    #         message_ids.add(message["message_id"])
    #
    # messages = [get_message(id) for id in message_ids]









#------------------------------------------------------------------------------
# Functions for turning chunks of the Messages database into a more human-
# readable format
#------------------------------------------------------------------------------
# def get_handle(handle_id, cursor=cursor):
#     query = cursor.execute("""SELECT id
#                                 FROM handle
#                                WHERE ROWID = ?""", (handle_id,)).fetchone()
#
#     return query["id"]
#

#
#
#
#
#
# #------------------------------------------------------------------------------
# # For each thread, get a list of associated handles.
# #------------------------------------------------------------------------------
# for chats in threads.itervalues():
#     handle_ids = set()
#
#     for chat_id in chats:
#         for handle in cursor.execute("""SELECT handle_id
#                                           FROM chat_handle_join
#                                          WHERE chat_id = ?""", (chat_id,)):
#             handle_ids.add(handle["handle_id"])
#
#     handles = [get_handle(id) for id in handle_ids]
#
#     pprint(handles)
#
# #------------------------------------------------------------------------------
# # For each thread, get a list of associated messages.
# #------------------------------------------------------------------------------
# for chats in threads.itervalues():
#     message_ids = set()
#
#     for chat_id in chats:
#         for message in cursor.execute("""SELECT message_id
#                                            FROM chat_message_join
#                                           WHERE chat_id = ?""", (chat_id,)):
#             message_ids.add(message["message_id"])
#
#     messages = [get_message(id) for id in message_ids]
